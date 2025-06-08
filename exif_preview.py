import re
from pathlib import Path
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm



# === Configuration ===
DOSSIER_PHOTOS = Path("F:/Run/Fotos")  # adapte ce chemin à ton cas
DOSSIER_TRAITES = Path("F:/Run/processed_full")       # Dossier où déplacer les fichiers traités
EXECUTER_EXIFTOOL = True  # True pour appliquer, False pour dry-run
DOSSIER_NON_IDENTIFIES = Path("F:/Run/unmatched")
# Créer les dossiers de destination si besoin
DOSSIER_TRAITES.mkdir(parents=True, exist_ok=True)
DOSSIER_NON_IDENTIFIES.mkdir(parents=True, exist_ok=True)


regex_patterns = [
    # IMG_20181126_153131-UUID.jpg
    (re.compile(r"IMG_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?: \(\d+\))?\.jpe?g", re.IGNORECASE), "long"),


    # 2020-01-20-1210_1-UUID.jpg
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})_\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "short"),

    # 23-01-28 08-02-43 7507-UUID.jpg
    (re.compile(r"(\d{2})-(\d{2})-(\d{2})[ -_](\d{2})-(\d{2})-(\d{2}) \d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "short2"),

    # 23-06-22 07-25-23 e.pn-UUID.jpg
    (re.compile(r"(\d{2})-(\d{2})-(\d{2})[ _](\d{2})-(\d{2})-(\d{2}) [\w.\- ]+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "short3"),
    
    (re.compile(r"IMG_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})_\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "img_partial"),

    (re.compile(r"IMG-(\d{4})(\d{2})(\d{2})-WA\d+(?:-[\w-]+)?\.(?:jpe?g|png|mp4)", re.IGNORECASE), "wa"),

    (re.compile(r".*?(\d{2})(\d{2})(\d{4})-\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "ddmmyyyy"),

    (re.compile(r"signal-(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})_\d+-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "signal"),

    (re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\d{2}-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "android8"),

    (re.compile(r"(?:IMG|SAVE)_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?: \(\d+\))?-[\w-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "long"),

    (re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.(?:jpe?g|png|mp4)", re.IGNORECASE), "android_simple"),

    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})\.(?:jpe?g|png|mp4)", re.IGNORECASE), "date_dash_time"),

    (re.compile(r"(?:IMG|SAVE)_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.(?:jpe?g|png|mp4)", re.IGNORECASE), "long_simple"),

    (re.compile(r"^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?: ?\(\d+\))*\.(?:jpe?g|png|mp4)$", re.IGNORECASE), "android_dup"),

    (re.compile(r"(\d{2})-(\d{2})-(\d{2}) (\d{2})-(\d{2})-(\d{2}) -\d+-\.(?:jpe?g|png|mp4)", re.IGNORECASE),"short_suffix"),
    
    (re.compile(r"VID_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.(?:mp4|mov)", re.IGNORECASE),"vid"),
    (re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})_\d+\.(?:jpe?g|png)", re.IGNORECASE),"android_suffix"),
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(?: \(\d+\))?\.(?:jpe?g|png|mp4|tiff?)", re.IGNORECASE), "date_short_time"),
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(?: \(\d+\))*\.(?:jpe?g|png|mp4)", re.IGNORECASE), "date_dash_time_dup"),

    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})\.(?:jpe?g|png|mp4|mov|avi)", re.IGNORECASE), "date_dash_time_nominal"),

    (re.compile(r"(\d{2})-(\d{2})-(\d{2})[ _-](\d{2})-(\d{2})-(\d{2}) \w+\.(?:jpe?g|png|mp4|mov|avi|tiff)", re.IGNORECASE), "short4"),

    (re.compile(r"IMG_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?: ?\(\d+\))?\.(?:jpe?g|png|mp4)", re.IGNORECASE), "long_dup"),
    (re.compile(r"(\d{2})-(\d{2})-(\d{2}) (\d{2})-(\d{2})-(\d{2}) [\w\-]+\.(?:jpe?g|png|mp4)", re.IGNORECASE), "short4_suffix"),
    (re.compile(r"VID-(\d{4})(\d{2})(\d{2})-WA\d+(?:-[\w-]+)?(?:\.(?:mp4|mov|avi))?", re.IGNORECASE), "wa_vid"),
    (re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\d{2}\.(?:jpe?g|png|mp4)", re.IGNORECASE), "android_fraction"),
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})_\d+\.(?:jpe?g|png|mp4|mov)", re.IGNORECASE), "date_dash_time_suffix"),
    (re.compile(r"(?:VID|IMG)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})\.(?:jpe?g|png|mp4|mov)", re.IGNORECASE), "prefix_compact"),
    (re.compile(r"IMG_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})_\d+\.(?:jpe?g|png)", re.IGNORECASE), "img_time_suffix"),
    (re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})_\d+\.(?:jpe?g|png)", re.IGNORECASE), "android_time_suffix"),
       

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

def traiter_fichier(fichier: Path):
    if not fichier.is_file():
        return

    if fichier.suffix.lower() == ".xmp":
        print(f"🗑️ Suppression du fichier XMP : {fichier.name}")
        fichier.unlink()
        return

    chemin_relatif = fichier.relative_to(DOSSIER_PHOTOS)

    for pattern, type_nom in regex_patterns:
        match = pattern.match(fichier.name)
        if match:
            try:
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

                elif type_nom == "long_simple":
                    yyyy, mm, dd, HH, MM, SS = match.groups()

                elif type_nom == "android_dup":
                    yyyy, mm, dd, HH, MM, SS = match.groups()
                elif type_nom == "short_suffix":
                    yy, mm, dd, HH, MM, SS = match.groups()
                    yyyy = "20" + yy
                elif type_nom == "vid":
                    yyyy, mm, dd, HH, MM, SS = match.groups()
                elif type_nom == "android_suffix":
                    yyyy, mm, dd, HH, MM, SS = match.groups()
                elif type_nom == "date_short_time":
                    yyyy, mm, dd, HH, MM = match.groups()
                    SS = "00"
                elif type_nom == "short4":
                    yy, mm, dd, HH, MM, SS = match.groups()
                    yyyy = "20" + yy
                elif type_nom == "date_dash_time_suffix":
                    yyyy, mm, dd, HH, MM, SS = match.groups()

                elif type_nom == "date_dash_time_suffix_nominal":
                    yyyy, mm, dd, HH, MM = match.groups()
                    SS = "00"
                elif type_nom == "date_dash_time_dup":
                    yyyy, mm, dd, HH, MM = match.groups()
                    SS = "00"

                elif type_nom == "date_dash_time_nominal":
                    yyyy, mm, dd, HH, MM = match.groups()
                    SS = "00"
                elif type_nom == "short4":
                    yy, mm, dd, HH, MM, SS = match.groups()
                    yyyy = "20" + yy  # conversion 2 chiffres vers 4 chiffres
                elif type_nom == "long_dup":
                    yyyy, mm, dd, HH, MM, SS = match.groups()
                elif type_nom == "short4_suffix":
                    yy, mm, dd, HH, MM, SS = match.groups()
                    yyyy = "20" + yy
                elif type_nom == "wa_vid":
                    yyyy, mm, dd = match.groups()
                    HH = MM = SS = "00"
                elif type_nom == "android_fraction":
                    yyyy, mm, dd, HH, MM, SS = match.groups()

                elif type_nom == "prefix_compact":
                    yyyy, mm, dd, HH, MM, SS = match.groups()
                elif type_nom == "img_time_suffix":
                    yyyy, mm, dd, HH, MM = match.groups()
                    SS = "00"
                elif type_nom == "android_time_suffix":
                        yyyy, mm, dd, HH, MM = match.groups()
                        SS = "00"


                else:
                    print(f"❌ Type de nom inconnu pour {fichier.name}")
                    return  # skip if type_nom not handled
            
                date_exif = f"{yyyy}:{mm}:{dd} {HH}:{MM}:{SS}"
                nom_nettoye = f"{yyyy}-{mm}-{dd}_{HH}-{MM}-{SS}{fichier.suffix.lower()}"

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

                destination_brut = DOSSIER_TRAITES / chemin_relatif.parent / nom_nettoye
                destination = nom_disponible(destination_brut)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(fichier), destination)
                print(f"✅ {fichier.name} → {destination}")
                return
            except ValueError as ve:
                print(f"❌ Erreur {fichier.name} / {type_nom} : {ve}")
                print(f"   Groupes extraits pour {type_nom} : {match.groups()}")
                break
            except Exception as e:
                print(f"❌ Erreur {fichier.name} : {e}")
                return

    # non reconnu
    destination = nom_disponible(DOSSIER_NON_IDENTIFIES / chemin_relatif)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(fichier), destination)
    print(f"❓ {fichier.name} → déplacé vers unmatched")

# === Lancement parallèle ===
if __name__ == "__main__":
    fichiers = [
        f for f in DOSSIER_PHOTOS.rglob("*")
        if f.is_file() and f.suffix.lower() != ".xmp"
    ]
    with ThreadPoolExecutor(max_workers=16) as executor:
        list(tqdm(executor.map(traiter_fichier, fichiers), total=len(fichiers)))