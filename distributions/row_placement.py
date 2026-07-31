import csv
from pathlib import Path


def load_layout(filename):
    with open(filename, newline='') as file:
        return list(csv.DictReader(file))


def validate_layout(rows, modules_per_row):
    used = {}
    errors = []
    for row in rows:
        key = row['Row']
        used[key] = used.get(key, 0) + int(row['Modules'])
    for row, total in used.items():
        if total > modules_per_row:
            errors.append(f'Row {row}: {total} modules > {modules_per_row}')
    return errors


if __name__ == '__main__':
    template = Path('row_layout_template.csv')
    rows = load_layout(template)
    for variant, capacity in [('UV_1ROW', 12), ('UV_2ROW', 12)]:
        subset = [r for r in rows if r['Variant'] == variant]
        print(variant, validate_layout(subset, capacity))
