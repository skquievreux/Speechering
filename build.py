"""
Build Script - Erstellt Standalone EXE mit PyInstaller
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_venv():
    """Prüft ob Virtual Environment aktiv ist"""
    if not hasattr(sys, 'real_prefix') and not (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        print("WARNUNG: Virtual Environment nicht aktiviert!")
        print("   Bitte erst ausfuehren: venv\\Scripts\\activate")
        return False
    return True

def clean_build():
    """Alte Builds löschen"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"Geloescht: {dir_name}/")
            except OSError as e:
                print(f"WARNUNG: Konnte {dir_name}/ nicht loeschen: {e}")
                print("   Versuche laufende Prozesse zu beenden...")

                # Versuche VoiceTranscriber.exe zu beenden
                try:
                    subprocess.run(['taskkill', '/f', '/im', 'VoiceTranscriber.exe'],
                                 capture_output=True, timeout=10)
                    print("   Prozesse beendet, versuche erneut...")
                    shutil.rmtree(dir_path)
                    print(f"   Geloescht: {dir_name}/")
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
                    print(f"   Konnte {dir_name}/ nicht bereinigen - bitte manuell schliessen")
                    return False
    return True

def generate_icon():
    """Generiert Icon falls nicht vorhanden"""
    icon_path = Path("assets/icon.ico")
    if not icon_path.exists():
        print("Generiere Generiere Icon...")
        try:
            # Wechsle in assets Verzeichnis und führe Generator aus
            os.chdir("assets")
            subprocess.run([sys.executable, "icon_generator.py"], check=True)
            os.chdir("..")
            print("OK: Icon generiert")
        except subprocess.CalledProcessError as e:
            print(f"FEHLER: Fehler beim Generieren des Icons: {e}")
            return False
    else:
        print("OK: Icon bereits vorhanden")
    return True

