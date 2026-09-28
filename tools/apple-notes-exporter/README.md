# Apple Notes Exporter

A small macOS utility for exporting Apple Notes for use with FlowLogue and other data workflows.

## What it exports

- Note title and HTML body
- Apple Notes account and nested folder path
- Created and modified timestamps
- Stable Apple Notes object ID
- `manifest.json` for deterministic downstream import
- Excludes `Recently Deleted` by default
- Deduplicates notes by Apple Notes ID

Attachments are not exported separately yet.

## Requirements

- macOS with Apple Notes
- Notes available on the Mac (for iCloud Notes, allow sync to complete)
- Permission for Terminal / osascript to automate Notes when macOS asks

## Install — one command

```bash
curl -fsSL https://raw.githubusercontent.com/ZunagesCo/flowlogue-public/main/tools/apple-notes-exporter/install.sh | bash
```

Then run `export-notes`. A new Terminal window will find the command automatically. In the same shell, run `source ~/.zprofile` first.

## Install — download and double-click

Download this repository as ZIP, open `tools/apple-notes-exporter`, then double-click `Install.command`.

Because this is currently an unsigned shell utility, macOS may require Control-click / Right-click → Open on first launch.

## Output

```text
~/Documents/AppleNotesExport/current/
├── manifest.json
└── notes/
    └── <account>/<folder path>/<stable-id>.html
```

The exporter writes to staging first and replaces `current` only after a valid manifest is produced.

## Uninstall

```bash
~/Library/Application\ Support/AppleNotesExporter/uninstall.sh
```

Uninstalling the utility does not delete exported notes.

## Privacy

All export processing happens locally on the Mac. The exporter does not upload Notes content to GitHub or FlowLogue.

## Status

Early public utility. Export format version: **2**.
