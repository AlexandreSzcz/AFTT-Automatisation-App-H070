import customtkinter as ctk
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"


class ConfigEditor(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Configuration des identifiants")
        self.geometry("900x700")
        self.configure(padx=20, pady=20)

        self.team_ids = []
        self.team_ids_veterans = []

        self.load_config()
        self.build_ui()

    def load_config(self):
        if not CONFIG_PATH.exists():
            self.config_data = {"CLUB_ID": "", "TEAM_IDS": [], "TEAM_IDS_VETERANS": []}
            return

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config_data = json.load(f)

    def build_ui(self):
        ctk.CTkLabel(self, text="Configuration des identifiants", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(self, text="CLUB_ID").pack()
        self.club_id_entry = ctk.CTkEntry(self)
        self.club_id_entry.insert(0, self.config_data.get("CLUB_ID", ""))
        self.club_id_entry.pack()

        ctk.CTkButton(self, text="💾 Sauvegarder", command=self.save_and_close).pack(pady=20)

    def save_and_close(self):
        config = {
            "CLUB_ID": self.club_id_entry.get(),
            "TEAM_IDS": self.config_data.get("TEAM_IDS", []),
            "TEAM_IDS_VETERANS": self.config_data.get("TEAM_IDS_VETERANS", [])
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        self.destroy()
