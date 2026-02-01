; Bootstrap Installer - NSIS Script für kleinen Downloader
; Erstellt einen minimalen Installer der nur den Bootstrap-Installer enthält

; Allgemeine Einstellungen
; Allgemeine Einstellungen
!ifndef VERSION
  !define VERSION "1.5.0"
!endif
Name "Voice Transcriber Bootstrap v${VERSION}"
OutFile "..\VoiceTranscriber_Bootstrap_Installer_v${VERSION}.exe"
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
VIProductVersion "${VERSION}.0"
VIAddVersionKey "ProductName" "Voice Transcriber Bootstrap"
VIAddVersionKey "CompanyName" "Voice Transcriber Team"
VIAddVersionKey "FileVersion" "${VERSION}.0"
VIAddVersionKey "ProductVersion" "${VERSION}.0"
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
    WriteRegStr HKLM "Software\VoiceTranscriber" "Version" "${VERSION}"
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
        DetailPrint "$\u274C Download fehlgeschlagen (Exit-Code: $0)"
        MessageBox MB_ICONEXCLAMATION|MB_OK "Der Download von VoiceTranscriber.exe ist fehlgeschlagen.$\n$\nBitte $\u00FCberpr$\u00FCfen Sie Ihre Internetverbindung und f$\u00FChren Sie die Installation erneut aus.$\n$\nSie k$\u00F6nnen den Download sp$\u00E4ter $\u00FCber '$INSTDIR\BootstrapInstaller.exe' wiederholen."
        ; Setze Flag f$\u00FCr Fehler, aber Installation fortsetzen
        WriteRegStr HKLM "Software\VoiceTranscriber" "DownloadFailed" "1"
    ${EndIf}

    ; Prüfe ob VoiceTranscriber.exe erfolgreich heruntergeladen wurde
    IfFileExists "$INSTDIR\VoiceTranscriber.exe" download_ok download_failed

    download_ok:
        DetailPrint "VoiceTranscriber.exe erfolgreich installiert"
        WriteRegStr HKLM "Software\VoiceTranscriber" "DownloadSuccess" "1"
        Goto after_download_check

    download_failed:
        DetailPrint "$\u26A0 VoiceTranscriber.exe wurde nicht heruntergeladen"
        WriteRegStr HKLM "Software\VoiceTranscriber" "DownloadSuccess" "0"

    after_download_check:

    ; Windows-Programme-Liste
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayName" "Voice Transcriber v${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "Publisher" "Voice Transcriber Team"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayVersion" "${VERSION}"
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
    ; Desktop & Startmen$\u00FC-Verkn$\u00FCpfungen auf VoiceTranscriber.exe
    ; (NICHT auf Bootstrap-Installer!)
    ; ====================================================================

    IfFileExists "$INSTDIR\VoiceTranscriber.exe" create_shortcuts_app create_shortcuts_bootstrap

    create_shortcuts_app:
        ; Desktop-Verknüpfung auf die eigentliche App
        DetailPrint "Erstelle Desktop-Verknüpfung für Voice Transcriber..."
        CreateShortCut "$DESKTOP\Voice Transcriber.lnk" "$INSTDIR\VoiceTranscriber.exe" "" "$INSTDIR\VoiceTranscriber.exe" 0 SW_SHOWNORMAL "" "Voice Transcriber - Sprachtranskription"

        ; Pr$\u00FCfe ob Desktop-Verkn$\u00FCpfung erstellt wurde
        IfFileExists "$DESKTOP\Voice Transcriber.lnk" desktop_ok desktop_failed
        desktop_ok:
            DetailPrint "$\u2705 Desktop-Verkn$\u00FCpfung erfolgreich erstellt"
            Goto desktop_done
        desktop_failed:
            DetailPrint "$\u26A0 Desktop-Verkn$\u00FCpfung konnte nicht erstellt werden"
        desktop_done:

        ; Startmen$\u00FC-Verkn$\u00FCpfungen
        DetailPrint "Erstelle Startmen$\u00FC-Eintr$\u00E4ge..."
        CreateDirectory "$SMPROGRAMS\Voice Transcriber"

        ; Pr$\u00FCfe ob Verzeichnis erstellt wurde
        IfFileExists "$SMPROGRAMS\Voice Transcriber" startmenu_dir_ok startmenu_dir_failed
        startmenu_dir_ok:
            DetailPrint "$\u2705 Startmen$\u00FC-Verzeichnis erstellt: $SMPROGRAMS\Voice Transcriber"

            ; Hauptverknüpfung mit Icon
            CreateShortCut "$SMPROGRAMS\Voice Transcriber\Voice Transcriber.lnk" "$INSTDIR\VoiceTranscriber.exe" "" "$INSTDIR\VoiceTranscriber.exe" 0 SW_SHOWNORMAL "" "Voice Transcriber starten"
            DetailPrint "Erstelle Verknüpfung: Voice Transcriber.lnk"

            ; Bootstrap-Verkn$\u00FCpfung
            CreateShortCut "$SMPROGRAMS\Voice Transcriber\Installation erneut durchf$\u00FChren.lnk" "$INSTDIR\BootstrapInstaller.exe" "" "$INSTDIR\BootstrapInstaller.exe" 0 SW_SHOWNORMAL "" "Installation erneut durchf$\u00FChren"
            DetailPrint "Erstelle Verkn$\u00FCpfung: Installation erneut durchf$\u00FChren.lnk"

            ; Deinstaller-Verkn$\u00FCpfung
            CreateShortCut "$SMPROGRAMS\Voice Transcriber\Deinstallieren.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0 SW_SHOWNORMAL "" "Voice Transcriber deinstallieren"
            DetailPrint "Erstelle Verkn$\u00FCpfung: Deinstallieren.lnk"

            ; Dokumentation-Verknüpfung
            CreateShortCut "$SMPROGRAMS\Voice Transcriber\Dokumentation.lnk" "$INSTDIR\README.md" "" "%SystemRoot%\system32\SHELL32.dll" 70 SW_SHOWNORMAL "" "Dokumentation öffnen"
            DetailPrint "Erstelle Verknüpfung: Dokumentation.lnk"

            ; Verifiziere Verkn$\u00FCpfungen
            IfFileExists "$SMPROGRAMS\Voice Transcriber\Voice Transcriber.lnk" 0 +2
                DetailPrint "$\u2705 Startmen$\u00FC-Verkn$\u00FCpfungen erfolgreich erstellt"

            Goto shortcuts_done

        startmenu_dir_failed:
            DetailPrint "$\u26A0 Startmen$\u00FC-Verzeichnis konnte nicht erstellt werden"
            MessageBox MB_ICONEXCLAMATION|MB_OK "Das Startmen$\u00FC-Verzeichnis konnte nicht erstellt werden.$\n$\nPfad: $SMPROGRAMS\Voice Transcriber$\n$\nBitte $\u00FCberpr$\u00FCfen Sie die Berechtigungen."

    create_shortcuts_bootstrap:
        ; Fallback: Wenn Download fehlgeschlagen, Verkn$\u00FCpfung auf Bootstrap erstellen
        DetailPrint "Download fehlgeschlagen - erstelle Verkn$\u00FCpfung auf Bootstrap-Installer..."
        CreateShortCut "$DESKTOP\Voice Transcriber - Installation durchf$\u00FChren.lnk" "$INSTDIR\BootstrapInstaller.exe" "" "$INSTDIR\BootstrapInstaller.exe" 0

        ; Startmenü
        CreateDirectory "$SMPROGRAMS\Voice Transcriber"
        CreateShortCut "$SMPROGRAMS\Voice Transcriber\Installation durchf$\u00FChren.lnk" "$INSTDIR\BootstrapInstaller.exe"
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
    MessageBox MB_YESNO "M$\u00F6chten Sie auch die benutzerspezifischen Einstellungen entfernen?" IDNO skip_user_data
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