"""
Bootstrap Installer - Kleiner Installer der nur den Downloader enthält
Lädt die eigentliche VoiceTranscriber.exe von Cloudflare R2 Storage nach.

Verwendung:
    bootstrap_installer.exe              # Mit GUI
    bootstrap_installer.exe --silent     # Silent-Mode (für NSIS)
"""

import argparse
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

    def __init__(self, silent_mode: bool = False):
        self.silent_mode = silent_mode
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
            logger.info(f"Installiere nach: {install_dir}")

            # Download durchführen
            if download_voice_transcriber(str(install_dir), raise_on_error=True):
                self.update_status("Installation erfolgreich abgeschlossen!")

                # Erfolgsmeldung
                if self.root:
                    self.root.after(1000, lambda: self.show_success_message(install_dir))
            else:
                # Sollte durch raise_on_error nicht erreicht werden, aber als Fallback
                self.update_status("Installation fehlgeschlagen!")
                if self.root:
                    self.root.after(1000, lambda: self.show_error_message("Unbekannter Fehler (Download lieferte False)"))

        except Exception as e:
            logger.error(f"Fehler während der Installation: {e}", exc_info=True)
            self.update_status("Fehler aufgetreten!")
            if self.root:
                # Entferne technische Details für User, außer sie sind wichtig
                error_msg = str(e)
                self.root.after(1000, lambda: self.show_error_message(error_msg))

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
        
        log_file = Path(os.environ.get('TEMP', '')) / "VoiceTranscriber_Bootstrap.log"
        
        error_text = "Bei der Installation ist ein Fehler aufgetreten:\n\n"
        if error:
            error_text += f"{error}\n\n"
        else:
            error_text += "Unbekannter Fehler.\n\n"
            
        error_text += "Bitte überprüfen Sie Ihre Internetverbindung.\n"
        error_text += f"Details finden Sie im Log: {log_file}"
        
        messagebox.showerror("Installationsfehler", error_text)
        if self.root:
            self.root.quit()

    def run_silent(self) -> int:
        """
        Führt Installation im Silent-Mode durch (ohne GUI)

        Returns:
            0 bei Erfolg, 1 bei Fehler
        """
        try:
            logger.info("Bootstrap-Installer startet im Silent-Mode")

            # Installationsverzeichnis bestimmen
            if getattr(sys, 'frozen', False):
                # Wir sind in einer EXE - verwende Programm-Verzeichnis
                install_dir = Path(sys.executable).parent
            else:
                # Entwicklung - verwende Standard-Programm-Verzeichnis
                install_dir = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / "Voice Transcriber"

            logger.info(f"Installationsverzeichnis: {install_dir}")
            logger.info("Lade VoiceTranscriber.exe von R2 Storage herunter...")

            # Download durchführen
            if download_voice_transcriber(str(install_dir), raise_on_error=True):
                logger.info("✅ Installation erfolgreich abgeschlossen!")
                logger.info(f"VoiceTranscriber.exe wurde nach {install_dir} installiert")
                return 0
            else:
                logger.error("❌ Installation fehlgeschlagen!")
                return 1

        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}", exc_info=True)
            return 1

    def run(self):
        """Startet den Installer"""
        if self.silent_mode:
            # Silent-Mode: Keine GUI, direkter Download
            exit_code = self.run_silent()
            sys.exit(exit_code)
        else:
            # GUI-Mode: Normale tkinter-GUI
            self.create_gui()
            if self.root:
                self.root.mainloop()

def main():
    """Haupteinstiegspunkt"""
    # Argument-Parser
    parser = argparse.ArgumentParser(description='Voice Transcriber Bootstrap Installer')
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Silent-Mode ohne GUI (für automatische Installation)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose Logging'
    )

    args = parser.parse_args()

    # Logging konfigurieren
    log_level = logging.DEBUG if args.verbose else logging.INFO
    
    # Log-Datei im Temp-Verzeichnis
    log_file = Path(os.environ.get('TEMP', '')) / "VoiceTranscriber_Bootstrap.log"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        file_handler = logging.FileHandler(str(log_file), mode='w', encoding='utf-8')
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warnung: Konnte Log-Datei nicht erstellen: {e}")

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S',
        handlers=handlers
    )
    
    logger.info(f"Logging gestartet: {log_file}")

    if args.silent:
        logger.info("Starte im Silent-Mode (keine GUI)")

    installer = BootstrapInstaller(silent_mode=args.silent)
    installer.run()

if __name__ == "__main__":
    main()