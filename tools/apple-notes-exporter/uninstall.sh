#!/bin/bash
set -euo pipefail
APP_DIR="$HOME/Library/Application Support/AppleNotesExporter"
BIN="$HOME/.local/bin/export-notes"
rm -f "$BIN"
rm -rf "$APP_DIR"
echo "Apple Notes Exporter removed."
echo "Exported data was left untouched in:"
echo "$HOME/Documents/AppleNotesExport"
