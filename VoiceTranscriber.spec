# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_exe.py'],
    pathex=['src'],
    binaries=[],
    datas=[('assets', 'assets'), ('scripts', 'scripts')],
    hiddenimports=['version_manager', 'version_manager', 'pystray._win32', 'winsound', 'keyboard', 'pyperclip', 'pillow', 'pyaudio', 'audioop', 'pydub', 'pydub.effects', 'numpy', 'httpx', 'requests', 'pyautogui', 'version_manager', 'user_config', 'mouse_integration', 'exceptions', 'notification', 'src.model_manager', 'src.audio_recorder', 'src.clipboard_injector', 'src.config', 'src.downloader', 'src.encryption', 'src.exceptions', 'src.hotkey_listener', 'src.local_transcription', 'src.main', 'src.model_manager', 'src.mouse_integration', 'src.notification', 'src.settings_gui', 'src.text_processor', 'src.transcription', 'src.user_config', 'src.version_manager', 'src.__main__', 'torch', 'faster_whisper', 'ctranslate2', 'huggingface_hub', 'tokenizers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'unittest', 'doctest', 'pytest', 'setuptools', 'IPython', 'PIL.ImageQt', 'PIL.ImageTk'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VoiceTranscriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icon.ico'],
    manifest='assets\\VoiceTranscriber.manifest',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='VoiceTranscriber',
)
