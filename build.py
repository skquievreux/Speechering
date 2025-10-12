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
        print("❌ WARNUNG: Virtual Environment nicht aktiviert!")
        print("   Bitte erst ausführen: venv\\Scripts\\activate")
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
                print(f"🧹 Gelöscht: {dir_name}/")
            except OSError as e:
                print(f"⚠️  Konnte {dir_name}/ nicht löschen: {e}")
                print("   Versuche laufende Prozesse zu beenden...")

                # Versuche VoiceTranscriber.exe zu beenden
                try:
                    subprocess.run(['taskkill', '/f', '/im', 'VoiceTranscriber.exe'],
                                 capture_output=True, timeout=10)
                    print("   ✅ Prozesse beendet, versuche erneut...")
                    shutil.rmtree(dir_path)
                    print(f"   ✅ Gelöscht: {dir_name}/")
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
                    print(f"   ❌ Konnte {dir_name}/ nicht bereinigen - bitte manuell schließen")
                    return False
    return True

def generate_icon():
    """Generiert Icon falls nicht vorhanden"""
    icon_path = Path("assets/icon.ico")
    if not icon_path.exists():
        print("🎨 Generiere Icon...")
        try:
            # Wechsle in assets Verzeichnis und führe Generator aus
            os.chdir("assets")
            subprocess.run([sys.executable, "icon_generator.py"], check=True)
            os.chdir("..")
            print("✅ Icon generiert")
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler beim Generieren des Icons: {e}")
            return False
    else:
        print("✅ Icon bereits vorhanden")
    return True

def build_exe():
    """EXE erstellen"""
    # venv-Prüfung für lokale Entwicklung überspringen
    # if not check_venv():
    #     sys.exit(1)

    print("🔨 Starte Build-Prozess...")
    print("=" * 50)

    # Cleanup
    if not clean_build():
        print("❌ Build abgebrochen - Cleanup fehlgeschlagen")
        sys.exit(1)

    # Icon generieren
    if not generate_icon():
        print("❌ Build abgebrochen - Icon-Generierung fehlgeschlagen")
        sys.exit(1)

    # Automatisch alle src-Module als Hidden Imports hinzufügen
    hidden_imports = [
        "--hidden-import=pystray._win32",  # Windows-spezifische Imports
        "--hidden-import=winsound",    # Windows Sound-API
        "--hidden-import=pydub",       # Audio-Komprimierung
        "--hidden-import=pydub.effects",  # pydub Effekte
        "--hidden-import=httpx",       # HTTP/2 Unterstützung
        "--hidden-import=requests",    # HTTP-Requests
        "--hidden-import=numpy",       # Für Audio-Verarbeitung
        "--hidden-import=pyaudio",     # Audio-Aufnahme
        "--hidden-import=keyboard",    # Hotkey-Unterstützung
        "--hidden-import=pyautogui",   # GUI-Automation
        "--hidden-import=pyperclip",   # Clipboard-Zugriff
        "--hidden-import=pillow",      # Bildverarbeitung für Tray-Icon
        # Neue Module für v1.4.0
        "--hidden-import=user_config", # Benutzerspezifische Konfiguration
        "--hidden-import=mouse_integration", # AHK-Integration
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

    print("📦 Führe PyInstaller aus...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")

    try:
        result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Build erfolgreich abgeschlossen!")
            print("📁 EXE-Datei: dist/VoiceTranscriber.exe")

            # Dateigröße anzeigen
            exe_path = Path("dist/VoiceTranscriber.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📊 Dateigröße: {size_mb:.1f} MB")

            print("\n🚀 Bereit zur Verwendung!")
            print("   Hinweis: OpenAI API-Key in .env erforderlich")

        else:
            print("❌ Build fehlgeschlagen!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller Fehler: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ PyInstaller nicht gefunden!")
        print("   Bitte installieren: pip install pyinstaller")
        sys.exit(1)

def build_installer():
    """Erstellt Windows-Installer mit NSIS"""
    print("📦 Erstelle Windows-Installer...")

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
                print(f"✅ NSIS gefunden: {path}")
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    if not nsis_path:
        print("❌ NSIS nicht gefunden!")
        print("   Bitte installiere NSIS von: https://nsis.sourceforge.io/")
        return False

    # Prüfe ob installer.nsi existiert
    installer_script = Path("installer.nsi")
    if not installer_script.exists():
        print(f"❌ Installer-Skript nicht gefunden: {installer_script}")
        return False

    # NSIS-Befehl ausführen
    nsis_cmd = [
        nsis_path,
        "/V4",  # Verbose output
        str(installer_script)
    ]

    print(f"🏗️ Führe NSIS aus: {' '.join(nsis_cmd)}")

    try:
        result = subprocess.run(nsis_cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            # Finde die erstellte Installer-Datei
            installer_files = list(Path(".").glob("VoiceTranscriber_*.exe"))
            if installer_files:
                installer_file = max(installer_files, key=lambda x: x.stat().st_mtime)
                size_mb = installer_file.stat().st_size / (1024 * 1024)
                print("✅ Installer erfolgreich erstellt!")
                print(f"📁 Installer: {installer_file}")
                print(f"📊 Größe: {size_mb:.1f} MB")
            else:
                print("✅ Installer erfolgreich erstellt!")
            return True
        else:
            print("❌ NSIS-Build fehlgeschlagen!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ NSIS Fehler: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ makensis.exe nicht gefunden")
        return False

def main():
    """Hauptfunktion"""
    print("🎤 Voice Transcriber - Build Script")
    print("=" * 50)

    # Kommandozeilen-Argumente prüfen
    build_installer_flag = "--installer" in sys.argv

    try:
        # Immer EXE bauen
        build_exe()

        # Optional Installer bauen
        if build_installer_flag:
            print("\n" + "=" * 50)
            if build_installer():
                print("\n🎉 Vollständiger Build erfolgreich!")
                print("   - EXE: dist/VoiceTranscriber.exe")
                print("   - Installer: VoiceTranscriber_Installer.exe")
            else:
                print("\n❌ Installer-Build fehlgeschlagen!")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n❌ Build durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()