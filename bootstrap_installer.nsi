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
!insertmacro MUI_PAGE_LICENSE "LICENSE"
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

    ; Bootstrap-Installer kopieren
    DetailPrint "Installiere Bootstrap-Installer..."
    File "VoiceTranscriber_Bootstrap_Installer.exe"

    ; Dokumentation kopieren
    DetailPrint "Installiere Dokumentation..."
    File "README.md"
    File "LICENSE"

    ; Registry-Einträge
    DetailPrint "Registriere Programm..."
    WriteRegStr HKLM "Software\VoiceTranscriber" "" $INSTDIR
    WriteRegStr HKLM "Software\VoiceTranscriber" "Version" "1.4.1"
    WriteRegStr HKLM "Software\VoiceTranscriber" "InstallDate" "$0"
    WriteRegStr HKLM "Software\VoiceTranscriber" "BootstrapMode" "1"

    ; Windows-Programme-Liste
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayName" "Voice Transcriber Bootstrap v1.4.1"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "Publisher" "Voice Transcriber Team"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayVersion" "1.4.1"
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "NoModify" 1
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "NoRepair" 1

    ; Installationsgröße berechnen
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "EstimatedSize" "$0"

    ; Deinstaller erstellen
    DetailPrint "Erstelle Deinstaller..."
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Desktop-Verknüpfung für Bootstrap-Installer
    DetailPrint "Erstelle Desktop-Verknüpfung..."
    CreateShortCut "$DESKTOP\Voice Transcriber Setup.lnk" "$INSTDIR\VoiceTranscriber_Bootstrap_Installer.exe" "" "$INSTDIR\VoiceTranscriber_Bootstrap_Installer.exe" 0

    ; Startmenü-Verknüpfung
    DetailPrint "Erstelle Startmenü-Eintrag..."
    CreateDirectory "$SMPROGRAMS\Voice Transcriber"
    CreateShortCut "$SMPROGRAMS\Voice Transcriber\Voice Transcriber Setup.lnk" "$INSTDIR\VoiceTranscriber_Bootstrap_Installer.exe"
    CreateShortCut "$SMPROGRAMS\Voice Transcriber\Deinstallieren.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$SMPROGRAMS\Voice Transcriber\Dokumentation.lnk" "$INSTDIR\README.md"

    ; Installationsdatum setzen
    ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallDate"
    ${If} $0 == ""
        Call GetCurrentDate
        Pop $0
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallDate" $0
    ${EndIf}

SectionEnd

Section "Uninstall"
    ; Deinstallation

    ; Anwendung beenden falls läuft
    DetailPrint "Beende Voice Transcriber..."
    ExecWait '"$INSTDIR\VoiceTranscriber.exe" --exit'

    ; Bootstrap-Installer beenden
    DetailPrint "Beende Bootstrap-Installer..."
    ExecWait 'taskkill /f /im VoiceTranscriber_Bootstrap_Installer.exe /fi "WINDOWTITLE eq Voice Transcriber*"'

    ; Dateien löschen
    DetailPrint "Entferne Programmdateien..."
    Delete "$INSTDIR\VoiceTranscriber_Bootstrap_Installer.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\uninstall.exe"

    ; Verzeichnis entfernen (nur wenn leer)
    RMDir "$INSTDIR"

    ; Registry bereinigen
    DetailPrint "Bereinige Registry..."
    DeleteRegKey HKLM "Software\VoiceTranscriber"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber"

    ; Verknüpfungen entfernen
    DetailPrint "Entferne Verknüpfungen..."
    Delete "$DESKTOP\Voice Transcriber Setup.lnk"
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
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN

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