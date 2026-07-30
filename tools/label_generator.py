import csv


def generate_labels(source, output):
    with open(source, newline='') as src:
        rows = csv.DictReader(src)
        with open(output, 'w', newline='') as dst:
            writer = csv.DictWriter(dst, fieldnames=rows.fieldnames)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == '__main__':
    generate_labels('label_template.csv', 'device_labels.csv')
