#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
NODE_MODULES_DIR="${SKILL_ROOT}/node_modules"
REQUIREMENTS_FILE="${SKILL_ROOT}/requirements.txt"

if [[ -d "${NODE_MODULES_DIR}" ]]; then
  echo "Dependencies already installed."
else
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is not installed or not on PATH." >&2
    exit 1
  fi

  cd "${SKILL_ROOT}"
  npm ci
fi

if ! command -v python >/dev/null 2>&1; then
  echo "python is not installed or not on PATH." >&2
  exit 1
fi

python -m pip install -r "${REQUIREMENTS_FILE}"
echo "DOCX assistant dependencies installed."
