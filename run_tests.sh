#!/usr/bin/env bash
set -u

cd "$(dirname "$0")"

if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
fi

if ! command -v python >/dev/null 2>&1; then
    echo "FEHLER: Python wurde nicht gefunden." >&2
    exit 1
fi

python -m pytest -q
