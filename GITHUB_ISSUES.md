# GitHub Issues für Voice Transcriber - Verbesserungsvorschläge

Erstellt: 2025-11-02
Basis: Code-Review v1.5.0

---

## 🚨 P1 - KRITISCH (Sofort beheben)

### Issue #1: Versionsnummer inkonsistent zwischen version.py und README
**Labels:** `bug`, `priority: critical`, `good first issue`

**Beschreibung:**
Die Versionsnummer ist zwischen verschiedenen Dateien inkonsistent:
- `version.py`: v1.4.1
- `README.md`: v1.5.0
- `CHANGELOG.md`: v1.5.0

**Schritte zur Reproduktion:**
```bash
python version.py get
# Output: 1.4.1

# Aber README.md zeigt v1.5.0
```

**Erwartetes Verhalten:**
Alle Dateien sollten die gleiche Version zeigen.

**Lösung:**
```bash
python version.py set 1.5.0
```

**Dateien betroffen:**
- `version.py` (Zeile 16)
- `src/config.py` (Zeile 66)
- `installer.nsi` (mehrere Zeilen)

---

### Issue #2: Code-Duplikate und fehlerhafte Log-Strings in main.py
**Labels:** `bug`, `priority: critical`, `code-quality`

**Beschreibung:**
Mehrere Probleme in `src/main.py`:

1. **Doppelte Variable-Deklaration:**
   - `self.last_recording_start_time` wird zweimal initialisiert (Zeile 91 + 98)

2. **Fehlerhafte Log-Strings:**
   - Zeile 189: `.2f` ohne String-Format-Funktion
   - Zeile 284: `.2f` ohne String-Format-Funktion
   - Zeile 287: `.2f` ohne String-Format-Funktion

3. **Doppelt auskommentierter Code:**
   - Single-Instance-Check ist zweimal auskommentiert (Zeile 462-470)

**Code-Beispiele:**
```python
# Problem 1:
self.last_recording_start_time = 0.0  # Zeile 91
# ...
self.last_recording_start_time = 0.0  # Zeile 98 - DUPLIKAT!

# Problem 2:
logger.debug(".2f")  # ← Sollte sein: f"...{duration:.2f}..."
```

**Impact:**
- Verwirrende Code-Struktur
- Logs zeigen ".2f" statt tatsächliche Werte
- Potenzielle Bugs durch doppelte Initialisierung

**Priorität:** KRITISCH

---

### Issue #3: Fehlende Error-Handling in _perform_recording()
**Labels:** `bug`, `priority: critical`, `stability`

**Beschreibung:**
Die Methode `_perform_recording()` in `src/main.py` hat schwache Fehlerbehandlung, was zu App-Abstürzen bei Audio-Fehlern führen kann.

**Probleme:**
- Generisches `except Exception` ohne spezifische Behandlung (Zeile 321)
- Keine Retry-Logik bei temporären Fehlern
- Keine User-Benachrichtigung bei Fehlern

**Betroffene Datei:**
- `src/main.py` (Zeile 216-326)

**Erwartetes Verhalten:**
- Spezifische Exception-Typen abfangen
- User-freundliche Fehlermeldungen
- Automatische Retry-Logik für temporäre Fehler
- Graceful Degradation

**Priorität:** KRITISCH

---

### Issue #36: Duplikate in requirements.txt
**Labels:** `bug`, `priority: high`, `dependencies`, `good first issue`

**Beschreibung:**
`requirements.txt` enthält doppelte Einträge:
- `numpy>=2.2.0` (Zeile 14)
- `numpy>=1.21.0` (Zeile 25)

**Problem:**
- Inkonsistente Versionsanforderungen
- Verwirrung für Dependency-Management

**Lösung:**
Einen Eintrag behalten (bevorzugt: `numpy>=2.2.0`)

**Priorität:** HOCH

---

## ⚠️ P2 - HOCH

### Issue #4: Fehlende Type Hints in vielen Funktionen
**Labels:** `enhancement`, `priority: high`, `code-quality`, `good first issue`

**Beschreibung:**
Viele Funktionen haben keine oder unvollständige Type Hints.

