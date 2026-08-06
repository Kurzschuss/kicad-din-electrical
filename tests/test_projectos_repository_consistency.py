"""Repositoryweite Schutzprüfungen gegen erneute AP- und Export-Doppelungen."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]


def _duplicates(values: list[str]) -> set[str]:
    return {value for value, count in Counter(values).items() if count > 1}


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


def test_error_codes_are_defined_by_only_one_runtime_module():
    owners: dict[str, set[str]] = {}
    pattern = re.compile(r"(?:ERR|WARN)-KICAD-\d{4}")
    for path in (ROOT / "projectos").glob("*.py"):
        for code in set(pattern.findall(path.read_text(encoding="utf-8"))):
            owners.setdefault(code, set()).add(path.name)
    duplicates = {code: sorted(paths) for code, paths in owners.items() if len(paths) > 1}
    assert not duplicates, f"Mehrfach definierte Fehlercodes: {duplicates}"
