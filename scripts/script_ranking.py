from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"
CREDS_PATH = BASE_DIR / "importrencontre-e0ccf9e96240.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

CLUB_ID = config["CLUB_ID"]
TEAM_IDS = {team.split("_")[1]: team for team in config["TEAM_IDS"]}

JSON_KEYFILE = str(CREDS_PATH)
SPREADSHEET_ID = "1xU4EQLRU8nWz8Wf7zHyj1zS0ZMiD83sHsRFbXF3_PA8"
SHEET_NAME = "RANKING"
SEMAINE = "22"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
sheet.clear()

headers = [
    "Place", "Nom équipe", "Score",
    "RJ", "RG", "RP", "RN", "FF",
    "MG", "MP", "SG", "SP", "Division"
]
sheet.append_row(headers)

for letter, div_id in TEAM_IDS.items():
    url = (
        f"https://resultats.aftt.be/?div_id={div_id}"
        f"&menu=5&withres=1&week_name={SEMAINE}"
        f"&divcat=0&club_id={CLUB_ID}"
    )

    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    div_td = soup.find("td", class_="interclubs_title")
    division = div_td.get_text(strip=True).split(" -")[0] if div_td else f"Division {letter}"

    rows = soup.find_all("tr", class_="DBTable")
    all_rows = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 12:
            continue

        all_rows.append([
            cols[0].text.strip(),
            cols[1].text.strip(),
            cols[11].text.strip(),
            cols[2].text.strip(),
            cols[3].text.strip(),
            cols[4].text.strip(),
            cols[5].text.strip(),
            cols[6].text.strip(),
            cols[7].text.strip(),
            cols[8].text.strip(),
            cols[9].text.strip(),
            cols[10].text.strip(),
            division
        ])

    sheet.append_rows(all_rows, value_input_option="USER_ENTERED")
    time.sleep(5)

print("✅ Classements standard mis à jour")
