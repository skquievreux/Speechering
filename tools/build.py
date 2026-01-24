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
        print("   Bitte nutzen Sie: poetry run python tools/build.py")
        print("   Oder aktivieren Sie die Shell: poetry shell")
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

def build_exe(mode="onedir", skip_cleanup=False):
    """EXE erstellen

    Args:
        mode: 'onedir' für Verzeichnis-Modus (stabiler) oder 'onefile' für einzelne EXE
        skip_cleanup: Wenn True, wird clean_build() übersprungen (für mehrere Builds)
    """
    # venv-Prüfung für lokale Entwicklung überspringen
    # if not check_venv():
    #     sys.exit(1)

    print("Starte Starte Build-Prozess...")
    print("=" * 50)

    # Cleanup (nur wenn nicht übersprungen)
    if not skip_cleanup:
        if not clean_build():
            print("FEHLER: Build abgebrochen - Cleanup fehlgeschlagen")
            sys.exit(1)
    else:
        print("HINWEIS: Cleanup übersprungen (Multi-Build-Modus)")

    # Icon generieren
    if not generate_icon():
        print("FEHLER: Build abgebrochen - Icon-Generierung fehlgeschlagen")
        sys.exit(1)

    # Selektive Hidden Imports - nur tatsächlich benötigte Module
    hidden_imports = [
        "--hidden-import=version_manager",  # Version Management
        "--hidden-import=version_manager",  # Version Management
        # Kern-Module (immer benötigt)
        "--hidden-import=pystray._win32",  # Windows-spezifische Imports
        "--hidden-import=winsound",        # Windows Sound-API
        "--hidden-import=keyboard",        # Hotkey-Unterstützung
        "--hidden-import=pyperclip",       # Clipboard-Zugriff
        "--hidden-import=pillow",          # Bildverarbeitung für Tray-Icon

        # Audio-Verarbeitung (immer benötigt)
        "--hidden-import=pyaudio",         # Audio-Aufnahme
        "--hidden-import=audioop",         # Audio-Verarbeitung

        # Optionale Features (nur wenn verfügbar)
        "--hidden-import=pydub",           # Audio-Komprimierung (optional)
        "--hidden-import=pydub.effects",   # pydub Effekte (optional)
        "--hidden-import=numpy",           # Für Audio-Verarbeitung (optional)

        # Netzwerk (nur für API-Calls)
        "--hidden-import=httpx",           # HTTP/2 Unterstützung
        "--hidden-import=requests",        # HTTP-Requests

        # GUI-Automation (nur für Settings)
        "--hidden-import=pyautogui",       # GUI-Automation

        # pkg_resources Side-fix (from main)
        "--hidden-import=pkg_resources",
        # jaraco dependencies (now explicitly installed)
        "--collect-all=jaraco",           # Namespace-Paket: alle jaraco Module sammeln
        "--copy-metadata=jaraco",         # Metadata für pkg_resources
        "--copy-metadata=jaraco.text",
        "--copy-metadata=jaraco.functools",
        "--copy-metadata=jaraco.context",
        
        # Explizite jaraco imports als Fallback
        "--hidden-import=jaraco",
        "--hidden-import=jaraco.text",
        "--hidden-import=jaraco.classes",
        "--hidden-import=jaraco.context",
        "--hidden-import=jaraco.functools",

        # Projekt-spezifische Module
        "--hidden-import=version_manager", # Version Management
        "--hidden-import=user_config",     # Benutzerspezifische Konfiguration
        "--hidden-import=mouse_integration", # AHK-Integration
        "--hidden-import=exceptions",      # Custom Exceptions
        "--hidden-import=notification",    # Notification Service
        "--hidden-import=src.model_manager", # Model Manager
    ]

    # Automatisch nur produktive src-Module hinzufügen (keine Tests)
    import os
    src_dir = Path("src")
    if src_dir.exists():
        for py_file in src_dir.glob("*.py"):
            if py_file.name != "__init__.py" and not py_file.name.startswith("test_"):
                module_name = f"src.{py_file.stem}"
                if module_name not in hidden_imports:
                    hidden_imports.append(f"--hidden-import={module_name}")

    # Modus bestimmen
    mode_flag = "--onedir" if mode == "onedir" else "--onefile"
    mode_desc = "Verzeichnis-Modus (verhindert DLL-Fehler)" if mode == "onedir" else "Einzelne EXE-Datei"

    print(f"Build-Modus: {mode} ({mode_desc})")

    # PyInstaller-Befehl - Optimiert für Stabilität und Performance
    pyinstaller_cmd = [
        "pyinstaller",
        mode_flag,                     # Verzeichnis oder Einzeldatei
        "--windowed",                  # Kein Konsolenfenster
        "--noupx",                     # UPX deaktivieren (verhindert DLL-Korruption)
        "--icon=assets/icon.ico",      # Icon für EXE
        "--manifest=assets/VoiceTranscriber.manifest",  # Windows-Manifest für UAC/Kompatibilität
        "--name=VoiceTranscriber",     # Name der EXE
        "--add-data=assets:assets",    # Assets einbinden
        "--add-data=scripts:scripts",  # AHK-Skript einbinden
        "--paths=src",                 # src-Verzeichnis zum Python-Pfad hinzufügen
        # Performance-Optimierungen (KONSERVATIV - verhindert DLL-Korruption)
        # ENTFERNT: --optimize=2 (zu aggressiv, kann DLLs beschädigen)
        # ENTFERNT: --strip (kann wichtige DLL-Informationen entfernen)
        # Modul-Excludes für kleinere EXE - EXTREM WICHTIG
        "--exclude-module=torch",      # PyTorch ausschließen (~150MB)
        "--exclude-module=faster_whisper", # Whisper ausschließen (~50MB)
        "--exclude-module=ctranslate2",
        "--exclude-module=numpy",      # Numpy ausschließen (wird bei Bedarf geladen)
        "--exclude-module=huggingface_hub",
        "--exclude-module=matplotlib", # Nicht benötigte Module ausschließen
        "--exclude-module=unittest",   # Test-Module entfernen
        "--exclude-module=doctest",    # Doctest entfernen
        "--exclude-module=pytest",     # Test-Framework entfernen
        "--exclude-module=setuptools", # Build-Tools entfernen
        "--exclude-module=IPython",
        "--exclude-module=PIL.ImageQt",
        "--exclude-module=PIL.ImageTk",
        # ffmpeg ist bereits im PATH verfügbar - kein Bündeln nötig
    ] + hidden_imports + [
        "main_exe.py"                  # Einstiegspunkt (PyInstaller-optimiert)
    ]

    print("Build: Führe PyInstaller aus...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")

    try:
        result = subprocess.run(
            pyinstaller_cmd, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )

        if result.returncode == 0:
            print("OK: Build erfolgreich abgeschlossen!")

            if mode == "onedir":
                print("Datei: EXE-Datei: dist/VoiceTranscriber/VoiceTranscriber.exe")

                # Verzeichnisgröße anzeigen
                dist_dir = Path("dist/VoiceTranscriber")
                if dist_dir.exists():
                    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)
                    print(f"Groesse: Gesamtgröße: {size_mb:.1f} MB")

                    # Anzahl der Dateien
                    file_count = len([f for f in dist_dir.rglob('*') if f.is_file()])
                    print(f"Dateien: {file_count} Dateien im Verzeichnis")
            else:
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
        print("   Bitte installieren: poetry install")
        sys.exit(1)

