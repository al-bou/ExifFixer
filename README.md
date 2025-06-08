# 🗂️ Photo Renamer & Organizer

This Python script automatically **renames, timestamps, and organizes your photos and videos** based on their filenames. It uses `ExifTool` to write metadata and supports processing an entire folder tree, **in parallel**, while cleaning up unwanted files (`.xmp`, unidentified files, etc.).

---

## ✅ Features

- 🔍 Recognizes over 25 common filename patterns (WhatsApp, Android, iPhone, Google Photos, etc.)
- 🕓 Extracts the date and time from the filename and writes it to metadata:
  - `DateTimeOriginal`
  - `CreateDate`
  - `ModifyDate`
- 🏷️ Renames files to format: `YYYY-MM-DD_HH-MM-SS.ext`
- 📁 Preserves the original folder structure in the output folders
- 🧹 Automatically deletes `.xmp` sidecar files
- ❓ Moves unrecognized files to a separate `unmatched/` folder
- 🚀 Parallel processing using `ThreadPoolExecutor` for speed

---

## 📂 Folder Structure

- **Source**: `F:/Run/Fotos`
- **Processed**: `F:/Run/processed_full`
- **Unmatched**: `F:/Run/unmatched`

Original folder paths are mirrored in the output folders.

---

## 🔧 Requirements

- Python 3.8+
- [ExifTool](https://exiftool.org/) installed and available in system `PATH`
- Python libraries:
  - `tqdm`
  - `pathlib`, `re`, `shutil`, `subprocess`, `concurrent.futures` (standard)

### Install Python dependency:

```bash
pip install tqdm


### Usage
````bash
python script.py
```

The script will:

1. Recursively scan all files (excluding .xmp) in F:/Run/Fotos
2. Match known date patterns from filenames
3. Write metadata using ExifTool (if EXECUTER_EXIFTOOL = True)
4. Rename and move files to processed_full/
5. Move unmatched or unknown files to unmatched/

🧪 Testing (Limit File Count)
To process only a sample of files during testing, you can limit the number processed by editing this line:

````python
fichiers = fichiers[:100]  # Only process first 100 files
```

### 🧠 Supported Filenames (Examples)
- IMG_20211202_0938_0861.jpg
- VID-20180829-WA0050.mp4
- 20220404_14380750.jpg
- 23-07-23 13-54-31 DB2F.jpg
- 2014-11-22-1323.avi
- VID20211231201335.mp4
- IMG_20220102_1004_1574.jpg
- 2007-09-14-0047 (2) (1).jpg

###⚠️ Duplicate Handling
If a renamed file already exists at the destination, a suffix is added automatically:

- 2020-01-01_12-00-00.jpg
- 2020-01-01_12-00-00 (1).jpg
- 2020-01-01_12-00-00 (2).jpg

### 🧹 Special Case Handling
.xmp sidecar files are deleted automatically.

Files with unrecognized date patterns are moved to unmatched/ for manual review.

### 📌 Roadmap (Optional Ideas)
- Add a --dry-run flag
- Generate a CSV report of renamed files
- Provide a simple web or desktop GUI
- Add logging or error summary at the end

### 📄 License
MIT License (or adapt as needed)

Author: Alan Bouo