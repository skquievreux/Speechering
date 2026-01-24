# Windows-Installationsfix - Technische Dokumentation

## Problem

Die Windows-Installation schlug mit zwei Hauptproblemen fehl:

### 1. DLL-Ladefehler
```
Failed to load Python DLL
C:\Users\steff\AppData\Local\Temp\_MEI102882\python311.dll
LoadLibrary: Unzulässiger Zugriff auf einen Speicherbereich.
```

**Ursache**: PyInstaller's `--onefile` Modus entpackt alle DLLs in ein temporäres Verzeichnis (`_MEI*`), was zu:
- DLL-Korruption durch UPX-Kompression
- Speicherzugriffsfehlern beim Laden
- Antivirus-Interferenz
- Langsameren Startzeiten

### 2. Fehlende Startmenü-Einträge
Windows Startmenü-Verknüpfungen wurden nicht erstellt.

**Ursache**:
- Keine expliziten Icon-Pfade in NSIS-Verknüpfungen
- Fehlendes Error-Logging
- Keine Verifizierung der Erstellung

---

## Implementierte Lösung

### 1. Windows-Manifest hinzugefügt (`assets/VoiceTranscriber.manifest`)

**Vorteile:**
- ✅ Explizite Windows 7-11 Kompatibilität
- ✅ Korrekte UAC-Behandlung (`asInvoker` - keine Admin-Rechte)
- ✅ DPI-Awareness für High-DPI-Displays
- ✅ Common Controls für moderne Windows-UI

### 2. Hybrid Build-Strategie

**Zwei Build-Modi:**

#### --onedir (für NSIS-Installer)
```bash
poetry run python tools/build.py --installer
```

- **Vorteil**: Alle DLLs liegen physisch neben der EXE
- **Vorteil**: Keine Entpackung → kein DLL-Fehler
- **Vorteil**: Schnellerer Start
- **Vorteil**: Besser für Antivirus
- **Nachteil**: Mehr Dateien (aber im Installer verpackt)

#### --onefile (für R2-Download/Bootstrap)
```bash
poetry run python tools/build.py --onefile
```

- **Vorteil**: Einzelne Datei für einfachen Download
- **Vorteil**: Kompatibel mit bestehendem Bootstrap-Installer
- **Nachteil**: Mögliche DLL-Probleme (mit Manifest gemildert)

### 3. Verbesserte PyInstaller-Flags

```python
--manifest=assets/VoiceTranscriber.manifest  # Windows-Kompatibilität
--win-private-assemblies                      # Verhindert DLL-Konflikte
--win-no-prefer-redirects                     # Nutzt gebündelte DLLs
--noupx                                       # Keine UPX-Kompression
```

### 4. NSIS-Installer-Verbesserungen

#### Vollständiger Installer (`tools/installer.nsi`)
- ✅ Rekursives Kopieren des gesamten Verzeichnisses
- ✅ Explizite Icon-Pfade in allen Verknüpfungen
- ✅ Verifizierung der Verknüpfungs-Erstellung
- ✅ Detailliertes Error-Logging
- ✅ Rekursive Deinstallation

#### Bootstrap-Installer (`tools/bootstrap_installer.nsi`)
- ✅ Verbesserte Fehlermeldungen
- ✅ Verifizierung von Desktop/Startmenü-Verknüpfungen
- ✅ Tooltips für alle Verknüpfungen
- ✅ Fallback-Shortcuts bei Download-Fehler

---

## Build-Architektur

### Lokale Entwicklung
```bash
# Stabiler Build (empfohlen)
poetry run python tools/build.py

# Mit Installer
poetry run python tools/build.py --installer

# Beide Modi
poetry run python tools/build.py --onefile --installer
```

### CI/CD Pipeline (GitHub Actions)

```yaml
1. Build onedir-Version       → dist/VoiceTranscriber/VoiceTranscriber.exe
2. Build onefile-Version       → dist/VoiceTranscriber.exe
3. Packe onedir in NSIS        → VoiceTranscriber_Installer_v*.exe
4. Erstelle Bootstrap-Installer → VoiceTranscriber_Bootstrap_*.exe
5. Upload onefile zu R2         → Für Bootstrap-Downloads
6. Upload Installer zu GitHub   → Release-Artefakte
```

---

## Deployment-Strategie

### Für Endbenutzer (Empfohlen)
**Vollständiger NSIS-Installer** (`VoiceTranscriber_Installer_v*.exe`)
- ✅ Maximale Stabilität (--onedir)
- ✅ Professionelle Installation
- ✅ Startmenü + Desktop-Verknüpfungen
- ✅ Saubere Deinstallation

### Für schnelle Installation
**Bootstrap-Installer** (`VoiceTranscriber_Bootstrap_*.exe`)
- ✅ Kleine Größe (~12 MB)
- ✅ Lädt onefile-Version von R2 (~220 MB)
- ⚠️ Erfordert Internetverbindung
- ⚠️ Potenziell weniger stabil (onefile-Modus)

### Für direkte Nutzung
**Portable onefile-EXE** (von R2)
- ✅ Einzelne Datei
- ✅ Keine Installation nötig
- ⚠️ Potenziell DLL-Fehler (mit Manifest gemildert)
- ⚠️ Keine Startmenü-Integration

---

## Technische Details

### DLL-Ladeverhalten

#### Vorher (--onefile + UPX)
```
1. Windows startet VoiceTranscriber.exe
2. PyInstaller entpackt nach %TEMP%\_MEI102882\
3. UPX dekomprimiert python311.dll
4. ❌ DLL-Korruption → Speicherzugriffsfehler
```

#### Nachher (--onedir)
```
1. Windows startet VoiceTranscriber\VoiceTranscriber.exe
2. DLLs liegen bereits neben der EXE
3. Direktes Laden → kein Entpacken
4. ✅ Erfolgreich
```

