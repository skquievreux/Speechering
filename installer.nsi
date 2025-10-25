; Voice Transcriber - NSIS Installer Script
; Erstellt einen professionellen Windows-Installer mit Deinstaller

; Allgemeine Einstellungen
Name "Voice Transcriber v1.3.0"
OutFile "VoiceTranscriber_Installer_v1.3.0.exe"
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
LangString DESC_SecApp ${LANG_GERMAN} "Voice Transcriber Anwendung"
LangString DESC_SecApp ${LANG_ENGLISH} "Voice Transcriber Application"

; Versionsinformationen
VIProductVersion "1.3.0.0"
VIAddVersionKey "ProductName" "Voice Transcriber"
VIAddVersionKey "CompanyName" "Voice Transcriber Team"
VIAddVersionKey "FileVersion" "1.3.0.0"
VIAddVersionKey "ProductVersion" "1.3.0.0"
VIAddVersionKey "FileDescription" "Voice Transcriber Installer"

; Makros für bessere Lesbarkeit
!macro CheckAdminRights
    UserInfo::GetAccountType
    Pop $0
    ${If} $0 != "admin"
        MessageBox MB_YESNO "Für die Installation werden Administratorrechte benötigt. Als Administrator fortfahren?" IDYES continue_install
        Abort
        continue_install:
        ; Versuche als Admin neu zu starten
        ExecShell "runas" '"$EXEPATH"'
        Abort
    ${EndIf}
!macroend

Section "Voice Transcriber" SecApp
    SectionIn RO  ; Read-only, immer installiert

    SetOutPath "$INSTDIR"

    ; Hauptprogrammdateien kopieren
    DetailPrint "Installiere Voice Transcriber..."
    File "dist\VoiceTranscriber.exe"

    ; AHK-Skript kopieren
    DetailPrint "Installiere AutoHotkey-Skript..."
    File "scripts\mouse_toggle.ahk"

    ; Dokumentation kopieren
    DetailPrint "Installiere Dokumentation..."
    File "MOUSE_WHEEL_README.md"
    File "README.md"
    File "LICENSE"

    ; AHK automatisch installieren falls nicht vorhanden
    Call CheckAndInstallAHK

    ; Registry-Einträge für Windows-Programme
    DetailPrint "Registriere Programm..."
    WriteRegStr HKLM "Software\VoiceTranscriber" "" $INSTDIR
    WriteRegStr HKLM "Software\VoiceTranscriber" "Version" "1.3.0"
    WriteRegStr HKLM "Software\VoiceTranscriber" "InstallDate" "$0"

    ; Windows-Programme-Liste
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayName" "Voice Transcriber v1.3.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "Publisher" "Voice Transcriber Team"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "DisplayVersion" "1.3.0"
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "NoModify" 1
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "NoRepair" 1

    ; Installationsgröße berechnen
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWord HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber" "EstimatedSize" "$0"

    ; Deinstaller erstellen
    DetailPrint "Erstelle Deinstaller..."
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Desktop-Verknüpfung
    DetailPrint "Erstelle Desktop-Verknüpfung..."
    CreateShortCut "$DESKTOP\Voice Transcriber.lnk" "$INSTDIR\VoiceTranscriber.exe" "" "$INSTDIR\VoiceTranscriber.exe" 0

    ; Startmenü-Verknüpfung
    DetailPrint "Erstelle Startmenü-Eintrag..."
    CreateDirectory "$SMPROGRAMS\Voice Transcriber"
    CreateShortCut "$SMPROGRAMS\Voice Transcriber\Voice Transcriber.lnk" "$INSTDIR\VoiceTranscriber.exe"
    CreateShortCut "$SMPROGRAMS\Voice Transcriber\Deinstallieren.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$SMPROGRAMS\Voice Transcriber\Dokumentation.lnk" "$INSTDIR\MOUSE_WHEEL_README.md"

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
    ExecWait '"$INSTDIR\VoiceTranscriber.exe" --exit' ; Angenommen die App unterstützt --exit

    ; AHK-Skript beenden
    DetailPrint "Beende AutoHotkey-Skript..."
    ExecWait 'taskkill /f /im AutoHotkey.exe /fi "WINDOWTITLE eq Voice Transcriber*"'

    ; Dateien löschen
    DetailPrint "Entferne Programmdateien..."
    Delete "$INSTDIR\VoiceTranscriber.exe"
    Delete "$INSTDIR\mouse_toggle.ahk"
    Delete "$INSTDIR\MOUSE_WHEEL_README.md"
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
    Delete "$DESKTOP\Voice Transcriber.lnk"
    RMDir /r "$SMPROGRAMS\Voice Transcriber"

    ; Benutzerdaten fragen (optional)
    MessageBox MB_YESNO "Möchten Sie auch die benutzerspezifischen Einstellungen entfernen?" IDNO skip_user_data
    RMDir /r "$APPDATA\VoiceTranscriber"
    skip_user_data:

SectionEnd

; Funktionen
Function CheckAndInstallAHK
    ; Prüfe ob AutoHotkey installiert ist
    ReadRegStr $0 HKLM "SOFTWARE\AutoHotkey" ""
    ${If} $0 != ""
        DetailPrint "AutoHotkey ist bereits installiert"
        Return
    ${EndIf}

    ; AHK nicht gefunden - nachfragen
    MessageBox MB_YESNO "AutoHotkey ist nicht installiert. Es wird für die Mausfunktionen benötigt. Soll es automatisch installiert werden?" IDNO skip_ahk_install

    DetailPrint "Lade AutoHotkey herunter..."
    ; AHK Installer herunterladen
    NSISdl::download "https://www.autohotkey.com/download/ahk-install.exe" "$TEMP\ahk-install.exe" /TIMEOUT=30000
    Pop $0
    ${If} $0 == "success"
        DetailPrint "Installiere AutoHotkey..."
        ExecWait '"$TEMP\ahk-install.exe" /S' $1
        ${If} $1 == 0
            DetailPrint "AutoHotkey erfolgreich installiert"
        ${Else}
            DetailPrint "AutoHotkey-Installation fehlgeschlagen"
            MessageBox MB_OK "AutoHotkey konnte nicht installiert werden. Sie können es später manuell installieren."
        ${EndIf}
        Delete "$TEMP\ahk-install.exe"
    ${Else}
        DetailPrint "AutoHotkey-Download fehlgeschlagen"
        MessageBox MB_OK "AutoHotkey konnte nicht heruntergeladen werden. Sie können es später manuell installieren."
    ${EndIf}

    skip_ahk_install:
FunctionEnd

Function GetCurrentDate
    ; Aktuelles Datum im Format YYYYMMDD zurückgeben
    System::Call "kernel32::GetLocalTime(ts) i .r0"
    System::Call "kernel32::GetDateFormatW(i 0, i 0, ts, w 'yyyyMMdd', w .r1, i 9) i .r2"
    Push $1
FunctionEnd

; Beschreibungen
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecApp} $(DESC_SecApp)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Callbacks
Function .onInit
    ; Admin-Rechte prüfen
    !insertmacro CheckAdminRights

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