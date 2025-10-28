"""
Bootstrap Installer - Kleiner Installer der nur den Downloader enthält
Lädt die eigentliche VoiceTranscriber.exe von Cloudflare R2 Storage nach.
"""

import logging
import os
import sys
import threading
from pathlib import Path
from tkinter import Tk, messagebox, ttk
from typing import Optional

# Füge src zum Pfad hinzu für lokale Entwicklung
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.downloader import (download_update_package,
                                download_voice_transcriber)
except ImportError:
    # Fallback für direkte Ausführung
    try:
        from downloader import (download_update_package,
                                download_voice_transcriber)
    except ImportError:
        print("Fehler: Downloader-Modul nicht gefunden!")
        sys.exit(1)

logger = logging.getLogger(__name__)

class BootstrapInstaller:
    """Bootstrap-Installer für Voice Transcriber"""

    def __init__(self):
        self.root = None
        self.progress_var = None
        self.status_label = None
        self.install_thread = None

    def create_gui(self):
        """Erstellt die Installer-GUI"""
        self.root = Tk()
        self.root.title("Voice Transcriber - Installation")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        # Icon setzen falls verfügbar
        try:
            icon_path = Path(__file__).parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass

        # Titel
        title_label = ttk.Label(self.root, text="Voice Transcriber Installation",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Status-Label
        self.status_label = ttk.Label(self.root, text="Bereite Installation vor...")
        self.status_label.pack(pady=5)

        # Fortschrittsbalken
        self.progress_var = ttk.Progressbar(self.root, orient="horizontal",
                                          length=300, mode="indeterminate")
        self.progress_var.pack(pady=10)
        self.progress_var.start()

        # Start-Button
        start_button = ttk.Button(self.root, text="Installation starten",
                                command=self.start_installation)
        start_button.pack(pady=10)

        # Center window
        self.root.eval('tk::PlaceWindow . center')

    def start_installation(self):
        """Startet die Installation in einem separaten Thread"""
        self.install_thread = threading.Thread(target=self.perform_installation, daemon=True)
        self.install_thread.start()

    def perform_installation(self):
        """Führt die eigentliche Installation durch"""
        try:
            self.update_status("Ermittle Installationsverzeichnis...")

            # Installationsverzeichnis bestimmen
            if getattr(sys, 'frozen', False):
                # Wir sind in einer EXE - verwende Programm-Verzeichnis
                install_dir = Path(sys.executable).parent
            else:
                # Entwicklung - verwende Standard-Programm-Verzeichnis
                install_dir = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / "Voice Transcriber"

            self.update_status("Lade VoiceTranscriber.exe herunter...")

            # Download durchführen
            if download_voice_transcriber(str(install_dir)):
                self.update_status("Installation erfolgreich abgeschlossen!")

                # Erfolgsmeldung
                if self.root:
                    self.root.after(1000, lambda: self.show_success_message(install_dir))
            else:
                self.update_status("Installation fehlgeschlagen!")
                if self.root:
                    self.root.after(1000, lambda: self.show_error_message())

        # Exception handling wird bereits in der äußeren try-except behandelt

        except Exception as e:
            logger.error(f"Fehler während der Installation: {e}")
            self.update_status("Unerwarteter Fehler!")
            if self.root:
                self.root.after(1000, lambda: self.show_error_message(str(e)))

    def update_status(self, text: str):
        """Aktualisiert den Status-Text"""
        if self.status_label and self.root:
            self.status_label.config(text=text)
            self.root.update_idletasks()

    def show_success_message(self, install_dir: Path):
        """Zeigt Erfolgsmeldung"""
        if self.progress_var:
            self.progress_var.stop()
        messagebox.showinfo("Installation erfolgreich",
                          f"Voice Transcriber wurde erfolgreich installiert in:\n\n{install_dir}\n\n"
                          "Sie können die Anwendung jetzt starten.")
        if self.root:
            self.root.quit()

    def show_error_message(self, error: Optional[str] = None):
        """Zeigt Fehlermeldung"""
        if self.progress_var:
            self.progress_var.stop()
        error_text = f"Bei der Installation ist ein Fehler aufgetreten:\n\n{error}" if error else \
                    "Bei der Installation ist ein Fehler aufgetreten.\n\n" \
                    "Bitte überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut."
        messagebox.showerror("Installationsfehler", error_text)
        if self.root:
            self.root.quit()

    def run(self):
        """Startet den Installer"""
        self.create_gui()
        if self.root:
            self.root.mainloop()

def main():
    """Haupteinstiegspunkt"""
    # Logging konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    installer = BootstrapInstaller()
    installer.run()

if __name__ == "__main__":
    main()