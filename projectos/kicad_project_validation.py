"""Projektweite KiCad-Validierung über Snapshot, Artefakte und Pinzuordnungen."""

from __future__ import annotations

from dataclasses import dataclass

from .identifiers import BusinessId
from .kicad_assets import KiCadAssetReference, KiCadAssetTargetType
from .kicad_connections import (
    DeviceTerminal,
    KiCadStandardConformance,
    TerminalPinAssignment,
    validate_required_terminal_assignments,
)
from .kicad_library_snapshot import (
    KiCadCompleteSnapshotBuilder,
    KiCadCompleteSnapshotResult,
    KiCadLocalFileSet,
)
from .kicad_library_tables import KiCadLibraryTable
from .kicad_library_validation import (
    KiCadLibraryValidationResult,
    KiCadLibraryValidator,
    KiCadTargetRequirements,
    KiCadValidationFinding,
    KiCadValidationSeverity,
)
from .kicad_native_snapshot import NativeKiCadSource


@dataclass(frozen=True, slots=True)
class KiCadProjectValidationTarget:
    target_type: KiCadAssetTargetType
    target_id: BusinessId
    assets: tuple[KiCadAssetReference, ...]
    terminals: tuple[DeviceTerminal, ...] = ()
    assignments: tuple[TerminalPinAssignment, ...] = ()
    requirements: KiCadTargetRequirements = KiCadTargetRequirements()


@dataclass(frozen=True, slots=True)
class KiCadProjectValidationResult:
    snapshot: KiCadCompleteSnapshotResult | None
    findings: tuple[KiCadValidationFinding, ...]
    target_count: int

    @property
    def valid(self) -> bool:
        return not any(item.severity is KiCadValidationSeverity.ERROR for item in self.findings)

    @property
    def exception_count(self) -> int:
        return sum(1 for item in self.findings if item.code == "INFO-KICAD-0001")


class KiCadProjectValidationPipeline:
    """Führt alle KiCad-Prüfungen eines Projekts deterministisch zusammen."""

    def validate(
        self,
        *,
        files: KiCadLocalFileSet,
        targets: tuple[KiCadProjectValidationTarget, ...],
        symbol_table: KiCadLibraryTable | None = None,
        footprint_table: KiCadLibraryTable | None = None,
        model_sources: tuple[NativeKiCadSource, ...] = (),
    ) -> KiCadProjectValidationResult:
        findings: list[KiCadValidationFinding] = []
        try:
            snapshot = KiCadCompleteSnapshotBuilder(files).build(
                symbol_table=symbol_table,
                footprint_table=footprint_table,
                model_sources=model_sources,
            )
        except ValueError as exc:
            code = str(exc).split(":", 1)[0]
            findings.append(KiCadValidationFinding(
                code,
                KiCadValidationSeverity.ERROR,
                str(exc),
            ))
            return KiCadProjectValidationResult(None, tuple(findings), len(targets))

        validator = KiCadLibraryValidator(snapshot.items)
        seen_targets: set[tuple[KiCadAssetTargetType, BusinessId]] = set()

        for target in targets:
            key = (target.target_type, target.target_id)
            if key in seen_targets:
                findings.append(KiCadValidationFinding(
                    "ERR-KICAD-0051",
                    KiCadValidationSeverity.ERROR,
                    f"KiCad-Validierungsziel ist doppelt vorhanden: {target.target_id}.",
                ))
                continue
            seen_targets.add(key)

            if any(asset.target_type is not target.target_type or asset.target_id != target.target_id for asset in target.assets):
                findings.append(KiCadValidationFinding(
                    "ERR-KICAD-0052",
                    KiCadValidationSeverity.ERROR,
                    f"Mindestens ein KiCad-Artefakt gehört nicht zum Ziel {target.target_id}.",
                ))
                continue
            if any(terminal.target_type is not target.target_type or terminal.target_id != target.target_id for terminal in target.terminals):
                findings.append(KiCadValidationFinding(
                    "ERR-KICAD-0053",
                    KiCadValidationSeverity.ERROR,
                    f"Mindestens ein Anschluss gehört nicht zum Ziel {target.target_id}.",
                ))
                continue

            result: KiCadLibraryValidationResult = validator.validate(
                assets=target.assets,
                assignments=target.assignments,
                requirements=target.requirements,
            )
            findings.extend(result.findings)

            symbol_assets = tuple(asset for asset in target.assets if asset.asset_type.value == "SYMBOL")
            for symbol in symbol_assets:
                missing = validate_required_terminal_assignments(
                    target.terminals,
                    target.assignments,
                    symbol,
                )
                for terminal_id in missing:
                    findings.append(KiCadValidationFinding(
                        "ERR-KICAD-0054",
                        KiCadValidationSeverity.ERROR,
                        f"Erforderlicher Anschluss ist keinem Symbolpin zugeordnet: {terminal_id}.",
                        symbol.asset_id,
                    ))

            for assignment in target.assignments:
                if assignment.conformance is KiCadStandardConformance.EXCEPTION:
                    findings.append(KiCadValidationFinding(
                        "INFO-KICAD-0001",
                        KiCadValidationSeverity.INFO,
                        f"Dokumentierte KiCad-Ausnahme: {assignment.exception_reason}",
                        assignment.symbol_asset_id,
                    ))

        ordered = tuple(sorted(
            findings,
            key=lambda item: (item.severity.value, item.code, str(item.asset_id or ""), item.message),
        ))
        return KiCadProjectValidationResult(snapshot, ordered, len(targets))