def build_bootstrap_installer():
    """Erstellt kleinen Bootstrap-Installer"""
    print("Build: Erstelle Bootstrap-Installer...")

    # PyInstaller-Befehl für Bootstrap-Installer
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Einzelne EXE-Datei
        "--windowed",                  # Kein Konsolenfenster
        "--noupx",                     # UPX deaktivieren (verhindert DLL-Korruption)
        "--icon=assets/icon.ico",      # Icon für EXE
        "--manifest=assets/VoiceTranscriber.manifest",  # Windows-Manifest
        "--name=BootstrapInstaller",   # Name der EXE
        "--add-data=assets;assets",    # Assets einbinden
        "--hidden-import=src.downloader",  # Downloader-Modul
        "--hidden-import=urllib.request",   # HTTP-Requests
        "--hidden-import=urllib.error",     # HTTP-Fehlerbehandlung
        "--hidden-import=ssl",              # SSL für HTTPS
        "--hidden-import=hashlib",          # Hashing für Verifikation
        "--paths=src",                      # src-Verzeichnis zum Python-Pfad hinzufügen
        "bootstrap_installer.py"      # Einstiegspunkt
    ]

    print("Build: Führe PyInstaller für Bootstrap-Installer aus...")
    print(f"Command: {' '.join(pyinstaller_cmd)}")

    try:
        result = subprocess.run(
            pyinstaller_cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

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
                    import shutil
                    shutil.copy2(exe_path, bootstrap_installer)
                    print(f"Datei: Finaler Installer (Copy): {bootstrap_installer}")
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
        print("   Bitte installieren: poetry install")
        return False

    return True

def build_bootstrap_installer_nsis():
    """Erstellt Bootstrap-Installer mit NSIS"""
    print("Build: Erstelle Bootstrap-Installer mit NSIS...")

    # VERIFICATION: Check if BootstrapInstaller.exe exists
    bootstrap_exe = Path("dist/BootstrapInstaller.exe")
    if not bootstrap_exe.exists():
        print(f"FEHLER: {bootstrap_exe} nicht gefunden!")
        print("   Bootstrap-Installer muss zuerst mit build_bootstrap_installer() erstellt werden")
        return False
    else:
        size_mb = bootstrap_exe.stat().st_size / (1024 * 1024)
        print(f"OK: Bootstrap-Installer gefunden: {bootstrap_exe} ({size_mb:.1f} MB)")

    # Prüfe ob NSIS verfügbar ist
    nsis_path = None
    possible_nsis_paths = [
        r'C:\Program Files\NSIS\makensis.exe',
        r'C:\Program Files (x86)\NSIS\makensis.exe',
        'makensis.exe'  # Im PATH
    ]

    for path in possible_nsis_paths:
        try:
            # Test if makensis executable exists (avoid /VERSION which Git Bash might convert)
            if Path(path).exists() or Path(path).name == 'makensis.exe':
                # Try to run makensis with a simple test
                result = subprocess.run([path, '--'], capture_output=True, text=True, timeout=5, encoding='utf-8', errors='replace')
                # makensis returns non-zero for invalid args, but that proves it exists
                nsis_path = path
                print(f"OK: NSIS gefunden: {path}")
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            print(f"DEBUG: NSIS-Suche fehlgeschlagen für {path}: {type(e).__name__}")
            continue

    if not nsis_path:
        print("FEHLER: NSIS nicht gefunden!")
        print("   Bitte installiere NSIS von: https://nsis.sourceforge.io/")
        return False

    # Prüfe ob bootstrap_installer.nsi existiert
    installer_script = Path("tools/bootstrap_installer.nsi")
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
        result = subprocess.run(nsis_cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")

        if result.returncode == 0:
            # Debug: NSIS output anzeigen
            if result.stdout:
                print("DEBUG: NSIS Output:")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)

            # Finde die erstellte Installer-Datei
            installer_files = list(Path(".").glob("VoiceTranscriber_Bootstrap_*.exe"))
            if installer_files:
                installer_file = max(installer_files, key=lambda x: x.stat().st_mtime)
                size_mb = installer_file.stat().st_size / (1024 * 1024)
                print("OK: Bootstrap-Installer erfolgreich erstellt!")
                print(f"Datei: Bootstrap-Installer: {installer_file}")
                print(f"Groesse: Größe: {size_mb:.1f} MB")
                return True
            else:
                print("FEHLER: Bootstrap-Installer-Datei nicht gefunden!")
                print(f"FEHLER: Erwartetes Pattern: VoiceTranscriber_Bootstrap_*.exe")
                all_exe = list(Path(".").glob("VoiceTranscriber*.exe"))
                print(f"FEHLER: Gefundene Dateien: {[f.name for f in all_exe]}")
                return False
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

    # VERIFICATION: Check if onedir build exists
    onedir_path = Path("dist/VoiceTranscriber")
    if not onedir_path.exists() or not onedir_path.is_dir():
        print(f"FEHLER: {onedir_path}/ nicht gefunden!")
        print("   onedir Build muss zuerst mit build_exe(mode='onedir') erstellt werden")
        return False
    else:
        file_count = len(list(onedir_path.rglob('*')))
        print(f"OK: onedir Build gefunden: {onedir_path}/ ({file_count} Dateien)")

    # Prüfe ob NSIS verfügbar ist
    nsis_path = None
    possible_nsis_paths = [
        r'C:\Program Files\NSIS\makensis.exe',
        r'C:\Program Files (x86)\NSIS\makensis.exe',
        'makensis.exe'  # Im PATH
    ]

    for path in possible_nsis_paths:
        try:
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a7dd59c (fix(ci): prevent Git Bash path conversion for NSIS commands)
            # Test if makensis executable exists (avoid /VERSION which Git Bash might convert)
            if Path(path).exists() or Path(path).name == 'makensis.exe':
                # Try to run makensis with a simple test
                result = subprocess.run([path, '--'], capture_output=True, text=True, timeout=5, encoding='utf-8', errors='replace')
                # makensis returns non-zero for invalid args, but that proves it exists
<<<<<<< HEAD
=======
            result = subprocess.run([path, '/VERSION'], capture_output=True, text=True, timeout=10, encoding='utf-8', errors='replace')
            if result.returncode == 0:
>>>>>>> 4826c34 (fix(ci): improve NSIS installation and detection)
=======
>>>>>>> a7dd59c (fix(ci): prevent Git Bash path conversion for NSIS commands)
                nsis_path = path
                print(f"OK: NSIS gefunden: {path}")
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            print(f"DEBUG: NSIS-Suche fehlgeschlagen für {path}: {type(e).__name__}")
            continue

    if not nsis_path:
        print("FEHLER: NSIS nicht gefunden!")
        print("   Bitte installiere NSIS von: https://nsis.sourceforge.io/")
        return False

    # Prüfe ob installer.nsi existiert
    installer_script = Path("tools/installer.nsi")
    if not installer_script.exists():
        print(f"FEHLER: Installer-Skript nicht gefunden: {installer_script}")
        return False

    # Lade Version aus pyproject.toml
    version = "1.0.0" # Fallback
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith('version = "'):
                    version = line.split('"')[1]
                    break
    except Exception as e:
        print(f"WARNUNG: Konnte Version nicht aus pyproject.toml lesen: {e}")
        
    print(f"Build: Verwende Version {version}")

    # NSIS-Befehl ausführen
    nsis_cmd = [
        nsis_path,
        "/V4",  # Verbose output
        f"/DVERSION={version}", # Version übergeben
        str(installer_script)
    ]

    print(f"NSIS: Führe NSIS aus: {' '.join(nsis_cmd)}")

    try:
        result = subprocess.run(nsis_cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")

        if result.returncode == 0:
            # Debug: NSIS output anzeigen
            if result.stdout:
                print("DEBUG: NSIS Output:")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)

            # Debug: Alle EXE-Dateien auflisten
            all_exe_files = list(Path(".").glob("VoiceTranscriber*.exe"))
            print(f"DEBUG: Gefundene EXE-Dateien im Root: {[f.name for f in all_exe_files]}")

            # Finde die erstellte Installer-Datei
            installer_files = list(Path(".").glob("VoiceTranscriber_Installer_*.exe"))
            if installer_files:
                installer_file = max(installer_files, key=lambda x: x.stat().st_mtime)
                size_mb = installer_file.stat().st_size / (1024 * 1024)
                print("OK: Installer erfolgreich erstellt!")
                print(f"Datei: Installer: {installer_file}")
                print(f"Groesse: Größe: {size_mb:.1f} MB")
                return True
            else:
                print("FEHLER: Installer-Datei nicht gefunden!")
                print(f"FEHLER: Erwartetes Pattern: VoiceTranscriber_Installer_*.exe")
                print(f"FEHLER: Gefundene Dateien: {[f.name for f in all_exe_files]}")
                return False
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
    build_onefile_flag = "--onefile" in sys.argv  # Für R2-Deployment
    help_flag = "--help" in sys.argv or "-h" in sys.argv

    # Hilfe anzeigen
    if help_flag:
        print("Verwendung: python build.py [OPTIONEN]")
        print("")
        print("Optionen:")
        print("  --installer      Erstellt vollständigen NSIS-Installer (--onedir)")
        print("  --bootstrap      Erstellt kleinen Bootstrap-Installer (PyInstaller)")
        print("  --bootstrap-nsis Erstellt kleinen Bootstrap-Installer (NSIS)")
        print("  --onefile        Erstellt zusätzlich eine --onefile Version für R2")
        print("  --help, -h       Diese Hilfe anzeigen")
        print("")
        print("Build-Modi:")
        print("  --onedir (Standard)  Stabiler, verhindert DLL-Fehler")
        print("  --onefile            Einzelne EXE, für R2-Download")
        print("")
        print("Beispiele:")
        print("  python build.py                           # Nur EXE erstellen (onedir)")
        print("  python build.py --installer              # EXE + vollständiger Installer")
        print("  python build.py --onefile                # Zusätzlich onefile für R2")
        print("  python build.py --bootstrap-nsis         # EXE + Bootstrap-Installer (NSIS)")
        print("  python build.py --installer --bootstrap  # Alles erstellen")
        return

    try:
        # Cleanup NUR einmal am Anfang
        print("Bereinige alte Builds...")
        if not clean_build():
            print("FEHLER: Build abgebrochen - Cleanup fehlgeschlagen")
            sys.exit(1)

        # Standardmäßig --onedir bauen (stabiler!)
        build_exe(mode="onedir", skip_cleanup=True)

        # Optional: --onefile für R2-Deployment bauen
        if build_onefile_flag or build_bootstrap_nsis_flag:
            print("\n" + "=" * 50)
            print("Erstelle zusätzlich --onefile Version für R2-Deployment...")
            build_exe(mode="onefile", skip_cleanup=True)

        # Optional Bootstrap-Installer (PyInstaller) bauen
        # Benötigt für --bootstrap-nsis, daher automatisch bauen wenn nötig
        if build_bootstrap_flag or build_bootstrap_nsis_flag:
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