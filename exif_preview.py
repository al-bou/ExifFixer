import re
from pathlib import Path
import shutil
import subprocess


# === Configuration ===
DOSSIER_PHOTOS = Path("F:\Run/2019/03")  # adapte ce chemin à ton cas
DOSSIER_TRAITES = Path("F:/Run/processed")       # Dossier où déplacer les fichiers traités
EXECUTER_EXIFTOOL = True  # True pour appliquer, False pour dry-run
DOSSIER_NON_IDENTIFIES = Path("F:/Run/unmatched")
DOSSIER_NON_IDENTIFIES.mkdir(parents=True, exist_ok=True)


regex_patterns = [
    # IMG_20181126_153131-UUID.jpg
    (re.compile(r"IMG_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})-*[\w-]*\.jpe?g", re.IGNORECASE), "long"),

    # 2020-01-20-1210_1-UUID.jpg
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})_\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "short"),

    # 23-01-28 08-02-43 7507-UUID.jpg
    (re.compile(r"(\d{2})-(\d{2})-(\d{2})[ -_](\d{2})-(\d{2})-(\d{2}) \d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "short2"),

    # 23-06-22 07-25-23 e.pn-UUID.jpg
    (re.compile(r"(\d{2})-(\d{2})-(\d{2})[ _](\d{2})-(\d{2})-(\d{2}) [\w.\- ]+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "short3"),
    
    (re.compile(r"IMG_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})_\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "img_partial"),

    (re.compile(r"IMG-(\d{4})(\d{2})(\d{2})-WA\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "wa"),

    (re.compile(r".*?(\d{2})(\d{2})(\d{4})-\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "ddmmyyyy"),

    (re.compile(r"signal-(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})_\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "signal"),

    (re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\d{2}-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "android8"),

    (re.compile(r"(?:IMG|SAVE)_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?: \(\d+\))?-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "long"),

    (re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.(?:jpe?g|png|mp4)", re.IGNORECASE), "android_simple"),

    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})\.(?:jpe?g|png|mp4)", re.IGNORECASE), "date_dash_time"),

    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})_\d+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "date_dash_time_suffix"),

    (re.compile(r"(?:IMG|SAVE)_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.(?:jpe?g|png|mp4)", re.IGNORECASE), "long_simple"),

    (re.compile(r"^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?: ?\(\d+\))*\.(?:jpe?g|png|mp4)$", re.IGNORECASE), "android_dup"),


]   

# === S'assurer que le dossier de destination existe
DOSSIER_TRAITES.mkdir(parents=True, exist_ok=True)

def nom_disponible(destination: Path) -> Path:
    if not destination.exists():
        return destination

    base = destination.stem
    ext = destination.suffix
    compteur = 1

    while True:
        nouveau_nom = f"{base} ({compteur}){ext}"
        candidat = destination.parent / nouveau_nom
        if not candidat.exists():
            return candidat
        compteur += 1

# === Traitement
print("📂 Début du traitement...\n")
compteur = 0
stop_iter = 1000
for fichier in DOSSIER_PHOTOS.iterdir():
    # Supprimer les fichiers .xmp (fichiers de métadonnées inutiles pour Immich)
    if fichier.suffix.lower() == ".xmp":
        print(f"🗑️ Suppression du fichier XMP : {fichier.name}")
        fichier.unlink()  # supprime le fichier
        continue  # passe au fichier suivant

    compteur += 1
    if compteur > stop_iter:
        print("📂 Sortie du traitement...\n")
        break
    else:
        print(f"▶️ [{compteur}/{stop_iter}] Traitement : {fichier.name}")
    if not fichier.is_file():
        continue
    traité = False

    for pattern, type_nom in regex_patterns:
        match = pattern.match(fichier.name)
        if match:
            # Extraire la date
            if type_nom == "long":
                yyyy, mm, dd, HH, MM, SS = match.groups()
            elif type_nom == "short":
                yyyy, mm, dd, HH, MM = match.groups()
                SS = "00"
            elif type_nom == "short2":
                yy, mm, dd, HH, MM, SS = match.groups()
                yyyy = "20" + yy  # Convertir année 2 chiffres en 4
            elif type_nom == "short3":
                yy, mm, dd, HH, MM, SS = match.groups()
                yyyy = "20" + yy
            elif type_nom == "img_partial":
                yyyy, mm, dd, HH, MM = match.groups()
                SS = "00"
            elif type_nom == "wa":
                yyyy, mm, dd = match.groups()
                HH = MM = SS = "00"
            
            elif type_nom == "ddmmyyyy":
                dd, mm, yyyy = match.groups()
                HH = MM = SS = "00"

            elif type_nom == "signal":
                yyyy, mm, dd, HH, MM, SS = match.groups()

            elif type_nom == "android8":
                yyyy, mm, dd, HH, MM, SS = match.groups()

            elif type_nom == "long":
                yyyy, mm, dd, HH, MM, SS = match.groups()

            elif type_nom == "android_simple":
                yyyy, mm, dd, HH, MM, SS = match.groups()

            elif type_nom == "date_dash_time":
                yyyy, mm, dd, HH, MM, SS = match.groups()


            elif type_nom == "date_dash_time_suffix":
                yyyy, mm, dd, HH, MM, SS = match.groups()

            elif type_nom == "long_simple":
                yyyy, mm, dd, HH, MM, SS = match.groups()

            elif type_nom == "android_dup":
                yyyy, mm, dd, HH, MM, SS = match.groups()




            date_exif = f"{yyyy}:{mm}:{dd} {HH}:{MM}:{SS}"
            print(f"🔧 {fichier.name} → Date EXIF : {date_exif}")

            if EXECUTER_EXIFTOOL:
                cmd = [
                    "exiftool",
                    f"-DateTimeOriginal={date_exif}",
                    f"-CreateDate={date_exif}",
                    f"-ModifyDate={date_exif}",
                    "-overwrite_original",
                    str(fichier)
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ exiftool appliqué")

                # Reconstruire un nom sans UUID
                nom_nettoye = f"{yyyy}-{mm}-{dd}_{HH}-{MM}-{SS}{fichier.suffix.lower()}"

                print('nom nettoyé : '+nom_nettoye)
                destination_brut = DOSSIER_TRAITES / nom_nettoye
                destination = nom_disponible(destination_brut)
                shutil.move(str(fichier), destination)
                print(f"📁 Fichier déplacé vers : {destination}\n")
            traité = True
            break
    if not traité:
        destination = nom_disponible(DOSSIER_NON_IDENTIFIES / fichier.name)
        if fichier.exists():
            shutil.move(str(fichier), destination)
            print(f"❓ Aucun format reconnu → déplacé vers : {destination}\n")
        else:
            print(f"⚠️ Fichier introuvable (déjà déplacé ?) : {fichier}")