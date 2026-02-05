#!/usr/bin/env bash
# Example run script for Linux. Must run where /sys/fs/cgroup is accessible.

set -euo pipefail

# Create venv and install dependencies if not present
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -r requirements.txt

# Run agent in dry-run on local cgroup root (.) — replace with real cgroup paths
python -m src.agent . --dry-run
