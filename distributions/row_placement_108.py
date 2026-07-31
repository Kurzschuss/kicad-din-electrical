import csv
from collections import defaultdict


def load_layout(filename):
    with open(filename, newline='') as file:
        return list(csv.DictReader(file))


def validate_layout(rows, modules_per_row=12):
    used = defaultdict(int)
    errors = []
    for item in rows:
        row = int(item['Row'])
        modules = int(item['Modules'])
        used[row] += modules
        if used[row] > modules_per_row:
            errors.append(f'Row {row}: {used[row]} modules > {modules_per_row}')
    return sorted(errors)


def validate_variant(rows, variant, rows_count):
    subset = [r for r in rows if r['Variant'] == variant]
    errors = validate_layout(subset)
    expected = rows_count * 12
    if not subset:
        errors.append(f'{variant}: no layout entries')
    if expected > 108:
        errors.append(f'{variant}: exceeds supported capacity of 108 modules')
    return errors


if __name__ == '__main__':
    rows = load_layout('row_layout_template.csv')
    variants = [(f'UV_{n}ROW', n) for n in range(1, 10)]
    for variant, count in variants:
        errors = validate_variant(rows, variant, count)
        print(f'{variant}: OK' if not errors else f'{variant}: {errors}')
