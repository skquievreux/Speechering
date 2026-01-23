; Bootstrap Installer - NSIS Script für kleinen Downloader
; Erstellt einen minimalen Installer der nur den Bootstrap-Installer enthält

; Allgemeine Einstellungen
Name "Voice Transcriber Bootstrap"
OutFile "VoiceTranscriber_Bootstrap_Installer.exe"
Unicode True
InstallDir "$PROGRAMFILES\Voice Transcriber"
InstallDirRegKey HKLM "Software\VoiceTranscriber" ""
RequestExecutionLevel admin

; Modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; Seiten definieren
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Deinstallationsseiten
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Sprachen
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "English"

; Spracheinstellungen
LangString DESC_SecApp ${LANG_GERMAN} "Voice Transcriber Bootstrap-Installer"
LangString DESC_SecApp ${LANG_ENGLISH} "Voice Transcriber Bootstrap Installer"
LangString DESC_SecAutostart ${LANG_GERMAN} "Mit Windows starten"
LangString DESC_SecAutostart ${LANG_ENGLISH} "Start with Windows"

; Versionsinformationen
VIProductVersion "1.4.1.0"
VIAddVersionKey "ProductName" "Voice Transcriber Bootstrap"
VIAddVersionKey "CompanyName" "Voice Transcriber Team"
VIAddVersionKey "FileVersion" "1.4.1.0"
VIAddVersionKey "ProductVersion" "1.4.1.0"
VIAddVersionKey "FileDescription" "Voice Transcriber Bootstrap Installer"

Section "Voice Transcriber Bootstrap" SecApp
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Bootstrap-Installer kopieren (temporär für Download)
    DetailPrint "Installiere Bootstrap-Installer..."
    File "..\dist\BootstrapInstaller.exe"

    ; Dokumentation kopieren
    DetailPrint "Installiere Dokumentation..."
    File "..\docs\README.md"
    File "..\LICENSE"

    ; Registry-Einträge
    DetailPrint "Registriere Programm..."
    WriteRegStr HKLM "Software\VoiceTranscriber" "" $INSTDIR
    WriteRegStr HKLM "Software\VoiceTranscriber" "Version" "1.5.0"
    WriteRegStr HKLM "Software\VoiceTranscriber" "InstallDate" "$0"
    WriteRegStr HKLM "Software\VoiceTranscriber" "BootstrapMode" "1"

    ; ====================================================================
    ; WICHTIG: Automatischer Download von VoiceTranscriber.exe
    ; ====================================================================
    DetailPrint "Lade VoiceTranscriber.exe von Cloudflare R2 herunter..."
    DetailPrint "Dies kann einige Minuten dauern (~220 MB)..."

    ; Führe Bootstrap-Installer im Silent-Mode aus
    ExecWait '"$INSTDIR\BootstrapInstaller.exe" --silent' $0

    ; Prüfe Exit-Code
    ${If} $0 == 0
        DetailPrint "✅ Download erfolgreich!"
    ${Else}
        DetailPrint "❌ Download fehlgeschlagen (Exit-Code: $0)"
        MessageBox MB_ICONEXCLAMATION|MB_OK "Der Download von VoiceTranscriber.exe ist fehlgeschlagen.$\n$\nBitte überprüfen Sie Ihre Internetverbindung und führen Sie die Installation erneut aus.$\n$\nSie können den Download später über '$INSTDIR\BootstrapInstaller.exe' wiederholen."
        ; Setze Flag für Fehler, aber Installation fortsetzen
        WriteRegStr HKLM "Software\VoiceTranscriber" "DownloadFailed" "1"
    ${EndIf}

    ; Prüfe ob VoiceTranscriber.exe erfolgreich heruntergeladen wurde
    IfFileExists "$INSTDIR\VoiceTranscriber.exe" download_ok download_failed

    download_ok:
        DetailPrint "VoiceTranscriber.exe erfolgreich installiert"
        WriteRegStr HKLM "Software\VoiceTranscriber" "DownloadSuccess" "1"
        Goto after_download_check

    download_failed:
        DetailPrint "⚠️ VoiceTranscriber.exe wurde nicht heruntergeladen"
        WriteRegStr HKLM "Software\VoiceTranscriber" "DownloadSuccess" "0"

    after_download_check:

    ; Windows-Programme-Liste
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayName" "Voice Transcriber v1.5.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "Publisher" "Voice Transcriber Team"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayVersion" "1.5.0"
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "NoModify" 1
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "NoRepair" 1

    ; Installationsgröße berechnen
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "EstimatedSize" "$0"

    ; Deinstaller erstellen
    DetailPrint "Erstelle Deinstaller..."
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; ====================================================================
    ; Desktop & Startmenü-Verknüpfungen auf VoiceTranscriber.exe
    ; (NICHT auf Bootstrap-Installer!)
    ; ====================================================================

    IfFileExists "$INSTDIR\VoiceTranscriber.exe" create_shortcuts_app create_shortcuts_bootstrap

    create_shortcuts_app:
        ; Desktop-Verknüpfung auf die eigentliche App
        DetailPrint "Erstelle Desktop-Verknüpfung für Voice Transcriber..."
        CreateShortCut "$DESKTOP\Voice Transcriber.lnk" "$INSTDIR\VoiceTranscriber.exe" "" "$INSTDIR\VoiceTranscriber.exe" 0

        ; Startmenü-Verknüpfungen
        DetailPrint "Erstelle Startmenü-Einträge..."
        CreateDirectory "$SMPROGRAMS\Voice Transcriber"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Voice Transcriber.lnk" "$INSTDIR\VoiceTranscriber.exe"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Installation erneut durchführen.lnk" "$INSTDIR\BootstrapInstaller.exe"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Deinstallieren.lnk" "$INSTDIR\uninstall.exe"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Dokumentation.lnk" "$INSTDIR\README.md"
        Goto shortcuts_done

    create_shortcuts_bootstrap:
        ; Fallback: Wenn Download fehlgeschlagen, Verknüpfung auf Bootstrap erstellen
        DetailPrint "Download fehlgeschlagen - erstelle Verknüpfung auf Bootstrap-Installer..."
        CreateShortCut "$DESKTOP\Voice Transcriber - Installation durchführen.lnk" "$INSTDIR\BootstrapInstaller.exe" "" "$INSTDIR\BootstrapInstaller.exe" 0

        ; Startmenü
        CreateDirectory "$SMPROGRAMS\Voice Transcriber"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Installation durchführen.lnk" "$INSTDIR\BootstrapInstaller.exe"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Deinstallieren.lnk" "$INSTDIR\uninstall.exe"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Dokumentation.lnk" "$INSTDIR\README.md"

    shortcuts_done:

    ; Installationsdatum setzen
    ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallDate"
    ${If} $0 == ""
        Call GetCurrentDate
        Pop $0
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallDate" $0
    ${EndIf}

