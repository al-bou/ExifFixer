# ExifFixer

📸 A Python script to automatically fix EXIF metadata (date and time) of photos and videos by extracting timestamps from the filenames.

## 🚀 Purpose

When photos are exported, transferred, or recovered from various apps or services (WhatsApp, Signal, Android, etc.), they often lose their original date/time metadata.  
`ExifFixer` scans filenames, extracts date/time information using regex patterns, and updates the EXIF fields (`DateTimeOriginal`, `CreateDate`, `ModifyDate`) using [ExifTool](https://exiftool.org/).

## 🔧 Features

- Supports over 15 common filename formats from phones and messaging apps.
- Applies EXIF metadata using `exiftool`.
- Renames files using a consistent `YYYY-MM-DD_HH-MM-SS.ext` format.
- Handles filename collisions (`photo (1).jpg`, `photo (2).jpg`, etc.).
- Moves processed files to a target folder.
- Moves unmatched files (those that don't match any pattern) to a separate folder.

## 📁 Folder Structure (customize to your setup)

```bash
F:/Run/2019/03           # Source folder with files to process
F:/Run/processed         # Destination for processed files
F:/Run/unmatched         # Destination for unrecognized files
