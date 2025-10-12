; Voice Transcriber - Mittleres Mausrad Toggle
; Dieses Skript erkennt mittleres Mausrad-Klicks und simuliert F12
; für die Voice Transcriber Anwendung (Toggle-Modus)

#Persistent
#SingleInstance Force

; Globale Variable für Aufnahme-Status
recording := false

; Mittleres Mausrad (MButton) Handler
MButton::
    ; Toggle Aufnahme-Status
    recording := !recording

    if (recording) {
        ; Starte Aufnahme: Simuliere F12 gedrückt
        Send {F12 down}
        Sleep 50
        Send {F12 up}

        ; Optional: Visuelles Feedback (TrayTip)
        TrayTip, Voice Transcriber, Aufnahme gestartet, 1, 1
    } else {
        ; Stoppe Aufnahme: Simuliere F12 gedrückt
        Send {F12 down}
        Sleep 50
        Send {F12 up}

        ; Optional: Visuelles Feedback
        TrayTip, Voice Transcriber, Aufnahme gestoppt, 1, 1
    }
return

; Hotkey zum Beenden des Skripts (Strg+Alt+End)
^!End::
    TrayTip, Voice Transcriber, Skript beendet, 2, 1
    Sleep 2000
    ExitApp
return

; Skript-Info beim Start
TrayTip, Voice Transcriber, Mittleres Mausrad aktiviert (Toggle-Modus), 2, 1