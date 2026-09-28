ObjC.import('Foundation');

function str(v) {
  if (v === null || v === undefined) return '';
  return String(v);
}
function iso(v) {
  try { return new Date(v).toISOString(); } catch (_) { return ''; }
}
function safePart(s) {
  s = str(s).trim() || 'Untitled';
  return s.replace(/[\\/:*?"<>|]/g, '_').replace(/^\.+$/, '_');
}
function writeText(path, text) {
  const ns = $(str(text));
  const ok = ns.writeToFileAtomicallyEncodingError(path, true, $.NSUTF8StringEncoding, null);
  if (!ok) throw new Error('Unable to write: ' + path);
}
function mkdir(path) {
  $.NSFileManager.defaultManager.createDirectoryAtPathWithIntermediateDirectoriesAttributesError(path, true, $(), null);
}
function join(a, b) {
  return $(a).stringByAppendingPathComponent(b).js;
}
function getId(obj) {
  try { return str(obj.id()); } catch (_) { return ''; }
}
function getChildFolders(folder) {
  try { return folder.folders(); } catch (_) { return []; }
}
function findRootFolders(account) {
  const allFolders = account.folders();
  const childIds = {};
  for (let i = 0; i < allFolders.length; i++) {
    const children = getChildFolders(allFolders[i]);
    for (let j = 0; j < children.length; j++) {
      const id = getId(children[j]);
      if (id) childIds[id] = true;
    }
  }
  const roots = [];
  for (let i = 0; i < allFolders.length; i++) {
    const id = getId(allFolders[i]);
    if (!id || !childIds[id]) roots.push(allFolders[i]);
  }
  return roots;
}
function exportFolder(folder, accountName, parentParts, outRoot, manifest, seenNoteIds, visitedFolderIds) {
  const folderId = getId(folder);
  if (folderId && visitedFolderIds[folderId]) return;
  if (folderId) visitedFolderIds[folderId] = true;
  const folderName = str(folder.name());
  if (folderName === 'Recently Deleted') {
    manifest.stats.excludedRecentlyDeletedFolders++;
    return;
  }
  const parts = parentParts.concat([folderName]);
  const notes = folder.notes();
  for (let i = 0; i < notes.length; i++) {
    const note = notes[i];
    const noteId = getId(note);
    if (noteId && seenNoteIds[noteId]) {
      manifest.stats.duplicateIdsSkipped++;
      continue;
    }
    if (noteId) seenNoteIds[noteId] = true;
    const title = str(note.name());
    const body = str(note.body());
    const attachmentList = [];
    let noteAttachments = [];
    try { noteAttachments = note.attachments(); } catch (_) {}
    for (let ai = 0; ai < noteAttachments.length; ai++) {
      const attachment = noteAttachments[ai];
      let props = {};
      try { props = attachment.properties(); } catch (_) {}
      attachmentList.push({
        id: getId(attachment),
        name: props.name === null || props.name === undefined ? null : str(props.name),
        contentIdentifier: props.contentIdentifier === null || props.contentIdentifier === undefined ? null : str(props.contentIdentifier),
        created: iso(props.creationDate),
        modified: iso(props.modificationDate)
      });
    }
    const stableName = safePart(noteId || ('note-' + i)) + '.html';
    let dir = join(outRoot, 'notes');
    dir = join(dir, safePart(accountName));
    for (let p = 0; p < parts.length; p++) dir = join(dir, safePart(parts[p]));
    mkdir(dir);
    writeText(join(dir, stableName), body);
    const relParts = ['notes', safePart(accountName)].concat(parts.map(safePart)).concat([stableName]);
    manifest.notes.push({
      id: noteId,
      title: title,
      account: accountName,
      folder: parts.join('/'),
      created: iso(note.creationDate()),
      modified: iso(note.modificationDate()),
      file: relParts.join('/'),
      attachments: attachmentList
    });
  }
  const children = getChildFolders(folder);
  for (let i = 0; i < children.length; i++) {
    exportFolder(children[i], accountName, parts, outRoot, manifest, seenNoteIds, visitedFolderIds);
  }
}
function run(argv) {
  if (!argv || argv.length < 1) throw new Error('Output directory argument is required.');
  const outRoot = argv[0];
  mkdir(outRoot);
  const Notes = Application('Notes');
  Notes.includeStandardAdditions = true;
  const manifest = {
    format: 'apple-notes-export',
    version: 3,
    exportedAt: new Date().toISOString(),
    stats: { duplicateIdsSkipped: 0, excludedRecentlyDeletedFolders: 0 },
    notes: []
  };
  const seenNoteIds = {};
  const visitedFolderIds = {};
  const accounts = Notes.accounts();
  for (let a = 0; a < accounts.length; a++) {
    const account = accounts[a];
    const accountName = str(account.name());
    const roots = findRootFolders(account);
    for (let f = 0; f < roots.length; f++) {
      exportFolder(roots[f], accountName, [], outRoot, manifest, seenNoteIds, visitedFolderIds);
    }
  }
  manifest.noteCount = manifest.notes.length;
  manifest.uniqueNoteCount = Object.keys(seenNoteIds).length;
  writeText(join(outRoot, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  console.log('Notes: ' + manifest.noteCount);
}
