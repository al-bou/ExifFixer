# ExifFixer

📸 A Python script to automatically fix EXIF metadata (date and time) of photos and videos by extracting timestamps from the filenames.

## 🚀 Purpose

When photos are exported, transferred, or recovered from various apps or services (WhatsApp, Signal, Android, etc.), they often lose their original date/time metadata.  
`ExifFixer` scans filenames, extracts date/time information using regex patterns, and updates the EXIF fields (`DateTimeOriginal`, `CreateDate`, `ModifyDate`) using [ExifTool](https://exiftool.org/).

## 🔧 Features

- Supports over 15 common filename formats from phones and messaging apps.
- Recursively scans folders (including subfolders).
- Applies EXIF metadata using `exiftool`.
- Renames files using a consistent `YYYY-MM-DD_HH-MM-SS.ext` format.
- Reconstructs the original folder hierarchy in the output folder.
- Handles filename collisions (`photo (1).jpg`, `photo (2).jpg`, etc.).
- Moves processed files to a target folder (`processed/`), keeping folder structure.
- Moves unmatched files (those that don't match any pattern) to a separate folder (`unmatched/`).

## ▶️ Usage

1. Clone this repository:

```bash
git clone https://github.com/al-bou/ExifFixer.git
cd ExifFixer
```
2. Update the # === Configuration === section in the script:

- Set your input folder (DOSSIER_PHOTOS)
- Set output folder for processed files (DOSSIER_TRAITES)
- Set folder for unmatched files (DOSSIER_NON_IDENTIFIES)
- Set EXECUTER_EXIFTOOL = True to apply changes, or False for dry run.

3. Run the script:

```bash
python exif_preview.py
```