#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/build_inputs"
if [[ ! -x "$ROOT/build_inputs/node" ]]; then
  echo "Copy the matching Node.js 22 LTS binary to build_inputs/node first." >&2
  exit 1
fi
chmod +x "$ROOT/build_inputs/node"
echo "macOS runtime inputs ready. macOS provides /usr/bin/ssh."
