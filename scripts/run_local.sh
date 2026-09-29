#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PIP_INDEX="${PIP_INDEX:-https://pypi.tuna.tsinghua.edu.cn/simple}"
PIP_TRUSTED_HOST="${PIP_TRUSTED_HOST:-pypi.tuna.tsinghua.edu.cn}"

# Homebrew python@3.12 may break pip (pyexpat); prefer macOS system Python for venv.
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  if [[ -x /usr/bin/python3 ]]; then
    PYTHON=/usr/bin/python3
  else
    PYTHON=python3
  fi
fi

if [[ ! -x "$ROOT/venv/bin/python" ]]; then
  echo "Creating venv with $PYTHON ..."
  rm -rf "$ROOT/venv"
  "$PYTHON" -m venv "$ROOT/venv"
fi

PIP="$ROOT/venv/bin/pip"
"$PIP" install --upgrade pip -i "$PIP_INDEX" --trusted-host "$PIP_TRUSTED_HOST"
"$PIP" install -r "$ROOT/requirements.txt" -i "$PIP_INDEX" --trusted-host "$PIP_TRUSTED_HOST"

exec "$ROOT/venv/bin/python" "$ROOT/src/main.py"
