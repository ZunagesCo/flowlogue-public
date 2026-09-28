#!/bin/bash
set -e
clear

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION_FILE="$SCRIPT_DIR/VERSION"
if [[ -f "$VERSION_FILE" ]]; then
  VERSION="$(tr -d '[:space:]' < "$VERSION_FILE")"
  REF="v$VERSION"
else
  VERSION="development"
  REF="main"
fi

echo "FlowLogue — Apple Notes Exporter $VERSION"
echo
INSTALL_URL="https://raw.githubusercontent.com/ZunagesCo/flowlogue-public/$REF/tools/apple-notes-exporter/install.sh"
/bin/bash -c "$(curl -fsSL "$INSTALL_URL")" -- "$VERSION" "$REF"
echo
read -n 1 -s -r -p "Press any key to close..."
echo
