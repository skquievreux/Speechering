"""
R2 Storage Downloader - Lädt Dateien von Cloudflare R2 Storage
"""

import hashlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from .config import config
    from .version_manager import version_manager
except ImportError:
    from config import config
    from version_manager import version_manager

logger = logging.getLogger(__name__)

class R2Downloader:
    """Downloader für Cloudflare R2 Storage Dateien"""

    def __init__(self, base_url: Optional[str] = None, access_token: Optional[str] = None):
        # Verwende benutzerdefinierte URL oder Standard
        if base_url:
            self.base_url = base_url.rstrip('/')
        else:
            self.base_url = "https://pub-fce2dd545d3648c38571dc323c7b403d.r2.dev"

        self.access_token = access_token
        self.timeout = 30  # Sekunden
        self.max_retries = 3
        self.retry_delay = 2  # Sekunden

    def download_file(self, remote_path: str, local_path: str, expected_size: Optional[int] = None, raise_on_error: bool = False) -> bool:
        """Lädt eine Datei von R2 Storage herunter"""
        remote_url = f"{self.base_url}/{remote_path.lstrip('/')}"

        try:
            logger.info(f"Lade {remote_url} -> {local_path}")

            # Erstelle Verzeichnis falls nötig
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            last_error = None
            # Download mit Retry-Logik
            for attempt in range(self.max_retries):
                try:
                    req = Request(remote_url)
                    req.add_header('User-Agent', 'VoiceTranscriber-Downloader/1.0')

                    with urlopen(req, timeout=self.timeout) as response:
                        if response.status != 200:
                            raise HTTPError(remote_url, response.status, "HTTP Error", response.headers, None)

                        # Prüfe Content-Length falls erwartet
                        if expected_size:
                            content_length = response.headers.get('Content-Length')
                            if content_length and int(content_length) != expected_size:
                                logger.warning(f"Content-Length ({content_length}) != erwartet ({expected_size})")

                        # Download in Chunks
                        downloaded_size = 0
                        with open(local_path, 'wb') as f:
                            while True:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded_size += len(chunk)

                        # Prüfe finale Größe
                        if expected_size and downloaded_size != expected_size:
                            logger.warning(f"Download-Größe ({downloaded_size}) != erwartet ({expected_size})")

                        logger.info(f"Download erfolgreich: {downloaded_size} bytes")
                        return True

                except (URLError, HTTPError, OSError) as e:
                    last_error = e
                    logger.warning(f"Download-Versuch {attempt + 1} fehlgeschlagen: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"Alle Download-Versuche fehlgeschlagen für {remote_url}")
                        if raise_on_error:
                            raise last_error or e
                        return False

        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Download: {e}")
            if raise_on_error:
                raise
            return False

        return False  # Fallback für unerwartete Fälle

    def get_file_size(self, remote_path: str) -> Optional[int]:
        """Ermittelt die Größe einer Remote-Datei"""
        remote_url = f"{self.base_url}/{remote_path.lstrip('/')}"

        try:
            req = Request(remote_url)
            req.add_header('User-Agent', 'VoiceTranscriber-Downloader/1.0')
            req.get_method = lambda: 'HEAD'  # HEAD request für Metadaten

            # Füge Access Token hinzu falls verfügbar
            if self.access_token:
                req.add_header('Authorization', f'Bearer {self.access_token}')

            with urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    content_length = response.headers.get('Content-Length')
                    return int(content_length) if content_length else None

        except Exception as e:
            logger.warning(f"Fehler beim Ermitteln der Dateigröße: {e}")

        return None

    def calculate_checksum(self, file_path: str) -> Optional[str]:
        """Berechnet SHA256-Checksumme einer Datei"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Fehler beim Berechnen der Checksumme: {e}")
            return None

    def verify_file(self, file_path: str, expected_size: Optional[int] = None, expected_checksum: Optional[str] = None) -> bool:
        """Verifiziert eine heruntergeladene Datei"""
        try:
            if not Path(file_path).exists():
                return False

            actual_size = Path(file_path).stat().st_size

            if expected_size and actual_size != expected_size:
                logger.error(f"Dateigröße stimmt nicht: {actual_size} != {expected_size}")
                return False

            # Prüfe Checksumme falls erwartet
            if expected_checksum:
                actual_checksum = self.calculate_checksum(file_path)
                if actual_checksum != expected_checksum:
                    logger.error(f"Checksumme stimmt nicht: {actual_checksum} != {expected_checksum}")
                    return False

            # Zusätzliche Verifikation: Prüfe ob Datei ausführbar ist (für EXE-Dateien)
            if file_path.lower().endswith('.exe'):
                try:
                    with open(file_path, 'rb') as f:
                        # Prüfe PE-Header (Windows EXE)
                        header = f.read(2)
                        if header != b'MZ':
                            logger.error("Datei ist keine gültige EXE-Datei")
                            return False
                except Exception as e:
                    logger.error(f"Fehler bei EXE-Verifikation: {e}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Fehler bei Dateiverifikation: {e}")
            return False

def download_voice_transcriber(target_dir: Optional[str] = None, version: str = "latest", raise_on_error: bool = False) -> bool:
    """Lädt die VoiceTranscriber EXE von R2 Storage"""
    if target_dir is None:
        # Standard-Installationsverzeichnis
        if getattr(sys, 'frozen', False):
            # Wir sind in einer EXE - verwende Programm-Verzeichnis
            target_dir_path = Path(sys.executable).parent
        else:
            # Entwicklung - verwende aktuelles Verzeichnis
            target_dir_path = Path.cwd()
    else:
        target_dir_path = Path(target_dir)

    target_dir_path.mkdir(parents=True, exist_ok=True)

    downloader = R2Downloader(base_url=config.R2_BASE_URL, access_token=config.R2_ACCESS_TOKEN)

    # Bestimme Remote-Pfad basierend auf Version
    if version == "latest":
        remote_path = "VoiceTranscriber.exe"
    else:
        remote_path = f"versions/{version}/VoiceTranscriber.exe"

    local_path = target_dir_path / "VoiceTranscriber.exe"

    # Backup alte Version falls vorhanden
    backup_path = None
    if local_path.exists():
        backup_path = target_dir_path / "VoiceTranscriber.exe.backup"
        try:
            local_path.replace(backup_path)
            logger.info(f"Backup erstellt: {backup_path}")
        except Exception as e:
            logger.warning(f"Backup konnte nicht erstellt werden: {e}")

    # Ermittle erwartete Größe
    expected_size = downloader.get_file_size(remote_path)

    # Prüfe ob Update nötig ist
    current_version = version_manager.get_installed_version(str(local_path))
    if current_version == version and local_path.exists():
        logger.info(f"Version {version} ist bereits installiert - überspringe Download")
        return True

    # Download
    if downloader.download_file(remote_path, str(local_path), expected_size, raise_on_error=raise_on_error):
        # Verifiziere Download
        checksum = downloader.calculate_checksum(str(local_path))
        if downloader.verify_file(str(local_path), expected_size):
            # Aktualisiere Versionsinformationen
            version_manager.update_file_version(str(local_path), version, expected_size or 0, checksum)
            logger.info("VoiceTranscriber erfolgreich heruntergeladen und verifiziert")
            return True
        else:
            msg = "Download-Verifikation fehlgeschlagen"
            logger.error(msg)
            # Versuche Backup wiederherzustellen
            if backup_path and backup_path.exists():
                backup_path.replace(local_path)
                logger.info("Backup wiederhergestellt")
            
            if raise_on_error:
                raise Exception(msg)
            return False
    else:
        logger.error("Download fehlgeschlagen")
        # raise_on_error wird bereits in download_file behandelt
        return False

def download_update_package(target_dir: Optional[str] = None, version: str = "latest") -> bool:
    """Lädt ein komplettes Update-Paket von R2 Storage"""
    if target_dir is None:
        # Standard-Update-Verzeichnis
        if getattr(sys, 'frozen', False):
            # Wir sind in einer EXE - verwende Programm-Verzeichnis
            base_dir = Path(sys.executable).parent
        else:
            # Entwicklung - verwende aktuelles Verzeichnis
            base_dir = Path.cwd()

        # Erstelle Updates-Verzeichnisstruktur
        target_dir_path = base_dir / "Updates"
    else:
        target_dir_path = Path(target_dir)

    # Erstelle Verzeichnisstruktur
    installer_dir = target_dir_path / "Installer"
    data_dir = target_dir_path / "Data" / "Echse"
    config_dir = target_dir_path / "Config"
    versions_dir = target_dir_path / "Versions"

    for dir_path in [installer_dir, data_dir, config_dir, versions_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    downloader = R2Downloader(base_url=config.R2_BASE_URL, access_token=config.R2_ACCESS_TOKEN)
    success = True

    try:
        # 1. Lade Bootstrap-Installer
        installer_remote = f"installer/Setup_{version}.exe"
        installer_local = installer_dir / f"Setup_{version}.exe"

        if not installer_local.exists():
            logger.info(f"Lade Bootstrap-Installer: {installer_remote}")
            if not downloader.download_file(installer_remote, str(installer_local)):
                logger.warning(f"Bootstrap-Installer konnte nicht geladen werden: {installer_remote}")
                # Das ist nicht kritisch, da der Installer optional ist

        # 2. Lade Anwendungsdaten (Echse)
        data_remote = f"data/echse/Daten_{version}.echse"
        data_local = data_dir / "Daten.echse"

        # Backup alte Daten
        if data_local.exists():
            backup_data = data_dir / f"Daten_{version_manager.get_installed_version(str(data_local)) or 'old'}.echse.backup"
            try:
                data_local.replace(backup_data)
                logger.info(f"Daten-Backup erstellt: {backup_data}")
            except Exception as e:
                logger.warning(f"Daten-Backup konnte nicht erstellt werden: {e}")

        logger.info(f"Lade Anwendungsdaten: {data_remote}")
        if downloader.download_file(data_remote, str(data_local)):
            checksum = downloader.calculate_checksum(str(data_local))
            version_manager.update_file_version(str(data_local), version, data_local.stat().st_size, checksum)
        else:
            logger.error("Anwendungsdaten konnten nicht geladen werden")
            success = False

        # 3. Lade Konfiguration (optional)
        config_remote = f"config/settings_{version}.json"
        config_local = config_dir / "settings.json"

        if downloader.get_file_size(config_remote):  # Prüfe ob Config verfügbar ist
            logger.info(f"Lade Konfiguration: {config_remote}")
            if config_local.exists():
                backup_config = config_dir / f"settings_{version_manager.get_installed_version(str(config_local)) or 'old'}.json.backup"
                try:
                    config_local.replace(backup_config)
                    logger.info(f"Config-Backup erstellt: {backup_config}")
                except Exception as e:
                    logger.warning(f"Config-Backup konnte nicht erstellt werden: {e}")

            if not downloader.download_file(config_remote, str(config_local)):
                logger.warning("Konfiguration konnte nicht geladen werden - verwende bestehende")

        # 4. Aktualisiere Versionsdatei
        version_file = versions_dir / "current.txt"
        try:
            version_file.write_text(version)
            logger.info(f"Versionsdatei aktualisiert: {version}")
        except Exception as e:
            logger.error(f"Versionsdatei konnte nicht aktualisiert werden: {e}")
            success = False

        if success:
            logger.info(f"Update-Paket {version} erfolgreich heruntergeladen")
        else:
            logger.warning(f"Update-Paket {version} teilweise fehlgeschlagen")

        return success

    except Exception as e:
        logger.error(f"Fehler beim Laden des Update-Pakets: {e}")
        return False

if __name__ == "__main__":
    # Einfacher Test
    logging.basicConfig(level=logging.INFO)
    success = download_voice_transcriber()
    sys.exit(0 if success else 1)