**Beispiele:**
```python
# Gut:
def transcribe(self, audio_path: str) -> Optional[str]:

# Schlecht (fehlt Return-Type):
def on_hotkey_press(self):
def on_hotkey_release(self):
def play_beep(self, frequency: int):
```

**Nutzen:**
- Bessere IDE-Unterstützung
- Weniger Bugs durch Type-Checking
- Verbesserte Dokumentation

**Betroffene Dateien:**
- `src/main.py`
- `src/audio_recorder.py`
- `src/clipboard_injector.py`
- `src/hotkey_listener.py`

**Priorität:** HOCH

---

### Issue #5: Keine Dependency Injection - Hard-coded Komponenten
**Labels:** `enhancement`, `priority: medium`, `architecture`, `refactoring`

**Beschreibung:**
Komponenten sind hart gekoppelt, was Testing erschwert.

**Aktueller Code:**
```python
def __init__(self):
    self.audio_recorder = AudioRecorder()  # Hard-coded
    self.transcription_service = TranscriptionService()
```

**Vorgeschlagene Verbesserung:**
```python
def __init__(self,
             audio_recorder: Optional[AudioRecorder] = None,
             transcription_service: Optional[TranscriptionService] = None):
    self.audio_recorder = audio_recorder or AudioRecorder()
    self.transcription_service = transcription_service or TranscriptionService()
```

**Nutzen:**
- Bessere Testbarkeit (Mock-Injection)
- Flexiblere Konfiguration
- Loose Coupling

**Priorität:** MITTEL

---

### Issue #6: Singleton-Pattern verwendet globale Variablen
**Labels:** `enhancement`, `priority: medium`, `architecture`, `refactoring`

**Beschreibung:**
`src/transcription.py` nutzt globale Variablen für Singleton-Pattern (Zeile 18-20):

```python
_global_local_service: Optional[LocalTranscriptionService] = None
_global_local_service_model_size: Optional[str] = None
```

**Problem:**
- Nicht Thread-Safe
- Schwer zu testen
- Verstößt gegen Python Best Practices

**Lösung:**
Metaclass-basiertes Singleton oder `@dataclass` mit frozen=True

**Priorität:** MITTEL

---

### Issue #7: Logging-Konfiguration mit Race Condition
**Labels:** `bug`, `priority: medium`, `threading`

**Beschreibung:**
`src/config.py` Zeile 204 löscht alle Handler und fügt sie sofort wieder hinzu:

```python
logging.getLogger().handlers.clear()  # ← Race Condition!
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)
```

**Problem:**
Bei Multi-Threading können Logs verloren gehen zwischen clear() und addHandler().

**Lösung:**
Handler nur einmal beim Start konfigurieren oder Thread-Safe-Locking verwenden.

**Priorität:** MITTEL

---

### Issue #8: Sehr geringe Test-Abdeckung (< 10%)
**Labels:** `testing`, `priority: high`, `technical-debt`

**Beschreibung:**
Nur 4 Test-Dateien vorhanden, viele kritische Module nicht getestet:

**Fehlende Tests:**
- ❌ `src/main.py` (0% Coverage)
- ❌ `src/clipboard_injector.py` (0%)
- ❌ `src/text_processor.py` (0%)
- ❌ `src/mouse_integration.py` (0%)
- ❌ Integration Tests für komplette Workflows
- ❌ E2E Tests für Installer

**Ziel:** Mindestens 70% Code Coverage

**Priorität:** HOCH

---

### Issue #11: API-Keys im Klartext in .env
**Labels:** `security`, `priority: high`

**Beschreibung:**
Sensible Daten werden nicht verschlüsselt gespeichert, obwohl `encryption.py` existiert.

**Problem:**
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx  # Klartext!
R2_ACCESS_TOKEN=your-token-here
```

**Lösung:**
Vollständige Migration zu verschlüsselter User-Config (bereits teilweise implementiert).

**Priorität:** HOCH

---

### Issue #14: Busy-Wait-Schleife verschwendet CPU
**Labels:** `performance`, `priority: high`, `bug`

**Beschreibung:**
`src/main.py` Zeile 266 verwendet Busy-Wait:

```python
while self.is_recording:
    time.sleep(0.01)  # ← Verschwendet CPU!
