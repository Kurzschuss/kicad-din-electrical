from dataclasses import dataclass

MODULES_PER_ROW = 12
MAX_MODULES = 108

@dataclass
class Device:
    name: str
    modules: int


def build_rows(devices, total_modules):
    if total_modules % MODULES_PER_ROW or total_modules > MAX_MODULES:
        raise ValueError('Capacity must be 12..108 modules in 12-module steps')
    rows = [[] for _ in range(total_modules // MODULES_PER_ROW)]
    row = 0
    used = 0
    for device in devices:
        if device.modules > MODULES_PER_ROW:
            raise ValueError(f'{device.name} exceeds one-row capacity')
        if used + device.modules > MODULES_PER_ROW:
            row += 1
            used = 0
        if row >= len(rows):
            raise ValueError('Not enough distribution capacity')
        rows[row].append(device)
        used += device.modules
    return rows


def example_layout():
    return build_rows([
        Device('MAIN_SWITCH', 2),
        Device('RCD_4P', 4),
        Device('MCB_B16', 1),
        Device('MCB_B16', 1),
        Device('MCB_C16', 1),
        Device('MCB_C25', 1),
        Device('RESERVE', 2),
    ], 24)
