#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then echo 'Usage: ./generate.sh presentation.txt [voice] [speed]'; exit 1; fi
python3 "$(dirname "$0")/generate.py" "$1" "${2:-am_adam}" "${3:-0.85}"
