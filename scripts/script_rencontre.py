from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tkinter

# =====================================================
# CHEMINS ROBUSTES
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"

# Fichier créé dynamiquement par GitHub Actions
JSON_KEYFILE = "importrencontre.json"

# =====================================================
# LECTURE CONFIG
# =====================================================
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

CLUB_ID = config["CLUB_ID"]
TEAM_IDS = {team.split("_")[1]: team for team in config["TEAM_IDS"]}

# =====================================================
# CONFIGURATION METIER
# =====================================================
SPREADSHEET_ID = "1xU4EQLRU8nWz8Wf7zHyj1zS0ZMiD83sHsRFbXF3_PA8"
SHEET_NAME = "Rencontre"
BASE_URL = (
    "https://resultats.aftt.be/?div_id={div_id}"
    "&menu=3&type=3&week_name=01&club_id={club_id}"
)

# =====================================================
# GOOGLE SHEETS AUTH
# =====================================================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
sheet.clear()

# =====================================================
# HEADERS
# =====================================================
headers = [
    "semaine",
    "début de semaine",
    "fin de semaine",
    "Anderlues",
    "score",
    "adversaire",
    "date",
    "heure",
    "domicile_bool",
    "type_match",
    "icone",
    "domicile_nom",
    "commentaire"
]
sheet.append_row(headers)

# =====================================================
# REGEX SEMAINE
# =====================================================
pattern = re.compile(
    r"Semaine\s+(\d+)\s+:\s+Du\s+(\d{2})-(\d{2})-(\d{4})\s+au\s+(\d{2})-(\d{2})-(\d{4})"
)

all_rows = []
total_teams = len(TEAM_IDS)

# =====================================================
# TRAITEMENT
# =====================================================
def run_rencontre(output=print, progress_callback=None):
    for i, (team_letter, div_id) in enumerate(TEAM_IDS.items(), 1):
        team_name = f"Anderlues {team_letter}"
        url = BASE_URL.format(div_id=div_id, club_id=CLUB_ID)

        try:
            output(f"⬇️ Téléchargement HTML équipe {team_letter}")
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            output(f"❌ Erreur téléchargement {team_letter} : {e}")
            continue

        tables = soup.find_all("table", class_="DBTable_short")
        matchs_extraits = 0

        for table in tables:
            semaine_info = table.find_previous(string=pattern)
            if not semaine_info:
                continue

            match = pattern.search(semaine_info)
            if not match:
                continue

            semaine = f"Semaine {int(match.group(1))}"

            debut = datetime.strptime(
                f"{match.group(2)}-{match.group(3)}-{match.group(4)}",
                "%d-%m-%Y"
            ).strftime("%d/%m/%Y")

            fin = datetime.strptime(
                f"{match.group(5)}-{match.group(6)}-{match.group(7)}",
                "%d-%m-%Y"
            ).strftime("%d/%m/%Y")

            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) < 4:
                    continue

                date_heure = cells[1].text.strip()
                equipe_local = cells[2].text.strip()
                equipe_visiteur = cells[3].text.strip()

                if team_name not in (equipe_local, equipe_visiteur):
                    continue

                domicile = "TRUE" if equipe_local == team_name else "FALSE"
                adversaire = equipe_visiteur if domicile == "TRUE" else equipe_local

                type_match = "Domicile" if domicile == "TRUE" else "Déplacement"
                icone = "🏠" if domicile == "TRUE" else "🚗"
                domicile_nom = "Anderlues" if domicile == "TRUE" else ""

                try:
                    date_str, heure_str = date_heure.split("/")
                    date_match = datetime.strptime(
                        date_str.strip()[3:], "%d-%m-%y"
                    ).strftime("%d/%m/%Y")
                    heure_match = heure_str.strip().replace("\xa0", "").replace("**", "")
                except Exception:
                    date_match = ""
                    heure_match = ""

                ligne = [
                    semaine,
                    debut,
                    fin,
                    team_name,
                    "0 - 0",
                    adversaire,
                    date_match,
                    heure_match,
                    domicile,
                    type_match,
                    icone,
                    domicile_nom,
                    ""
                ]

                all_rows.append(ligne)
                output(f"✔️ {semaine} : {team_name} vs {adversaire}")
                matchs_extraits += 1
                break

        output(f"➡️ {matchs_extraits} match(s) extrait(s) pour {team_letter}\n")
        time.sleep(1.5)

        if progress_callback:
            progress_callback(i / total_teams)
            try:
                tkinter._default_root.update_idletasks()
            except Exception:
                pass

    try:
        sheet.append_rows(all_rows, value_input_option="USER_ENTERED")
        output(f"✅ {len(all_rows)} lignes envoyées à Google Sheets.")
    except Exception as e:
        output(f"❌ Erreur Google Sheets : {e}")


# =====================================================
# MAIN
# =====================================================
def main(output=print, progress_callback=None):
    run_rencontre(output=output, progress_callback=progress_callback)


if __name__ == "__main__":
    main()
