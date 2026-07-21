#!/usr/bin/env bash
# Wrapper for setup.py on macOS / Linux
exec python3 "$(dirname "$0")/setup.py" "$@"
