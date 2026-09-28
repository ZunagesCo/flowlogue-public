#!/bin/bash
set -euo pipefail
REPO_RAW="https://raw.githubusercontent.com/ZunagesCo/flowlogue-public/main/tools/apple-notes-exporter"
APP_DIR="$HOME/Library/Application Support/AppleNotesExporter"
BIN_DIR="$HOME/.local/bin"
EXPORT_ROOT="$HOME/Documents/AppleNotesExport"
mkdir -p "$APP_DIR" "$BIN_DIR" "$EXPORT_ROOT"
curl -fsSL "$REPO_RAW/src/export-notes.js" -o "$APP_DIR/export-notes.js"
curl -fsSL "$REPO_RAW/bin/export-notes" -o "$BIN_DIR/export-notes"
curl -fsSL "$REPO_RAW/uninstall.sh" -o "$APP_DIR/uninstall.sh"
chmod +x "$BIN_DIR/export-notes" "$APP_DIR/uninstall.sh"
PROFILE="$HOME/.zprofile"
touch "$PROFILE"
PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
if ! grep -Fqx "$PATH_LINE" "$PROFILE"; then
  printf '\n%s\n' "$PATH_LINE" >> "$PROFILE"
fi
echo "Apple Notes Exporter installed."
echo "Exporter: $APP_DIR"
echo "Exports: $EXPORT_ROOT"
echo "Command: export-notes"
echo
echo "Starting first export..."
PATH="$HOME/.local/bin:$PATH" export-notes
