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
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"🧹 Gelöscht: {dir_name}/")

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
    clean_build()

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

def main():
    """Hauptfunktion"""
    print("🎤 Voice Transcriber - Build Script")
    print("=" * 50)

    try:
        build_exe()
    except KeyboardInterrupt:
        print("\n❌ Build durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()