import csv
from pathlib import Path


def generate_bom(input_file, output_file):
    with open(input_file, newline='') as src:
        rows = list(csv.DictReader(src))

    with open(output_file, 'w', newline='') as dst:
        writer = csv.DictWriter(dst, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    generate_bom(
        'bom_template.csv',
        'generated_bom.csv'
    )
