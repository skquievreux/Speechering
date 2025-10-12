#!/usr/bin/env python3
"""
Test-Skript für die neue Mouse Wheel Integration.
Testet UserConfig und MouseWheelIntegration.
"""

import os
import sys
from pathlib import Path

# Füge src zum Python-Pfad hinzu
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from config import config
from mouse_integration import MouseWheelIntegration
from user_config import user_config


def test_user_config():
    """Testet das UserConfig-System"""
    print("=== Testing UserConfig ===")

    # Lade Config
    success = user_config.load()
    print(f"Config loaded: {success}")

    # Zeige AppData-Verzeichnis
    appdata_dir = user_config.get_appdata_dir()
    print(f"AppData directory: {appdata_dir}")

    # Zeige Config-Datei
    config_file = user_config.get_config_file()
    print(f"Config file: {config_file}")

    # Teste Hotkey-Funktionen
    primary_hotkey = user_config.get_hotkey('primary')
    print(f"Primary hotkey: {primary_hotkey}")

    # Setze neuen Hotkey
    user_config.set_hotkey('primary', 'f11')
    user_config.save()
    print("Set primary hotkey to 'f11'")

    # Teste Mouse Wheel
    mouse_enabled = user_config.is_mouse_wheel_enabled()
    print(f"Mouse wheel enabled: {mouse_enabled}")

    user_config.enable_mouse_wheel(True)
    print("Enabled mouse wheel")

    mouse_enabled = user_config.is_mouse_wheel_enabled()
    print(f"Mouse wheel enabled: {mouse_enabled}")

    print("UserConfig test completed\n")

def test_mouse_integration():
    """Testet die MouseWheelIntegration"""
    print("=== Testing MouseWheelIntegration ===")

    integration = MouseWheelIntegration()

    # Zeige Skript-Pfad
    script_path = integration.get_script_path()
    print(f"AHK script path: {script_path}")
    print(f"Script exists: {script_path.exists()}")

    # Prüfe AHK-Verfügbarkeit
    ahk_available = integration.is_ahk_available()
    print(f"AutoHotkey available: {ahk_available}")

    if ahk_available:
        # Starte Integration
        started = integration.start()
        print(f"Integration started: {started}")

        if started:
            # Prüfe ob läuft
            running = integration.is_running()
            print(f"Integration running: {running}")

            # Stoppe Integration
            stopped = integration.stop()
            print(f"Integration stopped: {stopped}")

    print("MouseWheelIntegration test completed\n")

def test_combined_config():
    """Testet die kombinierte Config-Funktionalität"""
    print("=== Testing Combined Config ===")

    # Teste Config-Methoden
    primary_hotkey = config.get_user_hotkey('primary')
    print(f"Config primary hotkey: {primary_hotkey}")

    mouse_enabled = config.is_mouse_wheel_enabled()
    print(f"Config mouse wheel enabled: {mouse_enabled}")

    input_method = config.get_input_method()
    print(f"Config input method: {input_method}")

    print("Combined config test completed\n")

def main():
    """Hauptfunktion"""
    print("Voice Transcriber - Integration Test")
    print("=" * 40)

    try:
        test_user_config()
        test_mouse_integration()
        test_combined_config()

        print("All tests completed successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()