SectionEnd

Section "Autostart" SecAutostart
    ; Autostart
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "VoiceTranscriber" "$INSTDIR\VoiceTranscriber.exe"
SectionEnd

Section "Uninstall"
    ; Deinstallation

    ; Anwendung beenden falls läuft
    DetailPrint "Beende Voice Transcriber..."
    ExecWait 'taskkill /f /im VoiceTranscriber.exe'

    ; Bootstrap-Installer beenden
    DetailPrint "Beende Bootstrap-Installer..."
    ExecWait 'taskkill /f /im BootstrapInstaller.exe'

    ; Warte kurz für Process Cleanup
    Sleep 500

    ; Dateien löschen
    DetailPrint "Entferne Programmdateien..."
    Delete "$INSTDIR\VoiceTranscriber.exe"
    Delete "$INSTDIR\VoiceTranscriber.exe.backup"
    Delete "$INSTDIR\BootstrapInstaller.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\uninstall.exe"

    ; Verzeichnis entfernen (nur wenn leer)
    RMDir "$INSTDIR"

    ; Registry bereinigen
    DetailPrint "Bereinige Registry..."
    DeleteRegKey HKLM "Software\VoiceTranscriber"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber"
    DeleteRegValue HKLM "Software\Microsoft\Windows\CurrentVersion\Run" "VoiceTranscriber"

    ; Verknüpfungen entfernen
    DetailPrint "Entferne Verknüpfungen..."
    Delete "$DESKTOP\Voice Transcriber.lnk"
    Delete "$DESKTOP\Voice Transcriber - Installation durchführen.lnk"
    RMDir /r "$SMPROGRAMS\Voice Transcriber"

    ; Benutzerdaten fragen (optional)
    MessageBox MB_YESNO "Möchten Sie auch die benutzerspezifischen Einstellungen entfernen?" IDNO skip_user_data
    RMDir /r "$APPDATA\VoiceTranscriber"
    skip_user_data:

SectionEnd

Function GetCurrentDate
    ; Aktuelles Datum im Format YYYYMMDD zurückgeben
    System::Call "kernel32::GetLocalTime(ts) i .r0"
    System::Call "kernel32::GetDateFormatW(i 0, i 0, ts, w 'yyyyMMdd', w .r1, i 9) i .r2"
    Push $1
FunctionEnd

; Beschreibungen
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecApp} $(DESC_SecApp)
!insertmacro MUI_DESCRIPTION_TEXT ${SecAutostart} $(DESC_SecAutostart)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Callbacks
Function .onInit
    ; Sprache automatisch erkennen
    System::Call 'kernel32::GetUserDefaultUILanguage() i .r0'
    ${If} $0 == 1031  ; German
        !insertmacro MUI_LANGDLL_DISPLAY
    ${Else}
        StrCpy $LANGUAGE ${LANG_ENGLISH}
    ${EndIf}
FunctionEnd

Function un.onInit
    ; Sprache für Deinstallation
    !insertmacro MUI_UNGETLANGUAGE
FunctionEnd