from pathlib import Path


def generate_report(template, output):
    text = Path(template).read_text()
    Path(output).write_text(text)


if __name__ == '__main__':
    generate_report(
        'cabinet_report_template.md',
        'cabinet_report.md'
    )
