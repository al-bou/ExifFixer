# ExifFixer

📸 Script Python pour corriger automatiquement les métadonnées EXIF de vos photos et vidéos, à partir du nom de fichier.

## 🚀 Objectif

Quand les photos sont exportées, transférées ou récupérées depuis différentes apps ou services (WhatsApp, Signal, Android, etc.), elles perdent souvent leurs métadonnées de date/heure d’origine.  
`ExifFixer` analyse les noms de fichiers pour en extraire la date et l’heure, et réinjecte ces informations dans les champs EXIF (`DateTimeOriginal`, `CreateDate`, `ModifyDate`), grâce à [ExifTool](https://exiftool.org/).

## 🔧 Fonctionnalités

- Reconnaît plus de 15 formats de noms de fichiers issus de téléphones ou applications diverses.
- Applique les dates EXIF extraites via `exiftool`.
- Renomme les fichiers au format `YYYY-MM-DD_HH-MM-SS.jpg`.
- Gère les doublons (`photo (1).jpg`, `photo (2).jpg`...).
- Déplace les fichiers traités dans un dossier cible.
- Archive les fichiers non reconnus dans un dossier séparé.

## 📁 Structure des dossiers (à adapter)

```bash
F:/Run/2019/03           # Dossier source contenant les fichiers à traiter
F:/Run/processed         # Dossier destination des fichiers traités
F:/Run/unmatched         # Dossier des fichiers dont le nom est non reconnu
