# Bug: Bootstrap-Installer erfordert doppelte Installation

## 🐛 Problem

**Aktuelles Verhalten:**
1. User lädt `VoiceTranscriber_Bootstrap_Installer.exe` (NSIS) herunter
2. NSIS-Installer kopiert Bootstrap-Installer ins Programm-Verzeichnis
3. Desktop-Verknüpfung zeigt auf **Bootstrap-Installer** (nicht auf App!)
4. User muss Desktop-Icon klicken → Bootstrap-GUI öffnet sich
5. User muss "Installation starten" klicken
6. Download von VoiceTranscriber.exe startet
7. Nach Download: Keine Verknüpfung auf VoiceTranscriber.exe

**Resultat:** User muss zweimal "installieren" - das ist verwirrend! 😕

## ✅ Erwartetes Verhalten

1. User lädt `VoiceTranscriber_Bootstrap_Installer.exe` herunter
2. NSIS-Installer läuft
3. **Automatisch** wird VoiceTranscriber.exe von R2 heruntergeladen (kein zweiter Klick!)
4. Desktop-Verknüpfung zeigt auf **VoiceTranscriber.exe**
5. User kann sofort die App starten

## 📊 Impact

**Betroffene User:** Alle Nutzer des Bootstrap-Installers
**Schweregrad:** HOCH (Benutzerfreundlichkeit)
**Priorität:** P1

## 🔧 Lösung

**Option A: NSIS ruft Bootstrap automatisch auf** (Implementiert)

### Änderungen:

1. **bootstrap_installer.py:**
   - Silent-Mode hinzufügen (`--silent` Flag)
   - Keine GUI im Silent-Mode
   - Direkter Download ohne User-Interaktion
   - Exit-Code für Erfolg/Fehler

2. **bootstrap_installer.nsi:**
   - Nach Kopieren: Bootstrap automatisch aufrufen
   - `ExecWait` mit `--silent` Parameter
   - Warten auf Completion
   - Verknüpfungen auf **VoiceTranscriber.exe** erstellen (nicht Bootstrap!)

3. **Neue Verknüpfungen:**
   - Desktop: `Voice Transcriber.lnk` → VoiceTranscriber.exe
   - Startmenü: `Voice Transcriber.lnk` → VoiceTranscriber.exe
   - Startmenü: `Installation erneut durchführen.lnk` → Bootstrap (optional)

## 🧪 Test-Szenarien

- [ ] NSIS-Installer läuft durch ohne manuelle Interaktion
- [ ] VoiceTranscriber.exe wird automatisch heruntergeladen
- [ ] Desktop-Verknüpfung startet die App (nicht Bootstrap)
- [ ] Bei Fehler: User bekommt klare Fehlermeldung
- [ ] Deinstaller entfernt alle Dateien korrekt

## 📝 Betroffene Dateien

- `bootstrap_installer.py` - Silent-Mode hinzufügen
- `bootstrap_installer.nsi` - ExecWait Bootstrap + Verknüpfungen korrigieren
- `README.md` - Dokumentation aktualisieren

## 🔗 Verwandte Issues

- #18 - Progress-Bar für Bootstrap-Installer (kann danach implementiert werden)
- #24 - Auto-Update-Funktion (nutzt gleiche Infrastruktur)

## 📅 Timeline

- **Erstellt:** 2025-11-04
- **Priorität:** P1 (KRITISCH)
- **Ziel:** Vor nächstem Release (v1.5.1)
