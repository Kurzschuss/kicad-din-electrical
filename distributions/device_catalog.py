"""Module widths used by the DIN distribution planner.

Widths are planning defaults in DIN modules. They are not manufacturer-specific
mechanical guarantees; verify the actual product datasheet before fabrication.
"""

DEVICE_WIDTHS = {
    "MCB_1P": 1,
    "MCB_2P": 2,
    "MCB_3P": 3,
    "MCB_4P": 4,
    "RCD_2P": 2,
    "RCD_4P": 4,
    "RCBO_1P_N": 2,
    "Fuse_1P": 1,
    "Fuse_2P": 2,
    "Fuse_3P": 3,
    "Motor_Protection": 3,
    "Contactor_3P": 3,
    "Main_Switch_2P": 2,
    "Main_Switch_4P": 4,
    "Terminal_Block": 1,
    "N_PE_Terminal": 1,
}

MAX_MODULES = 216


def modules_for(devices: list[str]) -> int:
    try:
        total = sum(DEVICE_WIDTHS[name] for name in devices)
    except KeyError as exc:
        raise ValueError(f"unknown device type: {exc.args[0]}") from exc
    if total > MAX_MODULES:
        raise ValueError(f"device layout requires {total} modules; maximum is {MAX_MODULES}")
    return total
