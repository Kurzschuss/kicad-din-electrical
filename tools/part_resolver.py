import yaml


def load_rules(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)


def resolve_part(part, alternatives):
    return alternatives.get(part, [])


if __name__ == '__main__':
    rules = load_rules('alternatives.yaml')
    print(rules)