### Startmenü-Verknüpfungen

#### Vorher
```nsis
CreateShortCut "$SMPROGRAMS\...\App.lnk" "$INSTDIR\App.exe"
```
- Kein Icon
- Keine Verifizierung
- Keine Fehlermeldung

#### Nachher
```nsis
CreateShortCut "$SMPROGRAMS\...\App.lnk" \
    "$INSTDIR\App.exe" \
    "" \                          # Parameter
    "$INSTDIR\App.exe" \         # Icon-Pfad
    0 \                          # Icon-Index
    SW_SHOWNORMAL \              # Window-State
    "" \                         # Hotkey
    "Beschreibung"               # Tooltip

IfFileExists "$SMPROGRAMS\...\App.lnk" success failed
success:
    DetailPrint "✅ Verknüpfung erstellt"
failed:
    DetailPrint "⚠️ Fehler beim Erstellen"
    MessageBox "..."
```

---

## Verifizierung

### Lokaler Test
```bash
# Build ausführen
poetry run python tools/build.py --installer

# Installer sollte erstellen:
# 1. dist/VoiceTranscriber/VoiceTranscriber.exe (onedir)
# 2. VoiceTranscriber_Installer_v*.exe (NSIS)

# Installer ausführen:
# → Sollte installieren nach C:\Program Files\Voice Transcriber\
# → Sollte Startmenü-Ordner erstellen
# → Sollte Desktop-Verknüpfung erstellen
```

### CI/CD Test
```bash
# GitHub Actions sollte hochladen:
# 1. VoiceTranscriber.exe → R2 (onefile)
# 2. VoiceTranscriber_Installer_v*.exe → GitHub Release
# 3. VoiceTranscriber_Bootstrap_*.exe → GitHub Release + R2
```

### Manuelle Verifizierung (Windows)
1. ✅ Installer heruntergeladen
2. ✅ UAC-Prompt erscheint
3. ✅ Installation nach C:\Program Files\Voice Transcriber\
4. ✅ Startmenü-Ordner "Voice Transcriber" vorhanden
5. ✅ Desktop-Verknüpfung erstellt
6. ✅ App startet ohne DLL-Fehler
7. ✅ Deinstallation entfernt alle Dateien

---

## Zusammenfassung der Änderungen

### Neue Dateien
- ✅ `assets/VoiceTranscriber.manifest` - Windows-Kompatibilitäts-Manifest
- ✅ `WINDOWS_INSTALLATION_FIX.md` - Diese Dokumentation

### Geänderte Dateien
- ✅ `tools/build.py` - Hybrid-Build-System (onedir + onefile)
- ✅ `tools/installer.nsi` - Verbesserter NSIS-Installer
- ✅ `tools/bootstrap_installer.nsi` - Besseres Error-Handling
- ✅ `.github/workflows/build-and-deploy.yml` - Beide Modi bauen

### Keine Änderungen
- ✅ `tools/deploy_to_r2.py` - Funktioniert weiterhin (sucht .exe)
- ✅ `bootstrap_installer.py` - Funktioniert weiterhin

---

## Bekannte Einschränkungen

1. **Bootstrap-Installer**: Lädt weiterhin onefile-Version herunter
   - **Grund**: Einfachheit (einzelne Datei)
   - **Risiko**: Potenziell DLL-Fehler (mit Manifest gemildert)
   - **Zukünftige Lösung**: ZIP-Download + Extraktion

2. **Größe**: onedir-Version ist größer (~50MB vs. 1 Verzeichnis)
   - **Mitigation**: Im NSIS-Installer verpackt
   - **Vorteil**: Stabilität > Größe

3. **Antivirus**: Onefile-Modus kann Fehlalarme auslösen
   - **Mitigation**: Code-Signing (TODO)
   - **Workaround**: Vollständigen Installer nutzen

---

## Best Practices

### Für Entwickler
✅ Nutze `poetry run python tools/build.py --installer` für Release-Builds
✅ Teste beide Modi (onedir + onefile)
✅ Verifiziere Installer auf sauberem Windows-System

### Für Endbenutzer
✅ **Empfohlen**: Vollständiger Installer (VoiceTranscriber_Installer_*.exe)
⚠️ **Alternativ**: Bootstrap-Installer (kleinerer Download)
⚠️ **Portable**: Direkte EXE (keine Installation)

---

## Troubleshooting

### DLL-Fehler tritt weiterhin auf
1. Prüfe ob Manifest korrekt eingebunden: `--manifest=assets/VoiceTranscriber.manifest`
2. Prüfe Build-Modus: Sollte `--onedir` für Installer sein
3. Prüfe Antivirus-Logs
4. Nutze vollständigen Installer statt onefile-EXE

### Startmenü-Einträge fehlen
1. Prüfe Installer-Log auf "⚠️" Warnungen
2. Prüfe UAC: Installer benötigt Admin-Rechte
3. Prüfe Registry: `HKLM\Software\VoiceTranscriber`
4. Manueller Check: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Voice Transcriber`

### Build schlägt fehl
1. Prüfe dass `assets/VoiceTranscriber.manifest` existiert
2. Prüfe Poetry-Abhängigkeiten: `poetry install`
3. Prüfe NSIS-Installation: `makensis /VERSION`
4. Prüfe Python-Version: `python --version` (sollte 3.11 sein)

---

## Referenzen

- PyInstaller Dokumentation: https://pyinstaller.org/
- NSIS Dokumentation: https://nsis.sourceforge.io/
- Windows Manifest Schema: https://learn.microsoft.com/en-us/windows/win32/sbscs/application-manifests
- UPX-Problematik: https://github.com/pyinstaller/pyinstaller/issues?q=upx+dll
