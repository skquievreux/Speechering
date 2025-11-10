#!/usr/bin/env python3
"""
Version Manager für automatische Versionierung
Ermittelt die nächste Version basierend auf Git-Tags und Commits.
"""

import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def get_latest_git_tag() -> Optional[str]:
    """Ermittelt das neueste Git-Tag"""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_commits_since_tag(tag: str) -> int:
    """Zählt Commits seit dem letzten Tag"""
    try:
        result = subprocess.run(
            ['git', 'rev-list', f'{tag}..HEAD', '--count'],
            capture_output=True, text=True, check=True
        )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError:
        return 0

def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parst eine Version im Format v1.2.3 oder 1.2.3"""
    # Entferne 'v' Präfix falls vorhanden
    version_str = version_str.lstrip('v')

    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if not match:
        raise ValueError(f"Ungültiges Versionsformat: {version_str}")

    return int(match.group(1)), int(match.group(2)), int(match.group(3))

def increment_version(major: int, minor: int, patch: int, increment_type: str = 'patch') -> str:
    """Erhöht die Version um den angegebenen Typ"""
    if increment_type == 'major':
        return f"{major + 1}.0.0"
    elif increment_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif increment_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Unbekannter Increment-Typ: {increment_type}")

def determine_next_version() -> str:
    """Ermittelt die nächste Version basierend auf Git-Historie"""
    latest_tag = get_latest_git_tag()

    if latest_tag:
        try:
            major, minor, patch = parse_version(latest_tag)
            commits_since = get_commits_since_tag(latest_tag)

            if commits_since > 0:
                # Neue Commits seit letztem Tag -> Patch-Version erhöhen
                next_version = increment_version(major, minor, patch, 'patch')
            else:
                # Keine neuen Commits -> verwende bestehende Version
                next_version = f"{major}.{minor}.{patch}"

        except ValueError as e:
            print(f"Warnung: Konnte Version nicht parsen ({e}), verwende 1.0.0")
            next_version = "1.0.0"
    else:
        # Kein Tag gefunden -> starte mit 1.0.0
        next_version = "1.0.0"

    return next_version

def get_current_commit() -> str:
    """Gibt den aktuellen Git-Commit-Hash zurück"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

def get_current_branch() -> str:
    """Gibt den aktuellen Git-Branch zurück"""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

def is_working_tree_clean() -> bool:
    """Prüft ob das Working Tree sauber ist"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, check=True
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False

def create_version_info(version: str) -> dict:
    """Erstellt ein Dictionary mit Versionsinformationen"""
    return {
        "version": version,
        "commit": get_current_commit(),
        "branch": get_current_branch(),
        "clean": is_working_tree_clean(),
        "latest_tag": get_latest_git_tag()
    }

if __name__ == "__main__":
    # Kommandozeilen-Tool
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        version = determine_next_version()
        info = create_version_info(version)

        print(f"Version: {version}")
        print(f"Commit: {info['commit']}")
        print(f"Branch: {info['branch']}")
        print(f"Working Tree Clean: {info['clean']}")
        print(f"Latest Tag: {info['latest_tag']}")
    else:
        print(determine_next_version())