import customtkinter as ctk
from PIL import Image
from pathlib import Path
import subprocess
import sys

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# =====================================================
# CHEMINS ROBUSTES (OBLIGATOIRES)
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
PYTHON = sys.executable
LOGO_PATH = BASE_DIR / "logo_rctt.png"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("H070 - Automatisation")
        self.geometry("700x800")
        self.resizable(False, False)

        # === Logo ===
        if LOGO_PATH.exists():
            image = ctk.CTkImage(Image.open(LOGO_PATH), size=(160, 160))
            ctk.CTkLabel(self, image=image, text="").pack(pady=(20, 10))

        # === Menu ===
        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkOptionMenu(menu_frame, values=["Modifier Config"]).pack(side="left", padx=5)
        ctk.CTkOptionMenu(menu_frame, values=["Mode clair", "Mode sombre"]).pack(side="left", padx=5)
        ctk.CTkButton(
            menu_frame,
            text="❌ Quitter",
            fg_color="red",
            command=self.quit
        ).pack(side="right", padx=5)

        # === Boutons ===
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)

        btn_font = ("Arial", 18)

        ctk.CTkButton(
            btn_frame, text="⚛ Rencontres", font=btn_font,
            width=320, height=60,
            command=lambda: self.run_script("script_rencontre.py")
        ).pack(pady=12)

        ctk.CTkButton(
            btn_frame, text="⚛ Rencontres vétérans", font=btn_font,
            width=320, height=60,
            command=lambda: self.run_script("script_rencontre_veterans.py")
        ).pack(pady=12)

        ctk.CTkButton(
            btn_frame, text="📊 Classements", font=btn_font,
            width=320, height=60,
            command=lambda: self.run_script("script_ranking.py")
        ).pack(pady=12)

        ctk.CTkButton(
            btn_frame, text="📊 Classements vétérans", font=btn_font,
            width=320, height=60,
            command=lambda: self.run_script("script_ranking_veterans.py")
        ).pack(pady=12)

        # === Console ===
        self.console = ctk.CTkTextbox(self, height=220)
        self.console.pack(pady=15, padx=20, fill="both", expand=True)
        self.console.insert("end", "🧾 Console prête.\n")

    def run_script(self, script_name):
        script_path = SCRIPTS_DIR / script_name

        self.console.insert("end", f"\n▶️ Lancement {script_name}\n")
        self.console.see("end")

        if not script_path.exists():
            self.console.insert(
                "end",
                f"❌ Script introuvable : {script_path}\n"
            )
            return

        try:
            subprocess.run(
                [PYTHON, str(script_path)],
                check=True
            )
            self.console.insert("end", "✅ Terminé avec succès\n")
        except subprocess.CalledProcessError as e:
            self.console.insert("end", f"❌ Erreur : {e}\n")


if __name__ == "__main__":
    app = App()
    app.mainloop()
