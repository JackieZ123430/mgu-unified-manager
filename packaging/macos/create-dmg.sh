#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP="$ROOT/dist/MGU Unified Manager.app"
OUT="$ROOT/dist-installer"
mkdir -p "$OUT"
test -d "$APP" || { echo "Missing $APP"; exit 1; }
DMG="$OUT/MGU-Unified-Manager-macOS.dmg"
rm -f "$DMG"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname "MGU Unified Manager" -srcfolder "$STAGE" -ov -format UDZO "$DMG"
echo "Created $DMG"
