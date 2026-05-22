#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REQUIREMENTS_FILE="${SKILL_ROOT}/requirements.txt"

if ! command -v python >/dev/null 2>&1; then
  echo "python is not installed or not on PATH." >&2
  exit 1
fi

python -m pip install -r "${REQUIREMENTS_FILE}"
echo "Tasklist Gantt Creator dependencies installed."