def build_exe():
    """EXE erstellen"""
    # venv-Prüfung für lokale Entwicklung überspringen
    # if not check_venv():
    #     sys.exit(1)

    print("Starte Starte Build-Prozess...")
    print("=" * 50)

    # Cleanup
    if not clean_build():
        print("FEHLER: Build abgebrochen - Cleanup fehlgeschlagen")
        sys.exit(1)

    # Icon generieren
    if not generate_icon():
        print("FEHLER: Build abgebrochen - Icon-Generierung fehlgeschlagen")
        sys.exit(1)

    # Automatisch alle src-Module als Hidden Imports hinzufügen
    hidden_imports = [
        "--hidden-import=version_manager",  # Version Management
        "--hidden-import=version_manager",  # Version Management
        "--hidden-import=pystray._win32",  # Windows-spezifische Imports
        "--hidden-import=winsound",    # Windows Sound-API
        "--hidden-import=pydub",       # Audio-Komprimierung
        "--hidden-import=pydub.effects",  # pydub Effekte
        "--hidden-import=httpx",       # HTTP/2 Unterstützung
        "--hidden-import=requests",    # HTTP-Requests
        "--hidden-import=numpy",       # Für Audio-Verarbeitung
        "--hidden-import=pyaudio",     # Audio-Aufnahme
        "--hidden-import=audioop",     # Audio-Verarbeitung (pyaudioop)
        "--hidden-import=keyboard",    # Hotkey-Unterstützung
        "--hidden-import=pyautogui",   # GUI-Automation
        "--hidden-import=pyperclip",   # Clipboard-Zugriff
        "--hidden-import=pillow",      # Bildverarbeitung für Tray-Icon
        # Neue Module für v1.4.1
        "--hidden-import=user_config", # Benutzerspezifische Konfiguration
        "--hidden-import=mouse_integration", # AHK-Integration
        "--hidden-import=version_manager", # Versionsverwaltung
    ]

    # Alle src-Module automatisch hinzufügen
    import os
    src_dir = Path("src")
    if src_dir.exists():
        for py_file in src_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                module_name = f"src.{py_file.stem}"
                hidden_imports.append(f"--hidden-import={module_name}")

    # PyInstaller-Befehl
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Einzelne EXE-Datei
        "--windowed",                  # Kein Konsolenfenster
        "--icon=assets/icon.ico",      # Icon für EXE
        "--name=VoiceTranscriber",     # Name der EXE
        "--add-data=assets;assets",    # Assets einbinden
        "--add-data=scripts;scripts",  # AHK-Skript einbinden
        "--add-data=MOUSE_WHEEL_README.md;.",  # Dokumentation einbinden
        "--paths=src",                 # src-Verzeichnis zum Python-Pfad hinzufügen
        # ffmpeg ist bereits im PATH verfügbar - kein Bündeln nötig
    ] + hidden_imports + [
        "main_exe.py"                  # Einstiegspunkt (PyInstaller-optimiert)
    ]

    print("Build: Führe PyInstaller aus...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")

    try:
        result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("OK: Build erfolgreich abgeschlossen!")
            print("Datei: EXE-Datei: dist/VoiceTranscriber.exe")

            # Dateigröße anzeigen
            exe_path = Path("dist/VoiceTranscriber.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"Groesse: Dateigröße: {size_mb:.1f} MB")

            print("\nBereit: Bereit zur Verwendung!")
            print("   Hinweis: OpenAI API-Key in .env erforderlich")

        else:
            print("FEHLER: Build fehlgeschlagen!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"FEHLER: PyInstaller Fehler: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("FEHLER: PyInstaller nicht gefunden!")
        print("   Bitte installieren: pip install pyinstaller")
        sys.exit(1)

def build_bootstrap_installer():
    """Erstellt kleinen Bootstrap-Installer"""
    print("Build: Erstelle Bootstrap-Installer...")

    # PyInstaller-Befehl für Bootstrap-Installer
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Einzelne EXE-Datei
        "--windowed",                  # Kein Konsolenfenster
        "--icon=assets/icon.ico",      # Icon für EXE
        "--name=BootstrapInstaller",   # Name der EXE
        "--add-data=assets;assets",    # Assets einbinden
        "--hidden-import=src.downloader",  # Downloader-Modul
        "--hidden-import=urllib.request",   # HTTP-Requests
        "--hidden-import=urllib.error",     # HTTP-Fehlerbehandlung
        "--hidden-import=ssl",              # SSL für HTTPS
        "--hidden-import=hashlib",          # Hashing für Verifikation
        "bootstrap_installer.py"      # Einstiegspunkt
    ]

    print("Build: Führe PyInstaller für Bootstrap-Installer aus...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")

    try:
        result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("OK: Bootstrap-Installer erfolgreich erstellt!")

            # Dateigröße anzeigen
            exe_path = Path("dist/BootstrapInstaller.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"Datei: Bootstrap-Installer: {exe_path}")
                print(f"Groesse: Größe: {size_mb:.1f} MB")

                # Kopiere Bootstrap-Installer als Standard-Installer
                bootstrap_installer = Path("VoiceTranscriber_Bootstrap_Installer.exe")
                try:
                    exe_path.replace(bootstrap_installer)
                    print(f"Datei: Finaler Installer: {bootstrap_installer}")
                except Exception as e:
                    print(f"WARNUNG:  Konnte Bootstrap-Installer nicht kopieren: {e}")

            print("\nBereit: Bootstrap-Installer bereit!")
            print("   Hinweis: Lädt VoiceTranscriber.exe von R2 Storage nach")

        else:
            print("FEHLER: Bootstrap-Installer Build fehlgeschlagen!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"FEHLER: PyInstaller Fehler: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("FEHLER: PyInstaller nicht gefunden!")
        print("   Bitte installieren: pip install pyinstaller")
        return False

    return True

def build_bootstrap_installer_nsis():
    """Erstellt Bootstrap-Installer mit NSIS"""
    print("Build: Erstelle Bootstrap-Installer mit NSIS...")

    # Prüfe ob NSIS verfügbar ist
    nsis_path = None
    possible_nsis_paths = [
        r'C:\Program Files\NSIS\makensis.exe',
        r'C:\Program Files (x86)\NSIS\makensis.exe',
        'makensis.exe'  # Im PATH
    ]

    for path in possible_nsis_paths:
        try:
            result = subprocess.run([path, '/VERSION'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                nsis_path = path
                print(f"OK: NSIS gefunden: {path}")
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    if not nsis_path:
        print("FEHLER: NSIS nicht gefunden!")
        print("   Bitte installiere NSIS von: https://nsis.sourceforge.io/")
        return False

    # Prüfe ob bootstrap_installer.nsi existiert
    installer_script = Path("bootstrap_installer.nsi")
    if not installer_script.exists():
        print(f"FEHLER: Bootstrap-Installer-Skript nicht gefunden: {installer_script}")
        return False

    # NSIS-Befehl ausführen
    nsis_cmd = [
        nsis_path,
        "/V4",  # Verbose output
        str(installer_script)
    ]

    print(f"NSIS: Führe NSIS aus: {' '.join(nsis_cmd)}")

    try:
        result = subprocess.run(nsis_cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            # Finde die erstellte Installer-Datei
            installer_files = list(Path(".").glob("VoiceTranscriber_Bootstrap_*.exe"))
            if installer_files:
                installer_file = max(installer_files, key=lambda x: x.stat().st_mtime)
                size_mb = installer_file.stat().st_size / (1024 * 1024)
                print("OK: Bootstrap-Installer erfolgreich erstellt!")
                print(f"Datei: Bootstrap-Installer: {installer_file}")
                print(f"Groesse: Größe: {size_mb:.1f} MB")
            else:
                print("OK: Bootstrap-Installer erfolgreich erstellt!")
            return True
        else:
            print("FEHLER: NSIS-Bootstrap-Build fehlgeschlagen!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"FEHLER: NSIS Fehler: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("FEHLER: makensis.exe nicht gefunden")
        return False

def build_installer():
    """Erstellt Windows-Installer mit NSIS"""
    print("Build: Erstelle Windows-Installer...")

    # Prüfe ob NSIS verfügbar ist
    nsis_path = None
    possible_nsis_paths = [
        r'C:\Program Files\NSIS\makensis.exe',
        r'C:\Program Files (x86)\NSIS\makensis.exe',
        'makensis.exe'  # Im PATH
    ]

    for path in possible_nsis_paths:
        try:
            result = subprocess.run([path, '/VERSION'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                nsis_path = path
                print(f"OK: NSIS gefunden: {path}")
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    if not nsis_path:
        print("FEHLER: NSIS nicht gefunden!")
        print("   Bitte installiere NSIS von: https://nsis.sourceforge.io/")
        return False

    # Prüfe ob installer.nsi existiert
    installer_script = Path("installer.nsi")
    if not installer_script.exists():
        print(f"FEHLER: Installer-Skript nicht gefunden: {installer_script}")
        return False

    # NSIS-Befehl ausführen
    nsis_cmd = [
        nsis_path,
        "/V4",  # Verbose output
        str(installer_script)
    ]

    print(f"NSIS: Führe NSIS aus: {' '.join(nsis_cmd)}")

    try:
        result = subprocess.run(nsis_cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            # Finde die erstellte Installer-Datei
            installer_files = list(Path(".").glob("VoiceTranscriber_*.exe"))
            if installer_files:
                installer_file = max(installer_files, key=lambda x: x.stat().st_mtime)
                size_mb = installer_file.stat().st_size / (1024 * 1024)
                print("OK: Installer erfolgreich erstellt!")
                print(f"Datei: Installer: {installer_file}")
                print(f"Groesse: Größe: {size_mb:.1f} MB")
            else:
                print("OK: Installer erfolgreich erstellt!")
            return True
        else:
            print("FEHLER: NSIS-Build fehlgeschlagen!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"FEHLER: NSIS Fehler: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("FEHLER: makensis.exe nicht gefunden")
        return False

def main():
    """Hauptfunktion"""
    print("Voice Transcriber - Build Script")
    print("=" * 50)

    # Kommandozeilen-Argumente prüfen
    build_installer_flag = "--installer" in sys.argv
    build_bootstrap_flag = "--bootstrap" in sys.argv
    build_bootstrap_nsis_flag = "--bootstrap-nsis" in sys.argv

    try:
        # Immer EXE bauen
        build_exe()

        # Optional Bootstrap-Installer (PyInstaller) bauen
        if build_bootstrap_flag:
            print("\n" + "=" * 50)
            if build_bootstrap_installer():
                print("\nERFOLG: Bootstrap-Installer (PyInstaller) erfolgreich!")
                print("   - Bootstrap-Installer: VoiceTranscriber_Bootstrap_Installer.exe")
            else:
                print("\nFEHLER: Bootstrap-Installer-Build fehlgeschlagen!")
                sys.exit(1)

        # Optional Bootstrap-Installer (NSIS) bauen
        if build_bootstrap_nsis_flag:
            print("\n" + "=" * 50)
            if build_bootstrap_installer_nsis():
                print("\nERFOLG: Bootstrap-Installer (NSIS) erfolgreich!")
                print("   - Bootstrap-Installer: VoiceTranscriber_Bootstrap_Installer.exe")
            else:
                print("\nFEHLER: Bootstrap-Installer-NSIS-Build fehlgeschlagen!")
                sys.exit(1)

        # Optional Vollständigen Installer bauen
        if build_installer_flag:
            print("\n" + "=" * 50)
            if build_installer():
                print("\nERFOLG: Vollständiger Build erfolgreich!")
                print("   - EXE: dist/VoiceTranscriber.exe")
                print("   - Installer: VoiceTranscriber_Installer.exe")
            else:
                print("\nFEHLER: Installer-Build fehlgeschlagen!")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nFEHLER: Build durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"FEHLER: Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()