# Apple Notes Exporter for FlowLogue

A lightweight macOS utility that exports Apple Notes into a structured, local format suitable for importing into **FlowLogue** or for keeping as a portable archive.

The exporter is designed to preserve the information needed for reliable, repeatable imports: note identity, account, folder hierarchy, timestamps, title, HTML content, and supported original attachments.

> **Privacy:** your Notes stay on your Mac. This utility does not upload note content to GitHub, FlowLogue, or any other service.

[Русская версия](#русская-версия)

---

## English

### What it does

Apple Notes Exporter reads notes available in the macOS Notes application and creates a structured export under:

```text
~/Documents/AppleNotesExport/current/
```

For each note, the exporter preserves:

- note title;
- note body as HTML;
- Apple Notes account name;
- complete nested folder path;
- creation timestamp;
- modification timestamp;
- stable Apple Notes object ID;
- relative path to the exported note file;
- supported original attachments, including media files and Paper/PDF fallback files, in per-note `.assets` directories;
- attachment metadata and export status in the manifest.

Deleted/ghost attachment records marked by Apple Notes are excluded. Child representations of another attachment are not exported as separate top-level attachments.

It also creates a machine-readable `manifest.json` that allows FlowLogue or another importer to understand the export without guessing folder names or relying only on filenames.

### Why stable IDs matter

A note's Apple Notes object ID is stored in the manifest and used as part of the exported representation. This makes it possible for a downstream importer to identify the same note on later exports instead of treating every export as a completely new collection.

This is especially useful for future incremental synchronization and duplicate prevention.

### Folder hierarchy

Nested Apple Notes folders are preserved.

For example:

```text
Apple Notes
└── Projects
    └── Research
        └── Example note
```

is represented under the corresponding account and folder path in the export.

The exporter explicitly detects true root folders before recursively walking child folders. This prevents nested folders from being exported more than once.

### Duplicate protection

During one export, note IDs are tracked globally. If the same Apple Notes object is encountered again, it is skipped rather than exported twice.

The manifest records the number of duplicate IDs skipped.

### Recently Deleted

The Apple Notes `Recently Deleted` folder is excluded by default.

The manifest records how many such folders were excluded.

### Export format

Current export format version: **3**.

Typical structure:

```text
~/Documents/AppleNotesExport/
└── current/
    ├── manifest.json
    └── notes/
        └── <account>/
            └── <folder>/
                ├── <stable-note-id>.html
                └── <stable-note-id>.assets/
                    └── <attachment files>
```

A manifest contains information similar to:

```json
{
  "format": "apple-notes-export",
  "version": 3,
  "exportedAt": "2026-09-28T12:00:00.000Z",
  "stats": {
    "duplicateIdsSkipped": 0,
    "excludedRecentlyDeletedFolders": 1,
    "attachmentsExported": 5,
    "attachmentsStructured": 2,
    "attachmentsMissing": 0
  },
  "notes": [],
  "noteCount": 6,
  "uniqueNoteCount": 6
}
```

### Safe replacement of previous exports

The command does not write directly over the existing `current` export.

It first creates a staging export. Only after `manifest.json` has been successfully created does the wrapper replace `current`.

This reduces the chance of losing a previous successful export because of an interrupted or failed run.

### Requirements

- macOS;
- Apple Notes;
- notes must be available locally in the macOS Notes application;
- `osascript`, included with macOS;
- `python3` for the attachment resolver;
- permission to automate Apple Notes when macOS requests it;
- Full Disk Access for the terminal/host application so original Notes media can be read;
- Internet access during installation when using the public installer.

No Git installation, GitHub account, `gh` CLI, Node.js, or Apple Developer account is required.

### Installation from Terminal

Run:

```bash
curl -fsSL https://raw.githubusercontent.com/ZunagesCo/flowlogue-public/main/tools/apple-notes-exporter/install.sh | bash
```

The installer places the exporter in:

```text
~/Library/Application Support/AppleNotesExporter/
```

and installs the command:

```text
~/.local/bin/export-notes
```

It also adds `~/.local/bin` to `PATH` through `~/.zprofile` if necessary.

The installer performs the first export automatically.

### Running later exports

After installation:

```bash
export-notes
```

If you installed the utility in an already-open Terminal session and the command is not yet found, either open a new Terminal window or run:

```bash
source ~/.zprofile
```

### macOS permissions

On first use, macOS may ask whether Terminal or `osascript` is allowed to control Notes. The exporter needs this permission to read Notes through Apple's automation interface.

If you use the downloadable `Install.command`, macOS Gatekeeper may also warn that the file is from an unidentified developer because the utility is currently distributed without Apple Developer ID signing/notarization.

For original attachments, **Terminal must have Full Disk Access**: open **System Settings → Privacy & Security → Full Disk Access** and enable Terminal. If you change this permission while Terminal is running, quit Terminal completely and reopen it before running `export-notes` again.

### Uninstall

Run:

```bash
~/Library/Application\ Support/AppleNotesExporter/uninstall.sh
```

The uninstaller removes the installed utility and the `export-notes` command.

It intentionally **does not delete**:

```text
~/Documents/AppleNotesExport/
```

so uninstalling the utility does not destroy your exported notes.

### Current limitations

- Original file/media attachments backed by Apple Notes `Media` records are exported into per-note `.assets` directories.
- Structured Notes objects such as `com.apple.notes.table` are recorded in the manifest as metadata-only; they remain represented by the note HTML rather than as fake files.
- Paper/PDF fallback files are exported when their active Apple Notes database record can be resolved to a unique local PDF.
- Some specialized Notes objects, especially drawings/scans and other structured representations, may still be metadata-only or require additional handling.
- Note bodies are exported as the HTML returned by Apple Notes automation.
- The utility currently targets macOS; it does not run directly on iPhone or iPad.
- The downloadable installer is currently unsigned/not notarized.
- This is an early public utility and its export format may evolve. Format changes will be versioned.

### Privacy and data handling

The exporter runs locally.

It reads Apple Notes through macOS automation and writes the result to your local `Documents` folder. The exporter itself contains no code that sends note content to FlowLogue, GitHub, or another remote service.

Publishing this source repository does **not** publish your notes.

### Relationship to FlowLogue

This exporter is a public companion utility for FlowLogue. Its structured manifest is intended to make Apple Notes import, deduplication, and future synchronization easier.

The main FlowLogue application is not contained in this repository.

---

# Русская версия

## Что это такое

**Apple Notes Exporter for FlowLogue** — небольшая утилита для macOS, которая экспортирует заметки из Apple Notes в структурированный локальный формат.

Основное назначение — подготовить Apple Notes для последующего импорта в **FlowLogue**, сохранив при этом структуру папок и идентификаторы заметок. Экспорт также можно использовать как локальную переносимую копию заметок.

По умолчанию результат находится здесь:

```text
~/Documents/AppleNotesExport/current/
```

### Что сохраняется

Для каждой заметки экспортируются:

- название;
- содержимое заметки в HTML;
- название аккаунта Apple Notes;
- полный путь вложенных папок;
- дата создания;
- дата последнего изменения;
- стабильный внутренний ID Apple Notes;
- путь к экспортированному HTML-файлу;
- поддерживаемые оригинальные вложения, включая media-файлы и Paper/PDF fallback-файлы, в `.assets` рядом с заметкой;
- метаданные вложений и статус их экспорта в manifest.

Удалённые/ghost-записи вложений, помеченные Apple Notes на удаление, исключаются. Дочерние представления другого вложения не экспортируются как отдельные top-level вложения.

Дополнительно создаётся `manifest.json`, содержащий структурированные метаданные всего экспорта.

### Зачем сохранять Apple Notes ID

Внутренний ID позволяет в дальнейшем определить, что заметка в новом экспорте — это та же самая заметка, которая уже экспортировалась раньше.

Это важно для FlowLogue, поскольку позволяет строить нормальную дедупликацию и в будущем — инкрементальное обновление, вместо повторного создания одинаковых заметок при каждом импорте.

### Структура папок

Вложенные папки Apple Notes сохраняются.

Например:

```text
Apple Notes
└── Projects
    └── Research
        └── Example note
```

будут представлены в экспорте с тем же логическим путём внутри соответствующего аккаунта.

Экспортер отдельно определяет корневые папки и затем рекурсивно проходит вложенные. Это предотвращает повторный экспорт вложенных папок.

### Защита от дублей

Во время одного запуска exporter отслеживает ID уже обработанных заметок.

Если Apple Notes API повторно возвращает ту же заметку, второй экземпляр пропускается. Количество таких случаев записывается в статистику `manifest.json`.

### Recently Deleted

Папка **Recently Deleted** по умолчанию не экспортируется.

Количество исключённых папок также фиксируется в manifest.

### Формат экспорта

Текущая версия формата: **3**.

Структура выглядит примерно так:

```text
~/Documents/AppleNotesExport/
└── current/
    ├── manifest.json
    └── notes/
        └── <аккаунт>/
            └── <папка>/
                ├── <стабильный-ID>.html
                └── <стабильный-ID>.assets/
                    └── <файлы вложений>
```

В `manifest.json` находятся версия формата, время экспорта, статистика и список заметок с их метаданными.

### Безопасное обновление экспорта

Exporter не начинает сразу перезаписывать папку `current`.

Сначала создаётся временная staging-папка. Только после успешного создания `manifest.json` новый экспорт становится `current`.

Таким образом, ошибка или прерванный запуск с меньшей вероятностью уничтожит предыдущий успешный экспорт.

### Требования

Нужны:

- Mac с macOS;
- Apple Notes;
- заметки, доступные в приложении Notes на этом Mac;
- стандартный macOS `osascript`;
- `python3` для resolver вложений;
- разрешение macOS на управление Notes;
- Full Disk Access для Terminal/приложения, запускающего exporter;
- интернет во время установки через публичный installer.

**Не нужны:** Git, GitHub account, GitHub CLI, Node.js или Apple Developer account.

### Установка через Terminal

Выполните:

```bash
curl -fsSL https://raw.githubusercontent.com/ZunagesCo/flowlogue-public/main/tools/apple-notes-exporter/install.sh | bash
```

Утилита устанавливается в:

```text
~/Library/Application Support/AppleNotesExporter/
```

Команда запуска устанавливается как:

```text
~/.local/bin/export-notes
```

При необходимости installer автоматически добавляет `~/.local/bin` в `PATH` через `~/.zprofile`.

После установки автоматически выполняется первый экспорт.

### Последующие экспорты

Для нового экспорта достаточно выполнить:

```bash
export-notes
```

Если установка только что выполнена в уже открытом Terminal и команда ещё не определяется, откройте новое окно Terminal либо выполните:

```bash
source ~/.zprofile
```

### Разрешения macOS

При первом запуске macOS может запросить разрешение для Terminal или `osascript` на управление приложением Notes. Оно необходимо, чтобы exporter мог прочитать заметки через системный Apple Automation API. Для экспорта оригинальных media-вложений также требуется Full Disk Access для Terminal (или другого приложения, из которого запускается exporter).

При запуске скачанного `Install.command` Gatekeeper также может показать предупреждение о неизвестном разработчике: текущая версия пока распространяется без подписи Apple Developer ID и notarization.

Для оригинальных вложений **Terminal должен иметь Full Disk Access**: откройте **System Settings → Privacy & Security → Full Disk Access** и включите Terminal. Если разрешение было изменено при уже запущенном Terminal, полностью закройте Terminal и откройте его снова перед повторным `export-notes`.

### Удаление

Команда:

```bash
~/Library/Application\ Support/AppleNotesExporter/uninstall.sh
```

удаляет сам exporter и команду `export-notes`.

При этом каталог:

```text
~/Documents/AppleNotesExport/
```

**не удаляется специально**, чтобы uninstall не уничтожил уже экспортированные заметки.

### Текущие ограничения

- Оригинальные файловые/media-вложения, имеющие Apple Notes `Media` record, экспортируются в `.assets` рядом с соответствующей заметкой.
- Структурированные объекты Notes, например `com.apple.notes.table`, фиксируются в manifest как metadata-only и остаются представлены HTML заметки.
- Paper/PDF fallback-файлы экспортируются, когда активная запись Apple Notes однозначно разрешается в локальный PDF.
- Некоторые специальные объекты Notes, особенно drawings/scans и другие structured representations, всё ещё могут сохраняться только как metadata или требовать дополнительной обработки.
- Содержимое заметки сохраняется в HTML в том виде, в котором его возвращает Apple Notes automation.
- Утилита предназначена для macOS и не запускается непосредственно на iPhone/iPad.
- Downloadable installer пока не подписан и не notarized.
- Это ранняя публичная версия. При изменении формата экспорта его версия будет увеличиваться.

### Приватность

Весь экспорт выполняется локально на Mac.

Exporter читает Apple Notes через системную автоматизацию macOS и записывает результат в локальную папку `Documents`. Сам exporter не отправляет содержимое заметок в FlowLogue, GitHub или какой-либо другой удалённый сервис.

Публичность этого GitHub-репозитория **не означает публичность ваших заметок**.

### Связь с FlowLogue

Apple Notes Exporter — публичная вспомогательная утилита для FlowLogue.

Структурированный manifest предназначен для надёжного импорта Apple Notes в FlowLogue, предотвращения дублей и дальнейшего развития механизма синхронизации.

Основное приложение FlowLogue в этом публичном репозитории не распространяется.
