"""Planning metadata for rail-mounted distribution components."""

COMPONENTS = {
    "RCD_2P": {"width": 2, "category": "FI/RCD"},
    "RCD_4P": {"width": 4, "category": "FI/RCD"},
    "RCBO_1P_N": {"width": 2, "category": "FI/LS"},
    "MCB_1P": {"width": 1, "category": "MCB"},
    "MCB_2P": {"width": 2, "category": "MCB"},
    "MCB_3P": {"width": 3, "category": "MCB"},
    "MCB_4P": {"width": 4, "category": "MCB"},
    "Fuse_1P": {"width": 1, "category": "Sicherung"},
    "Fuse_2P": {"width": 2, "category": "Sicherung"},
    "Fuse_3P": {"width": 3, "category": "Sicherung"},
    "Motor_Protection": {"width": 3, "category": "Motorschutz"},
    "Contactor_3P": {"width": 3, "category": "Schütz"},
    "Main_Switch_2P": {"width": 2, "category": "Hauptschalter"},
    "Main_Switch_4P": {"width": 4, "category": "Hauptschalter"},
}


def category_summary(devices: list[str]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for device in devices:
        if device not in COMPONENTS:
            raise ValueError(f"unknown rail component: {device}")
        category = COMPONENTS[device]["category"]
        summary[category] = summary.get(category, 0) + COMPONENTS[device]["width"]
    return summary