```

**Problem:**
- Unnötiger CPU-Verbrauch
- Schlechte Performance

**Lösung:**
`threading.Event()` oder `queue.Queue()` verwenden:

```python
self.recording_stop_event = threading.Event()

# Warten:
self.recording_stop_event.wait()

# Signalisieren:
self.recording_stop_event.set()
```

**Priorität:** HOCH

---

### Issue #16: Doppelte Hidden-Imports in build.py
**Labels:** `bug`, `priority: medium`, `build`, `good first issue`

**Beschreibung:**
`build.py` enthält doppelte Hidden-Imports:

```python
"--hidden-import=version_manager",  # Zeile 86
"--hidden-import=version_manager",  # Zeile 87 - DUPLIKAT!
"--hidden-import=user_config",      # Zeile 102
# Dann wieder automatisch hinzugefügt in Zeile 114
```

**Lösung:**
Duplikate entfernen.

**Priorität:** MITTEL

---

### Issue #17: Keyboard-Shortcut-Anpassung fehlt in GUI
**Labels:** `enhancement`, `priority: high`, `ux`

**Beschreibung:**
Settings-GUI existiert, aber Hotkey-Anpassung ist nicht implementiert. User muss `config.json` manuell bearbeiten.

**Erwartetes Verhalten:**
- GUI-Widget zur Hotkey-Auswahl
- Live-Test der Hotkeys
- Konflikt-Erkennung

**Betroffene Datei:**
- `src/settings_gui.py`

**Priorität:** HOCH

---

## 📋 P3 - MITTEL

### Issue #9: Keine Continuous Testing in CI/CD
**Labels:** `ci/cd`, `testing`, `priority: medium`

**Beschreibung:**
GitHub Actions führt keine Tests aus.

**Fehlende Pipeline-Schritte:**
```yaml
- name: Run Tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=src tests/
    pytest --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

**Priorität:** MITTEL

---

### Issue #10: Fehlende Performance-Tests
**Labels:** `testing`, `performance`, `priority: low`

**Beschreibung:**
Keine Benchmarks für:
- Audio-Komprimierung
- Latenz-Messungen
- Memory-Profiling

**Vorschlag:**
`pytest-benchmark` integrieren.

**Priorität:** NIEDRIG

---

### Issue #12: Keine Input-Validierung in Config
**Labels:** `security`, `priority: medium`, `validation`

**Beschreibung:**
`src/config.py` validiert nicht ausreichend:

```python
if self.MAX_RECORDING_DURATION <= 0 or self.MAX_RECORDING_DURATION > 60:
    logging.error(...)
    return False  # ← App läuft trotzdem weiter!
```

**Problem:**
Ungültige Konfigurationen können App crashen.

**Lösung:**
`raise ValueError()` statt nur logging.

**Priorität:** MITTEL

---

### Issue #13: Temp-Dateien nicht sicher gelöscht
**Labels:** `security`, `privacy`, `priority: medium`

**Beschreibung:**
Audio-Dateien werden nicht sicher gelöscht (Überschreiben vor Löschen).

**Empfehlung:**
```python
def secure_delete(file_path: Path):
    # Überschreibe mit Zufallsdaten
    size = file_path.stat().st_size
    with open(file_path, 'wb') as f:
        f.write(os.urandom(size))
    file_path.unlink()
```

**Priorität:** MITTEL

---

### Issue #15: Unnötige Modell-Neuladungen
**Labels:** `performance`, `priority: low`

**Beschreibung:**
Lokales Whisper-Modell wird bei jedem App-Neustart geladen.

**Lösung:**
Model-Caching im AppData-Verzeichnis.

**Priorität:** NIEDRIG

---

### Issue #18: Kein Feedback bei langen Operationen
**Labels:** `ux`, `priority: high`, `enhancement`

**Beschreibung:**
Bootstrap-Installer lädt 220 MB ohne Progress-Bar.

**Lösung:**
Progress-Bar für Downloads hinzufügen.

**Priorität:** HOCH

---

### Issue #19: Keine Sprach-Auswahl
**Labels:** `enhancement`, `i18n`, `priority: low`

**Beschreibung:**
Sprache ist hardcoded auf Deutsch:

```python
# transcription.py:90
language="de",  # ← Hardcoded
```

