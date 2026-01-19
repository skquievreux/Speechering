# Versionsbereinigungs-Plan für Voice Transcriber

## Aktuelle Situation

Die Versionierung des Voice Transcriber Projekts weist derzeit Inkonsistenzen auf, die zu Verwirrung führen können. Hier ist eine Übersicht der aktuellen Versionsstände:

| Komponente | Version | Quelle |
|------------|---------|--------|
| Hauptanwendung | 1.5.0 | `src/config.py` |
| Bootstrap-Installer | 1.5.0 | `bootstrap_installer.py` |
| NSIS-Installer | 1.5.0 | `installer.nsi` |
| Cloudflare R2 | 1.5.0 | Deployment-Artefakte |
| CHANGELOG | 1.5.0 | `CHANGELOG.md` |

## Probleme

1. **Versionsdrift**: In der Vergangenheit wurden Versionen in verschiedenen Dateien manuell aktualisiert, was zu Inkonsistenzen führte.
2. **Fehlende zentrale Versionsverwaltung**: Obwohl `version.py` existiert, wurde es nicht konsequent für alle Komponenten genutzt.
3. **Unklare Versionshistorie**: Die tatsächliche Versionshistorie im CHANGELOG stimmt nicht immer mit den Release-Artefakten überein.

## Lösungsansatz

### 1. Zentralisierte Versionsverwaltung

- **Primäre Quelle**: `version.py` wird als einzige Quelle der Wahrheit für die Versionsnummer etabliert.
- **Automatische Synchronisation**: Alle anderen Dateien beziehen ihre Versionsnummer aus dieser Quelle.

### 2. Automatisierte Version-Updates

```python
# Beispiel für version.py Nutzung
import version

# Version abrufen
current_version = version.get_version()  # Gibt "1.5.0" zurück

# Version inkrementieren
version.increment("patch")  # Ändert zu "1.5.1"
version.increment("minor")  # Ändert zu "1.6.0"
version.increment("major")  # Ändert zu "2.0.0"
```

### 3. Build-Integration

- Der Build-Prozess (`build.py`) wird erweitert, um die Version aus `version.py` zu lesen und in alle relevanten Dateien einzufügen:
  - `src/config.py`
  - `bootstrap_installer.py`
  - `installer.nsi`
  - Generierte EXE-Metadaten

### 4. CI/CD-Pipeline

- GitHub Actions Workflow wird aktualisiert, um die Version aus `version.py` zu lesen und für Deployment-Artefakte zu verwenden.
- Automatische CHANGELOG-Updates bei Version-Änderungen.

## Implementierungsplan

### Phase 1: Konsolidierung (Abgeschlossen)

- [x] Alle Versionen auf 1.5.0 vereinheitlichen
- [x] CHANGELOG für Version 1.5.0 aktualisieren
- [x] Neuen Build mit konsistenter Version erstellen

### Phase 2: Automatisierung

- [ ] `version.py` erweitern, um alle relevanten Dateien zu aktualisieren
- [ ] Build-Skript anpassen, um Version automatisch einzubinden
- [ ] Tests für Versionsverwaltung implementieren

### Phase 3: CI/CD-Integration

- [ ] GitHub Actions Workflow aktualisieren
- [ ] Automatische CHANGELOG-Generierung implementieren
- [ ] Release-Prozess dokumentieren

## Vorteile

1. **Konsistenz**: Alle Komponenten zeigen dieselbe Version an
2. **Einfachheit**: Version muss nur an einer Stelle geändert werden
3. **Zuverlässigkeit**: Reduzierte Fehleranfälligkeit durch Automatisierung
4. **Transparenz**: Klare Versionshistorie im CHANGELOG

## Fazit

Mit diesem Plan wird die Versionsverwaltung des Voice Transcriber Projekts vereinheitlicht und automatisiert. Dies reduziert manuelle Fehler und stellt sicher, dass alle Komponenten konsistent versioniert sind.

Die aktuelle Version 1.5.0 ist nun in allen Komponenten synchronisiert und bildet die Basis für zukünftige Releases.