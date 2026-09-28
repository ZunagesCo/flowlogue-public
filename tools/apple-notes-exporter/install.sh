#!/bin/bash
set -euo pipefail

VERSION="${1:-development}"
REF="${2:-main}"
REPO_RAW="https://raw.githubusercontent.com/ZunagesCo/flowlogue-public/$REF/tools/apple-notes-exporter"
APP_DIR="$HOME/Library/Application Support/AppleNotesExporter"
BIN_DIR="$HOME/.local/bin"
EXPORT_ROOT="$HOME/Documents/AppleNotesExport"

mkdir -p "$APP_DIR" "$BIN_DIR" "$EXPORT_ROOT"

STAGING="$(mktemp -d)"
cleanup() { rm -rf "$STAGING"; }
trap cleanup EXIT

download() {
  local remote="$1"
  local local_name="$2"
  curl -fL --retry 3 --retry-all-errors \
    -H 'Cache-Control: no-cache' \
    "$REPO_RAW/$remote?ref=$REF" \
    -o "$STAGING/$local_name"
  test -s "$STAGING/$local_name"
}

download "src/export-notes.js" "export-notes.js"
download "src/resolve-attachments.py" "resolve-attachments.py"
download "bin/export-notes" "export-notes"
download "uninstall.sh" "uninstall.sh"

# Validate the complete payload before replacing a working installation.
grep -q '^def main():' "$STAGING/resolve-attachments.py"
grep -q 'resolve-attachments.py' "$STAGING/export-notes"

install -m 644 "$STAGING/export-notes.js" "$APP_DIR/export-notes.js"
install -m 644 "$STAGING/resolve-attachments.py" "$APP_DIR/resolve-attachments.py"
install -m 755 "$STAGING/export-notes" "$BIN_DIR/export-notes"
install -m 755 "$STAGING/uninstall.sh" "$APP_DIR/uninstall.sh"
printf '%s\n' "$VERSION" > "$APP_DIR/VERSION"

trap - EXIT
cleanup

PROFILE="$HOME/.zprofile"
touch "$PROFILE"
PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
if ! grep -Fqx "$PATH_LINE" "$PROFILE"; then
  printf '\n%s\n' "$PATH_LINE" >> "$PROFILE"
fi

echo "Apple Notes Exporter $VERSION installed."
echo "Exporter: $APP_DIR"
echo "Exports: $EXPORT_ROOT"
echo "Command: export-notes"
echo
echo "Starting first export..."
PATH="$HOME/.local/bin:$PATH" export-notes
