import csv
from collections import Counter


def read_parts(filename):
    with open(filename, newline='') as f:
        return list(csv.DictReader(f))


def build_bom(parts, selections):
    index = {(p['Manufacturer'], p['Series']): p for p in parts}
    bom = Counter()
    for manufacturer, series in selections:
        key = (manufacturer, series)
        if key not in index:
            raise KeyError(f'Unknown part: {manufacturer} {series}')
        bom[key] += 1
    return bom


if __name__ == '__main__':
    parts = read_parts('parts_catalog.csv')
    selections = [('ABB', 'S201'), ('ABB', 'F200'), ('Hager', 'ADS')]
    for (manufacturer, series), qty in build_bom(parts, selections).items():
        print(f'{qty}x {manufacturer} {series}')
