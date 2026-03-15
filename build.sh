#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

pip3 install -q -r "$SCRIPT_DIR/requirements.txt"
exec python3 "$SCRIPT_DIR/build.py" "$@"
