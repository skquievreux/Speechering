#!/usr/bin/env python3
"""
Cloudflare R2 Storage Deployment Script
Lädt Build-Artefakte zu Cloudflare R2 Storage hoch.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class R2Deployer:
    """Deployment-Klasse für Cloudflare R2 Storage"""

    def __init__(self, access_key_id: str, secret_access_key: str, account_id: str, bucket_name: str):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.account_id = account_id
        self.bucket_name = bucket_name

        # R2 Endpoint
        self.endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

        # S3 Client für R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto'  # R2 verwendet 'auto' als Region
        )

    def upload_file(self, local_path: str, remote_path: str, content_type: Optional[str] = None) -> bool:
        """Lädt eine Datei zu R2 Storage hoch"""
        try:
            # Content-Type automatisch bestimmen
            if content_type is None:
                if local_path.lower().endswith('.exe'):
                    content_type = 'application/x-msdownload'
                elif local_path.lower().endswith('.json'):
                    content_type = 'application/json'
                elif local_path.lower().endswith('.txt'):
                    content_type = 'text/plain'
                else:
                    content_type = 'application/octet-stream'

            # Datei hochladen
            logger.info(f"Lade {local_path} -> {remote_path}")
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                remote_path,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # Öffentlicher Lesezugriff
                }
            )

            logger.info(f"✅ Erfolgreich hochgeladen: {remote_path}")
            return True

        except ClientError as e:
            logger.error(f"❌ Upload-Fehler für {remote_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler beim Upload von {remote_path}: {e}")
            return False

    def upload_directory(self, local_dir: str, remote_prefix: str = "") -> bool:
        """Lädt ein ganzes Verzeichnis zu R2 Storage hoch"""
        local_path = Path(local_dir)
        if not local_path.exists():
            logger.error(f"Verzeichnis existiert nicht: {local_dir}")
            return False

        success = True
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                # Relativer Pfad für Remote-Key
                relative_path = file_path.relative_to(local_path)
                remote_key = f"{remote_prefix.rstrip('/')}/{relative_path}".lstrip('/')

                if not self.upload_file(str(file_path), remote_key):
                    success = False

        return success

    def get_public_url(self, remote_path: str) -> str:
        """Gibt die öffentliche URL für eine Datei zurück"""
        return f"https://{self.bucket_name}.{self.account_id}.r2.cloudflarestorage.com/{remote_path.lstrip('/')}"

def load_build_info() -> dict:
    """Lädt Build-Informationen"""
    build_info_file = Path("artifacts/build_info.txt")
    if build_info_file.exists():
        info = {}
        with open(build_info_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    info[key] = value
        return info

    # Fallback: Aus Umgebungsvariablen
    return {
        'VERSION': os.getenv('VERSION', 'latest'),
        'BUILD_DATE': os.getenv('BUILD_DATE', ''),
        'GIT_COMMIT': os.getenv('GITHUB_SHA', ''),
        'GIT_REF': os.getenv('GITHUB_REF', '')
    }

def main():
    """Hauptfunktion für das Deployment"""
    # Umgebungsvariablen aus GitHub Secrets
    access_key_id = os.getenv('R2_ACCESS_KEY_ID')
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
    account_id = os.getenv('R2_ACCOUNT_ID')
    bucket_name = os.getenv('R2_BUCKET_NAME')

    if not all([access_key_id, secret_access_key, account_id, bucket_name]):
        logger.error("❌ Fehlende R2-Konfiguration!")
        logger.error("Benötigte Umgebungsvariablen:")
        logger.error("  R2_ACCESS_KEY_ID")
        logger.error("  R2_SECRET_ACCESS_KEY")
        logger.error("  R2_ACCOUNT_ID")
        logger.error("  R2_BUCKET_NAME")
        sys.exit(1)

    # Sicherstellen, dass alle Werte Strings sind
    access_key_id = str(access_key_id)
    secret_access_key = str(secret_access_key)
    account_id = str(account_id)
    bucket_name = str(bucket_name)

    # Build-Info laden
    build_info = load_build_info()
    version = build_info.get('VERSION', 'latest')
    logger.info(f"🚀 Starte Deployment für Version {version}")

    # Deployer initialisieren
    deployer = R2Deployer(access_key_id, secret_access_key, account_id, bucket_name)

    # Artifacts-Verzeichnis bestimmen
    artifacts_dir = Path("artifacts")
    if not artifacts_dir.exists() or not list(artifacts_dir.glob("*")):
        logger.info("Verzeichnis 'artifacts/' nicht gefunden oder leer, verwende aktuelles Verzeichnis '.'")
        artifacts_dir = Path(".")

    success = True

    try:
        # 1. VoiceTranscriber.exe hochladen (als "latest")
        exe_files = list(artifacts_dir.glob("VoiceTranscriber.exe"))
        if exe_files:
            exe_path = exe_files[0]
            if not deployer.upload_file(str(exe_path), "VoiceTranscriber.exe"):
                success = False

            # Versionierte Kopie
            if version != "latest":
                versioned_path = f"versions/{version}/VoiceTranscriber.exe"
                if not deployer.upload_file(str(exe_path), versioned_path):
                    success = False

        # 2. Bootstrap-Installer hochladen
        bootstrap_files = list(artifacts_dir.glob("VoiceTranscriber_Bootstrap_*.exe"))
        for bootstrap_file in bootstrap_files:
            remote_path = f"installer/{bootstrap_file.name}"
            if not deployer.upload_file(str(bootstrap_file), remote_path):
                success = False

        # 3. Vollständige Installer hochladen
        installer_files = list(artifacts_dir.glob("VoiceTranscriber_Installer_*.exe"))
        for installer_file in installer_files:
            remote_path = f"installer/{installer_file.name}"
            if not deployer.upload_file(str(installer_file), remote_path):
                success = False

        # 4. Build-Info hochladen
        build_info_files = list(artifacts_dir.glob("build_info.txt"))
        if build_info_files:
            remote_path = f"builds/{version}/build_info.txt"
            if not deployer.upload_file(str(build_info_files[0]), remote_path):
                success = False

        # 5. Version-Info als JSON hochladen
        version_info = {
            "version": version,
            "build_date": build_info.get('BUILD_DATE', ''),
            "git_commit": build_info.get('GIT_COMMIT', ''),
            "git_ref": build_info.get('GIT_REF', ''),
            "files": {
                "exe": deployer.get_public_url("VoiceTranscriber.exe"),
                "bootstrap_installer": deployer.get_public_url(f"installer/VoiceTranscriber_Bootstrap_Installer_v{version}.exe"),
                "full_installer": deployer.get_public_url(f"installer/VoiceTranscriber_Installer_v{version}.exe")
            }
        }

        # Temporäre JSON-Datei erstellen
        version_json_path = artifacts_dir / f"version_{version}.json"
        with open(version_json_path, 'w') as f:
            json.dump(version_info, f, indent=2)

        if not deployer.upload_file(str(version_json_path), f"versions/{version}.json", "application/json"):
            success = False

        # Temporäre Datei löschen
        version_json_path.unlink(missing_ok=True)

        if success:
            logger.info("✅ Deployment erfolgreich abgeschlossen!")
            logger.info(f"📦 Version {version} ist verfügbar unter:")
            logger.info(f"   EXE: {deployer.get_public_url('VoiceTranscriber.exe')}")
            logger.info(f"   Bootstrap: {deployer.get_public_url(f'installer/VoiceTranscriber_Bootstrap_Installer_v{version}.exe')}")
        else:
            logger.error("❌ Deployment teilweise fehlgeschlagen!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()