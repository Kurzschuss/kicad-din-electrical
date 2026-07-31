import csv

from distributions.terminal_labels import apply_terminal_labels
from distributions.terminal_validation import validate_terminal_labels


def generate_terminal_report(source, output, schema=None):
    """Generate a terminal report while preserving custom terminal labels."""
    with open(source, newline='', encoding='utf-8') as src:
        rows = list(csv.DictReader(src))

    labeled = []
    for row in rows:
        terminal = row.get('Terminal', '')
        rail = row.get('Rail') or terminal.split('.')[0] or 'X1'
        number_text = row.get('TerminalNumber')
        try:
            number = int(number_text) if number_text else int(''.join(ch for ch in terminal.split('.')[-1] if ch.isdigit()))
        except ValueError:
            number = len(labeled) + 1
        labeled.append({
            **row,
            'terminal_rail': rail,
            'terminal_number': number,
            'custom_terminal_label': row.get('CustomLabel') or None,
        })

    labeled = apply_terminal_labels(labeled, schema)
    labeled = validate_terminal_labels(labeled)

    fieldnames = list(rows[0].keys()) if rows else ['Terminal', 'Type', 'Signal', 'Device']
    for field in ('Terminal', 'Rail', 'TerminalNumber', 'LabelValid', 'LabelErrors'):
        if field not in fieldnames:
            fieldnames.append(field)

    with open(output, 'w', newline='', encoding='utf-8') as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in labeled:
            row['Terminal'] = row['terminal_label']
            row['Rail'] = row['terminal_rail']
            row['TerminalNumber'] = row['terminal_number']
            row['LabelValid'] = 'yes' if row['terminal_label_valid'] else 'no'
            row['LabelErrors'] = '; '.join(row['terminal_label_errors'])
            writer.writerow(row)


if __name__ == '__main__':
    generate_terminal_report('terminal_template.csv', 'terminal_report.csv')
