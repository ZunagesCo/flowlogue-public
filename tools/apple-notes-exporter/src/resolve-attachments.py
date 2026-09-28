#!/usr/bin/env python3
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

NOTES_ROOT = Path.home() / "Library/Group Containers/group.com.apple.notes"
DB_PATH = NOTES_ROOT / "NoteStore.sqlite"
ACCOUNTS_ROOT = NOTES_ROOT / "Accounts"

def object_pk(object_id):
    if not object_id:
        return None
    tail = object_id.rsplit("/", 1)[-1]
    return int(tail[1:]) if tail.startswith("p") and tail[1:].isdigit() else None

def safe_name(name):
    name = (name or "attachment").strip() or "attachment"
    for ch in '/\\:*?"<>|':
        name = name.replace(ch, "_")
    return name

def unique_file(matches):
    files = []
    seen = set()
    for p in matches:
        try:
            if p.is_file():
                rp = p.resolve()
                if rp not in seen:
                    seen.add(rp)
                    files.append(p)
        except OSError:
            pass
    return files[0] if len(files) == 1 else None

def find_media_file(media_id, generation, filename):
    if not media_id or not generation or not filename or not ACCOUNTS_ROOT.is_dir():
        return None
    return unique_file(ACCOUNTS_ROOT.glob(f"*/Media/{media_id}/{generation}/{filename}"))

def find_paper_pdf(identifier, generation):
    if not identifier or not generation or not ACCOUNTS_ROOT.is_dir():
        return None
    patterns = [
        f"*/FallbackPDFs/{identifier}/{generation}/*",
        f"*/FallbackPDFs/{identifier}/{generation}/**/*",
        f"*/Paper/**/{identifier}/**/{generation}/**/*",
        f"*/Paper/**/{generation}/**/*",
    ]
    candidates = []
    for pattern in patterns:
        candidates.extend(ACCOUNTS_ROOT.glob(pattern))
    pdfs = [p for p in candidates if p.is_file() and (p.suffix.lower() == ".pdf" or p.name.lower().endswith("pdf"))]
    found = unique_file(pdfs)
    if found:
        return found
    # Apple has changed Paper/Fallback layouts across Notes versions. As a
    # conservative fallback, search only for the exact generation token and
    # accept the result only when it resolves to one PDF.
    candidates = []
    try:
        for p in ACCOUNTS_ROOT.rglob("*"):
            if generation in p.parts or generation in p.name:
                if p.is_file() and p.suffix.lower() == ".pdf":
                    candidates.append(p)
    except OSError:
        pass
    return unique_file(candidates)

def db_inventory(db, note_pk):
    rows = db.execute(
        """
        SELECT a.Z_PK, a.ZIDENTIFIER, a.ZTYPEUTI, a.ZFILESIZE, a.ZMEDIA,
               a.ZPARENTATTACHMENT, a.ZPARENTATTACHMENT1,
               a.ZFALLBACKPDFGENERATION, a.ZPAPERBUNDLEGENERATION,
               a.ZTITLE, a.ZSUMMARY,
               m.ZIDENTIFIER, m.ZFILENAME, m.ZGENERATION1
        FROM ZICCLOUDSYNCINGOBJECT a
        LEFT JOIN ZICCLOUDSYNCINGOBJECT m ON m.Z_PK = a.ZMEDIA
        WHERE a.ZNOTE1 = ?
          AND a.Z_PK != ?
          AND COALESCE(a.ZPARENTATTACHMENT, 0) = 0
          AND COALESCE(a.ZPARENTATTACHMENT1, 0) = 0
        ORDER BY a.Z_PK
        """,
        (note_pk, note_pk),
    ).fetchall()
    return rows

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
            note_pk = object_pk(note.get("id"))
            if note_pk is None:
                continue
            note_rel = Path(note["file"])
            asset_dir = note_rel.parent / (note_rel.stem + ".assets")
            jxa_by_pk = {
                object_pk(a.get("id")): a
                for a in note.get("attachments", [])
                if object_pk(a.get("id")) is not None
            }
            resolved = []
            used_names = set()

            for row in db_inventory(db, note_pk):
                (pk, identifier, uti, file_size, media_pk, parent, parent1,
                 fallback_pdf_generation, paper_bundle_generation, title, summary,
                 media_id, filename, media_generation) = row

                att = dict(jxa_by_pk.get(pk, {}))
                att["id"] = att.get("id") or f"db-p{pk}"
                att["databaseId"] = pk
                att["identifier"] = identifier or ""
                att["uti"] = uti or ""
                att["fileSize"] = file_size or 0
                if title and not att.get("name"):
                    att["name"] = title

                source = None
                export_name = None

                if media_pk:
                    att["kind"] = "media"
                    att["mediaId"] = media_id or ""
                    att["generation"] = media_generation or ""
                    att["originalFilename"] = filename or att.get("name") or ""
                    source = find_media_file(media_id, media_generation, filename)
                    export_name = filename or att.get("name") or f"attachment-{pk}"
                elif (uti or "") in ("com.apple.paper.doc.pdf", "com.apple.paper.doc.scan") and fallback_pdf_generation:
                    att["kind"] = "paper-pdf"
                    att["fallbackPdfGeneration"] = fallback_pdf_generation
                    att["paperBundleGeneration"] = paper_bundle_generation or ""
                    source = find_paper_pdf(identifier, fallback_pdf_generation)
                    export_name = (title or att.get("name") or f"attachment-{pk}") + ".pdf"
                else:
                    att["kind"] = "structured"
                    att["status"] = "metadata-only"
                    if summary:
                        att["summary"] = summary
                    structured += 1
                    resolved.append(att)
                    continue

                if source is None:
                    att["status"] = "missing"
                    missing += 1
                    resolved.append(att)
                    continue

                base = safe_name(export_name)
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
                resolved.append(att)

            note["attachments"] = resolved
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
