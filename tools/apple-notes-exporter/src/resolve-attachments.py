#!/usr/bin/env python3
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

NOTES_ROOT = Path.home() / "Library/Group Containers/group.com.apple.notes"
DB_PATH = NOTES_ROOT / "NoteStore.sqlite"

def attachment_pk(object_id):
    if not object_id:
        return None
    tail = object_id.rsplit("/", 1)[-1]
    if tail.startswith("p") and tail[1:].isdigit():
        return int(tail[1:])
    return None

def find_media_file(media_id, generation, filename):
    if not media_id or not generation or not filename:
        return None
    accounts = NOTES_ROOT / "Accounts"
    if not accounts.is_dir():
        return None
    matches = list(accounts.glob(f"*/Media/{media_id}/{generation}/{filename}"))
    return matches[0] if len(matches) == 1 else None

def safe_name(name):
    name = (name or "attachment").strip() or "attachment"
    for ch in '/\\:*?"<>|':
        name = name.replace(ch, "_")
    return name

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: resolve-attachments.py <export-root>")
    export_root = Path(sys.argv[1]).resolve()
    manifest_path = export_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if not DB_PATH.exists():
        raise SystemExit(f"Apple Notes database not found: {DB_PATH}")

    try:
        db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    except sqlite3.OperationalError as exc:
        raise SystemExit(
            "Cannot read Apple Notes database. Grant Full Disk Access to Terminal "
            "in System Settings > Privacy & Security > Full Disk Access, then retry. "
            f"({exc})"
        )

    copied = missing = structured = 0
    try:
        for note in manifest.get("notes", []):
            note_rel = Path(note["file"])
            asset_dir = note_rel.parent / (note_rel.stem + ".assets")
            used_names = set()
            for att in note.get("attachments", []):
                pk = attachment_pk(att.get("id"))
                if pk is None:
                    att["status"] = "unresolved"
                    missing += 1
                    continue
                row = db.execute(
                    """
                    SELECT a.ZIDENTIFIER, a.ZTYPEUTI, a.ZFILESIZE, a.ZMEDIA,
                           m.ZIDENTIFIER, m.ZFILENAME, m.ZGENERATION1
                    FROM ZICCLOUDSYNCINGOBJECT a
                    LEFT JOIN ZICCLOUDSYNCINGOBJECT m ON m.Z_PK = a.ZMEDIA
                    WHERE a.Z_PK = ?
                    """,
                    (pk,),
                ).fetchone()
                if not row:
                    att["status"] = "unresolved"
                    missing += 1
                    continue

                att_uuid, uti, file_size, media_pk, media_id, filename, generation = row
                att["databaseId"] = pk
                att["identifier"] = att_uuid
                att["uti"] = uti or ""
                att["fileSize"] = file_size or 0

                if not media_pk:
                    att["kind"] = "structured"
                    att["status"] = "metadata-only"
                    structured += 1
                    continue

                att["kind"] = "media"
                att["mediaId"] = media_id or ""
                att["generation"] = generation or ""
                att["originalFilename"] = filename or att.get("name") or ""

                source = find_media_file(media_id, generation, filename)
                if source is None or not source.is_file():
                    att["status"] = "missing"
                    missing += 1
                    continue

                base = safe_name(filename or att.get("name") or f"attachment-{pk}")
                candidate = base
                stem, suffix = os.path.splitext(base)
                n = 2
                while candidate in used_names:
                    candidate = f"{stem}-{n}{suffix}"
                    n += 1
                used_names.add(candidate)

                dest_rel = asset_dir / candidate
                dest = export_root / dest_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                actual_size = dest.stat().st_size
                att["file"] = dest_rel.as_posix()
                att["exportedSize"] = actual_size
                att["status"] = "exported"
                if file_size and actual_size != file_size:
                    att["sizeMismatch"] = True
                copied += 1
    finally:
        db.close()

    manifest["version"] = 3
    stats = manifest.setdefault("stats", {})
    stats["attachmentsExported"] = copied
    stats["attachmentsStructured"] = structured
    stats["attachmentsMissing"] = missing
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Attachments: {copied} exported, {structured} structured, {missing} missing")

if __name__ == "__main__":
    main()
