#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/tools/apple-notes-exporter"
DIST="$ROOT/dist"
VERSION="${1:-${GITHUB_REF_NAME:-}}"
VERSION="${VERSION#v}"

if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>" >&2
  exit 1
fi
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([+-][0-9A-Za-z.-]+)?$ ]]; then
  echo "Invalid version: $VERSION" >&2
  exit 1
fi

NAME="AppleNotesExporter-$VERSION"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PKG="$WORK/Apple Notes Exporter"

mkdir -p "$PKG" "$DIST"
cp "$SRC/Install.command" "$PKG/Install.command"
cp "$SRC/README.md" "$PKG/README.txt"
printf '%s\n' "$VERSION" > "$PKG/VERSION"
chmod 755 "$PKG/Install.command"

# Release packages must contain a version-pinned bootstrap installer.
grep -q 'VERSION_FILE="$SCRIPT_DIR/VERSION"' "$PKG/Install.command"
grep -q 'REF="v$VERSION"' "$PKG/Install.command"

rm -f "$DIST/$NAME.zip"
(
  cd "$WORK"
  /usr/bin/zip -qry "$DIST/$NAME.zip" "Apple Notes Exporter"
)

echo "$DIST/$NAME.zip"
