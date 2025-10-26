"""
Version Management - Zentrale Versionsverwaltung für Voice Transcriber
Automatische Versionsnummerierung und Synchronisation aller Versionseinträge.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class VersionManager:
    """Verwaltet Versionsnummern zentral und synchronisiert alle Dateien"""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.current_version = "1.4.1"  # Aktuelle Version

        # Dateien die aktualisiert werden müssen
        self.version_files = {
            'src/config.py': [
                (r"self\.APP_VERSION: str = os\.getenv\('APP_VERSION', '[^']+'\)",
                 f"self.APP_VERSION: str = os.getenv('APP_VERSION', '{self.current_version}')")
            ],
            'installer.nsi': [
                (r"Name \"Voice Transcriber v[^\"]+\"",
                 f"Name \"Voice Transcriber v{self.current_version}\""),
                (r"OutFile \"VoiceTranscriber_Installer_v[^\"]+.exe\"",
                 f"OutFile \"VoiceTranscriber_Installer_v{self.current_version}.exe\""),
                (r"VIProductVersion \"[^\"]+\"",
                 f"VIProductVersion \"{self.current_version}.0\""),
                (r"VIAddVersionKey \"ProductVersion\" \"[^\"]+\"",
                 f"VIAddVersionKey \"ProductVersion\" \"{self.current_version}.0\""),
                (r"VIAddVersionKey \"FileVersion\" \"[^\"]+\"",
                 f"VIAddVersionKey \"FileVersion\" \"{self.current_version}.0\""),
                (r"WriteRegStr HKLM \"Software\\VoiceTranscriber\" \"Version\" \"[^\"]+\"",
                 f"WriteRegStr HKLM \"Software\\VoiceTranscriber\" \"Version\" \"{self.current_version}\""),
                (r"WriteRegStr HKLM \"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\VoiceTranscriber\" \"DisplayName\" \"Voice Transcriber v[^\"]+\"",
                 f"WriteRegStr HKLM \"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\VoiceTranscriber\" \"DisplayName\" \"Voice Transcriber v{self.current_version}\""),
                (r"WriteRegStr HKLM \"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\VoiceTranscriber\" \"DisplayVersion\" \"[^\"]+\"",
                 f"WriteRegStr HKLM \"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\VoiceTranscriber\" \"DisplayVersion\" \"{self.current_version}\"")
            ],
            'build.py': [
                (r"hidden_imports = \[",
                 f"hidden_imports = [\n        \"--hidden-import=version_manager\",  # Version Management")
            ]
        }

    def get_version(self) -> str:
        """Gibt die aktuelle Version zurück"""
        return self.current_version

    def set_version(self, new_version: str):
        """Setzt eine neue Version und aktualisiert alle Dateien"""
        if not self._validate_version(new_version):
            raise ValueError(f"Ungültiges Versionsformat: {new_version}")

        old_version = self.current_version
        self.current_version = new_version

        print(f"🔄 Aktualisiere Version von {old_version} auf {new_version}")

        # Aktualisiere alle Dateien
        for file_path, patterns in self.version_files.items():
            self._update_file(file_path, patterns, old_version, new_version)

        print("✅ Versionsaktualisierung abgeschlossen")

    def _validate_version(self, version: str) -> bool:
        """Validiert das Versionsformat (Semantic Versioning)"""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    def _update_file(self, file_path: str, patterns: List[tuple], old_version: str, new_version: str):
        """Aktualisiert eine einzelne Datei mit den neuen Versionseinträgen"""
        full_path = self.base_dir / file_path

        if not full_path.exists():
            print(f"⚠️  Datei nicht gefunden: {file_path}")
            return

        try:
            content = full_path.read_text(encoding='utf-8')

            for pattern, replacement in patterns:
                # Ersetze Platzhalter in replacement
                final_replacement = replacement.replace('{self.current_version}', new_version)

                # Führe Ersetzung durch
                if re.search(pattern, content, re.MULTILINE):
                    content = re.sub(pattern, final_replacement, content, flags=re.MULTILINE)
                    print(f"   📝 {file_path}: {pattern[:50]}... → {final_replacement[:50]}...")
                else:
                    print(f"   ⚠️  Pattern nicht gefunden in {file_path}: {pattern[:50]}...")

            # Schreibe aktualisierte Datei
            full_path.write_text(content, encoding='utf-8')
            print(f"   ✅ {file_path} aktualisiert")

        except Exception as e:
            print(f"   ❌ Fehler beim Aktualisieren von {file_path}: {e}")

    def bump_version(self, bump_type: str = 'patch') -> str:
        """Erhöht die Version automatisch (major, minor, patch)"""
        major, minor, patch = map(int, self.current_version.split('.'))

        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Unbekannter Bump-Type: {bump_type}")

        new_version = f"{major}.{minor}.{patch}"
        self.set_version(new_version)
        return new_version

    def get_version_info(self) -> Dict[str, Any]:
        """Gibt detaillierte Versionsinformationen zurück"""
        return {
            'version': self.current_version,
            'major': self.current_version.split('.')[0],
            'minor': self.current_version.split('.')[1],
            'patch': self.current_version.split('.')[2],
            'files_updated': list(self.version_files.keys())
        }


# Globale Instanz
version_manager = VersionManager()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'get':
            print(version_manager.get_version())
        elif command == 'set' and len(sys.argv) > 2:
            version_manager.set_version(sys.argv[2])
        elif command in ['major', 'minor', 'patch']:
            new_version = version_manager.bump_version(command)
            print(f"Neue Version: {new_version}")
        elif command == 'info':
            import json
            print(json.dumps(version_manager.get_version_info(), indent=2))
        else:
            print("Verwendung: python version.py [get|set <version>|major|minor|patch|info]")
    else:
        print(f"Aktuelle Version: {version_manager.get_version()}")