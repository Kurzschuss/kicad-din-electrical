"""End-to-end KiCad manifest synchronization regressions for issue #4."""
from copy import deepcopy

from .din_editor_change_service import DinEditorChangeService
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService


def _components() -> list[dict]:
    return [
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "terminal_label": "+24V SPS",
            "can_edit_label": True,
            "terminal_function": "24V supply",
            "part_number": "PT-2,5",
            "symbol_library": "Connector_Generic:Conn_01x02",
            "footprint": "TerminalBlock:TerminalBlock_1x02",
            "rail": 1,
            "start_te": 1,
            "end_te": 1,
        },
        {
            "reference": "X6",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "0V SPS",
            "terminal_label": "0V SPS",
            "can_edit_label": True,
            "terminal_function": "0V return",
            "part_number": "PT-2,5",
            "symbol_library": "Connector_Generic:Conn_01x02",
            "footprint": "TerminalBlock:TerminalBlock_1x02",
            "rail": 1,
            "start_te": 2,
            "end_te": 2,
        },
        {
            "reference": "Q1",
            "component_type": "CIRCUIT_BREAKER",
            "value": "MCB 16A",
            "part_number": "MCB-1P-B16",
            "symbol_library": "Z_Electrical:MCB_1P",
            "footprint": None,
            "rail": 1,
            "start_te": 4,
            "end_te": 5,
        },
    ]


def _service(components: list[dict] | None = None) -> DinEditorSyncService:
    session = DinEditorSession(components=deepcopy(components or _components()))
    return DinEditorSyncService(DinEditorChangeService(session))


def _symbol(manifest: dict, reference: str) -> dict:
    return next(symbol for symbol in manifest["symbols"] if symbol["reference"] == reference)


def test_manifest_roundtrip_preserves_labels_metadata_and_order():
    service = _service()

    first = service.export_manifest()
    second = service.export_manifest()

    assert first == second
    assert first["format"] == "kicad-symbol-manifest"
    assert [symbol["reference"] for symbol in first["symbols"]] == ["Q1", "X5", "X6"]

    q1 = _symbol(first, "Q1")
    assert q1["value"] == "MCB 16A"
    assert q1["part_number"] == "MCB-1P-B16"
    assert q1["symbol_library"] == "Z_Electrical:MCB_1P"
    assert q1["rail"] == 1
    assert q1["start_te"] == 4
    assert q1["end_te"] == 5

    x5 = _symbol(first, "X5")
    assert x5["label"] == "+24V SPS"
    assert x5["user_editable_label"] is True
    assert x5["terminal_function"] == "24V supply"
    assert x5["part_number"] == "PT-2,5"
    assert x5["symbol_library"] == "Connector_Generic:Conn_01x02"
    assert x5["footprint"] == "TerminalBlock:TerminalBlock_1x02"
    assert x5["rail"] == 1
    assert x5["start_te"] == 1
    assert x5["end_te"] == 1


def test_import_edit_export_reimport_is_lossless_and_noop_is_stable():
    service = _service()
    edited_manifest = deepcopy(service.export_manifest())
    _symbol(edited_manifest, "X5")["label"] = "Versorgung 24V KiCad"

    service.import_manifest_labels(edited_manifest)
    assert service.session.components[0]["label"] == "Versorgung 24V KiCad"
    assert service.session.components[0]["terminal_label"] == "Versorgung 24V KiCad"
    assert service.change_service.can_undo()

    exported = service.export_manifest()
    assert _symbol(exported, "X5")["label"] == "Versorgung 24V KiCad"
    assert _symbol(exported, "Q1") == _symbol(edited_manifest, "Q1")

    reimported = _service()
    reimported.import_manifest_labels(exported)
    assert reimported.session.components[0]["label"] == "Versorgung 24V KiCad"
    assert reimported.export_manifest() == exported

    state_before_noop = deepcopy(reimported.session.state())
    history_before_noop = deepcopy(reimported.change_service.history.state())
    reimported.import_manifest_labels(exported)

    assert reimported.session.state() == state_before_noop
    assert reimported.change_service.history.state() == history_before_noop
    assert reimported.export_manifest() == exported


def test_duplicate_and_ambiguous_references_are_deterministic():
    service = _service()
    original_state = deepcopy(service.session.state())
    original_history = deepcopy(service.change_service.history.state())
    manifest = service.export_manifest()
    x5 = deepcopy(_symbol(manifest, "X5"))
    manifest["symbols"] = [
        symbol for symbol in manifest["symbols"] if symbol["reference"] != "X5"
    ] + [
        {**deepcopy(x5), "label": "24V A"},
        {**deepcopy(x5), "label": "24V B"},
    ]

    service.import_manifest_labels(manifest)
    assert service.session.state() == original_state
    assert service.change_service.history.state() == original_history

    duplicates = _service(
        [
            {
                "reference": "X5",
                "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                "label": "24V",
                "can_edit_label": True,
            },
            {
                "reference": "X5",
                "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                "label": "0V",
                "can_edit_label": True,
            },
        ]
    )
    first_report = duplicates.report()
    second_report = duplicates.report()

    assert first_report == second_report
    assert not first_report["valid"]
    assert first_report["conflicts"] == [
        {"reference": "X5", "labels": ["24V", "0V"]}
    ]