**Erwartetes Verhalten:**
GUI-Option zur Sprachauswahl (de, en, fr, es, etc.)

**Priorität:** NIEDRIG

---

### Issue #20: Fehlende Audio-Vorschau
**Labels:** `enhancement`, `ux`, `priority: low`

**Beschreibung:**
User kann aufgenommenes Audio nicht anhören vor Transkription.

**Nutzen:**
- QA-Check vor teuren API-Calls
- Bessere User-Kontrolle

**Priorität:** NIEDRIG

---

### Issue #21: Keine History/Verlauf
**Labels:** `enhancement`, `feature`, `priority: medium`

**Beschreibung:**
Transkriptionen werden nicht gespeichert.

**Vorschlag:**
SQLite-Datenbank für:
- Transkriptions-Verlauf
- Volltextsuche
- Export (CSV, JSON)

**Priorität:** MITTEL

---

### Issue #22: Fehlende Undo-Funktion
**Labels:** `enhancement`, `ux`, `priority: low`

**Beschreibung:**
Einmal eingefügter Text kann nicht rückgängig gemacht werden.

**Lösung:**
Strg+Z sollte letzten eingefügten Text entfernen (mit Clipboard-Stack).

**Priorität:** NIEDRIG

---

### Issue #23: Keine digitale Signatur
**Labels:** `deployment`, `security`, `priority: high`

**Beschreibung:**
Windows SmartScreen blockiert Installer.

**Lösung:**
Code-Signing Zertifikat beantragen (z.B. SignPath, DigiCert).

**Priorität:** HOCH

---

### Issue #24: Fehlende Auto-Update-Funktion
**Labels:** `enhancement`, `deployment`, `priority: high`

**Beschreibung:**
Bootstrap-Installer prüft zwar Version, aber kein Auto-Update.

**Vorschlag:**
- Squirrel.Windows integrieren
- Oder eigene Update-Logik mit R2 Storage

**Priorität:** HOCH

---

### Issue #25: Keine Rollback-Mechanismus
**Labels:** `deployment`, `stability`, `priority: medium`

**Beschreibung:**
Bei fehlgeschlagenem Update bleibt User mit kaputter Installation.

**Lösung:**
- Backup vor Update
- Automatisches Restore bei Fehler

**Priorität:** MITTEL

---

### Issue #26: Installer-Lokalisierung unvollständig
**Labels:** `i18n`, `priority: low`

**Beschreibung:**
NSIS-Installer hat DE/EN, aber App selbst ist nur DE.

**Lösung:**
i18n mit `gettext` oder `babel`.

**Priorität:** NIEDRIG

---

### Issue #27: Fehlende API-Dokumentation
**Labels:** `documentation`, `priority: medium`

**Beschreibung:**
Keine Docstrings in vielen Funktionen.

**Empfehlung:**
- Sphinx einrichten
- Google-Style Docstrings
- Automatische API-Docs auf GitHub Pages

**Priorität:** MITTEL

---

### Issue #28: Keine Contributor-Guidelines
**Labels:** `documentation`, `community`, `priority: low`

**Beschreibung:**
Fehlende Dateien:
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/`

**Priorität:** NIEDRIG

---

### Issue #29: Fehlende Architecture Decision Records (ADRs)
**Labels:** `documentation`, `architecture`, `priority: low`

**Beschreibung:**
Dokumentiere wichtige Entscheidungen:
- Warum Cloudflare R2 statt S3?
- Warum PyInstaller statt cx_Freeze?
- Warum AHK statt Python für Mouse-Integration?

**Format:** `docs/adr/0001-use-cloudflare-r2.md`

**Priorität:** NIEDRIG

---

### Issue #30: Fehlende Pre-Commit Hooks
**Labels:** `ci/cd`, `code-quality`, `priority: medium`

**Beschreibung:**
Einrichten von `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/pylint
    hooks:
      - id: pylint
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

**Priorität:** MITTEL

---

### Issue #31: Keine Automatischen Releases
**Labels:** `ci/cd`, `deployment`, `priority: medium`

**Beschreibung:**
GitHub Actions baut nur, veröffentlicht aber nicht.

**Lösung:**
Automatisches Release bei Git-Tag:
```yaml
on:
  push:
    tags:
      - 'v*'
```

