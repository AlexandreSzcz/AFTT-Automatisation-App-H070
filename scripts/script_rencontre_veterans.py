import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import tkinter

# =====================================================
# CHEMINS SIMPLES (COMME AVANT)
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"
JSON_KEYFILE = BASE_DIR / "importrencontre-e0ccf9e96240.json"

# =====================================================
# CONFIG
# =====================================================
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

CLUB_ID = config["CLUB_ID"]
TEAM_IDS = {team.split("_")[1]: team for team in config["TEAM_IDS_VETERANS"]}

# =====================================================
# GOOGLE SHEETS
# =====================================================
SPREADSHEET_ID = "1xU4EQLRU8nWz8Wf7zHyj1zS0ZMiD83sHsRFbXF3_PA8"
SHEET_NAME = "Rencontre VETERANS"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    str(JSON_KEYFILE), scope
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
sheet.clear()

# =====================================================
# HEADERS
# =====================================================
headers = [
    "semaine", "début de semaine", "fin de semaine",
    "Anderlues", "score", "adversaire",
    "date", "heure",
    "domicile_bool", "type_match",
    "icone", "domicile_nom", "commentaire"
]
sheet.append_row(headers)

# =====================================================
# EXTRACTION
# =====================================================
BASE_URL = (
    "https://resultats.aftt.be/?div_id={div_id}"
    "&menu=3&type=3&week_name=01&club_id={club_id}"
)

pattern = re.compile(
    r"Semaine\s+(\d+)\s+:\s+Du\s+(\d{2})-(\d{2})-(\d{4})\s+au\s+(\d{2})-(\d{2})-(\d{4})"
)

all_rows = []

for team_letter, div_id in TEAM_IDS.items():
    team_name = f"Anderlues {team_letter}"
    url = BASE_URL.format(div_id=div_id, club_id=CLUB_ID)

    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    tables = soup.find_all("table", class_="DBTable_short")

    for table in tables:
        semaine_info = table.find_previous(string=pattern)
        if not semaine_info:
            continue

        match = pattern.search(semaine_info)
        if not match:
            continue

        semaine = f"Semaine {match.group(1)}"
        debut = f"{match.group(2)}/{match.group(3)}/{match.group(4)}"
        fin = f"{match.group(5)}/{match.group(6)}/{match.group(7)}"

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
                heure_match = heure_str.strip()
            except:
                date_match = ""
                heure_match = ""

            all_rows.append([
                semaine, debut, fin,
                team_name, "0 - 0", adversaire,
                date_match, heure_match,
                domicile, type_match,
                icone, domicile_nom, ""
            ])
            break

    time.sleep(1)

sheet.append_rows(all_rows, value_input_option="USER_ENTERED")
print("✅ Rencontres vétérans mises à jour")
