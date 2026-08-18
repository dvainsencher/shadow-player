#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "Open http://127.0.0.1:8000"
python3 server.py