**Priorität:** MITTEL

---

### Issue #32: Fehlende Dependency-Updates
**Labels:** `dependencies`, `security`, `priority: medium`

**Beschreibung:**
Keine Dependabot/Renovate-Konfiguration.

**Lösung:**
`.github/dependabot.yml` erstellen:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Priorität:** MITTEL

---

## 🎨 P4 - NIEDRIG (Code-Stil)

### Issue #33: Inkonsistente String-Quotes
**Labels:** `code-quality`, `style`, `good first issue`

**Beschreibung:**
Gemischte Verwendung von `"` und `'`.

**Lösung:**
Black-Formatter durchlaufen lassen.

**Priorität:** NIEDRIG

---

### Issue #34: Magic Numbers überall
**Labels:** `code-quality`, `refactoring`, `good first issue`

**Beschreibung:**
Unbenannte numerische Konstanten:

```python
time.sleep(0.5)   # Was bedeutet 0.5?
time.sleep(0.01)  # Und 0.01?
```

**Lösung:**
Benannte Konstanten:
```python
DEBOUNCE_DELAY_SECONDS = 0.5
RECORDING_POLL_INTERVAL = 0.01
```

**Priorität:** NIEDRIG

---

### Issue #35: Try-Except zu breit
**Labels:** `code-quality`, `error-handling`, `good first issue`

**Beschreibung:**
Zu generische Exception-Behandlung:

```python
except Exception as e:  # ← Fängt ALLES!
```

**Lösung:**
Spezifische Exceptions:
```python
except (OSError, IOError, AudioError) as e:
```

**Priorität:** NIEDRIG

---

### Issue #37: Ungenutzte Imports
**Labels:** `code-quality`, `cleanup`, `good first issue`

**Beschreibung:**
Aufräumen ungenutzter Imports mit `autoflake` oder `pylint`.

**Priorität:** NIEDRIG

---

### Issue #38: Hardcoded Pfade
**Labels:** `code-quality`, `refactoring`, `good first issue`

**Beschreibung:**
```python
icon_path = "assets/icon.ico"  # ← Sollte über Config
```

**Lösung:**
Alle Pfade in `config.py` zentralisieren.

**Priorität:** NIEDRIG

---

## 📊 Zusammenfassung

**Gesamt:** 38 Issues
- 🚨 **P1 Kritisch:** 4 Issues (#1, #2, #3, #36)
- ⚠️ **P2 Hoch:** 10 Issues (#4-#8, #11, #14, #16-18, #23-24)
- 📋 **P3 Mittel:** 15 Issues (#9-#10, #12-#13, #15, #21, #25, #27, #30-32)
- 🎨 **P4 Niedrig:** 9 Issues (#19-#20, #22, #26, #28-#29, #33-#35, #37-#38)

---

## 🎯 Empfohlene Reihenfolge

**Quick Wins (1-2 Stunden):**
1. Issue #1 - Versionsnummer sync
2. Issue #36 - requirements.txt Duplikate
3. Issue #2 - Code-Duplikate
4. Issue #16 - build.py Duplikate
5. Issue #34 - Magic Numbers

**High Impact (1-2 Tage):**
6. Issue #14 - Busy-Wait → Event
7. Issue #8 - Test-Coverage erhöhen
8. Issue #17 - Hotkey-GUI
9. Issue #18 - Progress-Bar

**Long-term (1-2 Wochen):**
10. Issue #24 - Auto-Update
11. Issue #21 - History-Feature
12. Issue #23 - Code-Signing

---

**Anleitung zum Erstellen der Issues:**

Da `gh` CLI nicht verfügbar ist, kannst du diese Issues entweder:

**Option A: Manuell über GitHub Web-UI**
1. Gehe zu: https://github.com/skquievreux/Speechering/issues/new
2. Kopiere Titel + Beschreibung aus diesem Dokument
3. Füge entsprechende Labels hinzu

**Option B: Bulk-Import mit GitHub CLI (lokal)**
```bash
gh issue create --title "..." --body "..." --label "bug,priority:critical"
```

**Option C: Ich erstelle ein Python-Script**
Das automatisch alle Issues via GitHub API erstellt (benötigt PAT).

Welche Option bevorzugst du?
