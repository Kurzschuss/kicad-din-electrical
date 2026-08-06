"""Repositoryweite Schutzprüfungen gegen strukturelle Doppelungen."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
ERROR_CODE_PATTERN = re.compile(r"(?:ERR|WARN)-KICAD-\d{4}")


def _duplicates(values: list[str]) -> set[str]:
    return {value for value, count in Counter(values).items() if count > 1}


def _string_template(node: ast.AST) -> str | None:
    """Liefert eine stabile Textschablone für String- und f-String-Knoten."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return " ".join(node.value.split())
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append("{...}")
        return " ".join("".join(parts).split())
    return None


def test_ap_document_ids_are_unique():
    ids = []
    for path in (ROOT / "docs" / "projectos").glob("AP-*.md"):
        match = re.match(r"(AP-\d{4})-", path.name)
        assert match, f"Ungültiger AP-Dateiname: {path.name}"
        ids.append(match.group(1))
    assert not _duplicates(ids), f"Doppelte AP-Dokumente: {sorted(_duplicates(ids))}"


def test_completed_work_packages_have_no_duplicates():
    text = (ROOT / "docs" / "projectos" / "arbeitsstand.yaml").read_text(encoding="utf-8")
    completed_lines = re.findall(r"(?:work_packages|completed_work_packages): \[([^\]]*)\]", text)
    ids = re.findall(r"AP-\d{4}", "\n".join(completed_lines))
    assert not _duplicates(ids), f"Doppelte AP-Einträge im Arbeitsstand: {sorted(_duplicates(ids))}"


def test_package_exports_do_not_redefine_names():
    path = ROOT / "projectos" / "__init__.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            names.extend(alias.asname or alias.name for alias in node.names)
    assert not _duplicates(names), f"Doppelte Paketexporte: {sorted(_duplicates(names))}"


def test_error_codes_have_one_consistent_meaning():
    """Mehrfachnutzung ist nur bei identischer Meldungsbedeutung zulässig.

    Die eingefrorenen Kompatibilitätsmodule dürfen denselben öffentlichen
    Fehlervertrag wiederverwenden. Derselbe Code darf jedoch niemals mit
    unterschiedlichen Meldungstexten beziehungsweise Bedeutungen auftreten.
    """
    definitions: dict[str, dict[str, set[str]]] = {}
    for path in sorted((ROOT / "projectos").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            template = _string_template(node)
            if not template:
                continue
            for code in ERROR_CODE_PATTERN.findall(template):
                definitions.setdefault(code, {}).setdefault(template, set()).add(path.name)

    conflicts = {
        code: {message: sorted(paths) for message, paths in messages.items()}
        for code, messages in definitions.items()
        if len(messages) > 1
    }
    assert not conflicts, f"Widersprüchlich definierte Fehlercodes: {conflicts}"


def test_workflow_display_names_are_unique():
    workflow_dir = ROOT / ".github" / "workflows"
    names: dict[str, list[str]] = {}
    for path in sorted(workflow_dir.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"(?m)^name:\s*[\"']?([^\n\"']+)", text)
        assert match, f"Workflow ohne Namen: {path.relative_to(ROOT)}"
        name = match.group(1).strip()
        names.setdefault(name, []).append(path.name)
    duplicates = {name: paths for name, paths in names.items() if len(paths) > 1}
    assert not duplicates, f"Doppelte Workflow-Anzeigenamen: {duplicates}"


def test_legacy_and_primary_documentation_have_no_identical_files():
    primary = ROOT / "docs"
    legacy = ROOT / "documentation"
    if not legacy.exists():
        return

    primary_hashes: dict[str, list[str]] = {}
    for path in primary.rglob("*"):
        if path.is_file():
            digest = sha256(path.read_bytes()).hexdigest()
            primary_hashes.setdefault(digest, []).append(str(path.relative_to(ROOT)))

    duplicates: dict[str, dict[str, list[str]]] = {}
    for path in legacy.rglob("*"):
        if not path.is_file():
            continue
        digest = sha256(path.read_bytes()).hexdigest()
        if digest in primary_hashes:
            duplicates[digest[:12]] = {
                "docs": primary_hashes[digest],
                "documentation": [str(path.relative_to(ROOT))],
            }

    assert not duplicates, f"Bytegleiche Dokumentationsdubletten: {duplicates}"
