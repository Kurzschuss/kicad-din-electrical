"""Planning metadata for DIN busbars and distribution rails."""

BUSBAR_TYPES = {
    "PHASE_1P": 1,
    "PHASE_2P": 2,
    "PHASE_3P": 3,
    "PHASE_4P": 4,
    "THREE_PHASE": 3,
    "RCD_2P": 2,
    "RCD_4P": 4,
    "RCBO_1P_N": 2,
    "FUSE_1P": 1,
    "FUSE_2P": 2,
    "FUSE_3P": 3,
}


def validate_busbar(busbar_type: str, device_poles: int) -> dict:
    if busbar_type not in BUSBAR_TYPES:
        raise ValueError(f"unknown busbar type: {busbar_type}")
    if not isinstance(device_poles, int) or device_poles < 1:
        raise ValueError("device_poles must be a positive integer")
    capacity = BUSBAR_TYPES[busbar_type]
    compatible = device_poles <= capacity
    return {
        "busbar": busbar_type,
        "capacity_poles": capacity,
        "device_poles": device_poles,
        "compatible": compatible,
    }
