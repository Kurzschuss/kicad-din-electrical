@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title KiCad DIN Electrical - Testmenue

where python >nul 2>nul
if errorlevel 1 (
    cls
    echo ============================================================
    echo   FEHLER: Python wurde nicht gefunden
    echo ============================================================
    echo.
    echo Installiere Python 3.10 oder neuer und starte dieses Skript erneut.
    echo Achte bei der Installation auf die Option "Python zu PATH hinzufuegen".
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    cls
    echo ============================================================
    echo   Entwicklungsumgebung wird eingerichtet
    echo ============================================================
    echo.
    echo Erzeuge die virtuelle Python-Umgebung .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo FEHLER: Die virtuelle Umgebung konnte nicht erstellt werden.
        echo Pruefe die Python-Installation und fuehre bei Bedarf aus:
        echo   python -m venv .venv
        echo.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    cls
    echo ============================================================
    echo   FEHLER: .venv konnte nicht aktiviert werden
    echo ============================================================
    echo.
    echo Loesche bei einer beschaedigten Umgebung den Ordner .venv
    echo und starte run_tests.bat danach erneut.
    echo.
    pause
    exit /b 1
)

call :ensure_dev_environment startup
if errorlevel 1 exit /b 1

call "tools\windows\detect_kicad.bat"

set "QUALITY_CMD=python -m tools.quality.run_quality --profile release --json-output build\Z_QUALITY_RESULTS.json --footprint footprints\Z_DIN_Module_18mm.pretty\Z_DIN_Module_18mm.kicad_mod symbols\Z_MCB.kicad_sym"

:menu
cls
echo ============================================================
echo   KiCad DIN Electrical - Tests und Werkzeuge
echo ============================================================
echo.
if defined KICAD_CLI (
    echo   KiCad CLI        : %KICAD_CLI%
) else (
    echo   KiCad CLI        : nicht gefunden
)
echo   Python-Umgebung     : %CD%\.venv
echo   KiCad Benutzerordner: %KICAD_USER_DIR%
echo   Z_-Stammordner      : %KICAD_Z_ROOT_DIR%
if "%KICAD_Z_REGISTRATION%"=="OK" (
    if not "%KICAD_Z_REGISTERED%"=="0" echo   Z_-Registrierung  : %KICAD_Z_REGISTERED% Eintraege neu hinzugefuegt
    if "%KICAD_Z_REGISTERED%"=="0" echo   Z_-Registrierung  : alle Eintraege bereits vorhanden
) else (
    echo   Z_-Registrierung  : noch keine KiCad-Konfiguration gefunden
)
echo.
echo   [1] Schneller Testlauf
echo   [2] Ausfuehrlicher Testlauf
echo   [3] Alle Pruefungen
echo   [4] Beim ersten Fehler stoppen
echo   [5] Nur zuletzt fehlgeschlagene Tests
echo   [6] Hilfe und Erklaerungen
echo   [7] Bibliotheksreferenz erzeugen
echo   [8] Bibliotheksreferenz pruefen
echo   [9] Z_-Qualitaetspruefung fuer Symbol und Footprint
echo   [A] KiCad-Umgebungsvariablen anzeigen
echo   [I] Entwicklungsumgebung reparieren
echo   [0] Programm verlassen
echo.
choice /c 123456789AI0 /n /m "Auswahl: "

if errorlevel 12 goto :end
if errorlevel 11 goto :repair_environment
if errorlevel 10 goto :environment
if errorlevel 9 goto :quality
if errorlevel 8 goto :referencecheck
if errorlevel 7 goto :referencewrite
if errorlevel 6 goto :help
if errorlevel 5 goto :lastfailed
if errorlevel 4 goto :firstfailure
if errorlevel 3 goto :allchecks
if errorlevel 2 goto :verbose
if errorlevel 1 goto :quick
goto :menu

:quick
call :run "Schneller Testlauf" "python -m pytest -q"
goto :menu

:verbose
call :run "Ausfuehrlicher Testlauf" "python -m pytest -vv"
goto :menu

:firstfailure
call :run "Testlauf bis zum ersten Fehler" "python -m pytest -x"
goto :menu

:lastfailed
call :run "Zuletzt fehlgeschlagene Tests" "python -m pytest --lf"
goto :menu

:referencewrite
call :run "Bibliotheksreferenz erzeugen" "python tools\generate_library_reference.py"
goto :menu

:referencecheck
call :run "Bibliotheksreferenz pruefen" "python tools\generate_library_reference.py --check"
goto :menu

:quality
call :run "Z_-Qualitaetspruefung" "%QUALITY_CMD%"
goto :menu

:repair_environment
cls
echo ============================================================
echo   Entwicklungsumgebung reparieren
 echo ============================================================
echo.
echo Dabei werden pip und alle Eintraege aus requirements-dev.txt
 echo geprueft und bei Bedarf installiert oder aktualisiert.
echo.
choice /c JN /n /m "Reparatur jetzt starten? [J/N]: "
if errorlevel 2 goto :menu
call :ensure_dev_environment repair
echo.
if errorlevel 1 (
    echo Die Reparatur ist fehlgeschlagen.
) else (
    echo Die Entwicklungsumgebung ist einsatzbereit.
)
echo.
pause
goto :menu

:environment
cls
echo ============================================================
echo   KiCad-Umgebungsvariablen - Name und Pfad
echo ============================================================
echo.
echo Vorhandene KiCad-Variablen
echo ------------------------------------------------------------
set KICAD_ 2>nul
if errorlevel 1 echo Keine KICAD_-Variablen im aktuellen Prozess vorhanden.
echo.
echo KICAD_Z_-Registrierung
echo ------------------------------------------------------------
if "%KICAD_Z_REGISTRATION%"=="NO_CONFIG_ROOT" (
    echo [HINWEIS] KiCad wurde noch nicht gestartet oder besitzt noch keinen
    echo           Konfigurationsordner. Folgende Eintraege fehlen und werden
    echo           beim naechsten Start dieses Testmenues automatisch hinzugefuegt:
    call :show_names "%KICAD_Z_MISSING_NAMES%" "[FEHLT]"
) else if "%KICAD_Z_REGISTRATION%"=="NO_CONFIG_FILE" (
    echo [HINWEIS] Noch keine kicad_common.json gefunden. Folgende Eintraege
    echo           werden automatisch hinzugefuegt, sobald KiCad eine Konfiguration angelegt hat:
    call :show_names "%KICAD_Z_MISSING_NAMES%" "[FEHLT]"
) else (
    if defined KICAD_Z_MISSING_NAMES (
        echo Vor der Pruefung fehlende Eintraege:
        call :show_names "%KICAD_Z_MISSING_NAMES%" "[FEHLT - wird hinzugefuegt]"
        echo.
    )
    if defined KICAD_Z_ADDED_NAMES (
        echo Neu registriert:
        call :show_names "%KICAD_Z_ADDED_NAMES%" "[OK - hinzugefuegt]"
        echo.
    )
    if defined KICAD_Z_EXISTING_NAMES (
        echo Bereits korrekt vorhanden:
        call :show_names "%KICAD_Z_EXISTING_NAMES%" "[OK]"
        echo.
    )
    if defined KICAD_Z_MISMATCH_NAMES (
        echo Abweichende vorhandene Pfade:
        call :show_names "%KICAD_Z_MISMATCH_NAMES%" "[ACHTUNG - nicht ueberschrieben]"
        echo Diese Werte bleiben aus Sicherheitsgruenden unveraendert.
        echo.
    )
)
echo Allgemeine KiCad-Variablen werden nur angezeigt und nicht veraendert.
echo.
pause
goto :menu

:allchecks
cls
echo ============================================================
echo   Alle Pruefungen
echo ============================================================
echo.
echo [1/3] Vollstaendige Testsuite
echo.
call "tools\windows\run_with_error_report.bat" "Vollstaendige Testsuite" "build\ALLE_PRUEFUNGEN_PYTEST.log" python -m pytest -q
if errorlevel 1 goto :allchecks_failed

echo.
echo [2/3] Python-Syntaxpruefung
echo.
call "tools\windows\run_with_error_report.bat" "Python-Syntaxpruefung" "build\ALLE_PRUEFUNGEN_SYNTAX.log" python -m compileall -q distributions tests tools
if errorlevel 1 goto :allchecks_failed

echo.
echo [3/3] Z_-Qualitaetspruefung fuer Symbol und Footprint
echo.
call "tools\windows\run_with_error_report.bat" "Z_-Qualitaetspruefung" "build\ALLE_PRUEFUNGEN_QUALITAET.log" %QUALITY_CMD%
if errorlevel 1 goto :allchecks_failed

set "RESULT=0"
echo.
echo Alle Pruefungen waren erfolgreich.
call :finish
goto :menu

:allchecks_failed
set "RESULT=1"
echo.
echo FEHLER: Mindestens eine Pruefung ist fehlgeschlagen.
echo.
echo Ausfuehrlicher Bericht:
echo   build\FEHLERBERICHT.md
echo Das zugehoerige Schrittprotokoll wurde unter build\ gespeichert.
call :finish
goto :menu

:help
cls
echo ============================================================
echo   Hilfe
echo ============================================================
echo.
echo ENTWICKLUNGSUMGEBUNG
echo   Beim ersten Start wird automatisch die virtuelle Umgebung .venv
 echo   angelegt und aktiviert. Anschliessend werden pip und alle Pakete
 echo   aus requirements-dev.txt geprueft und bei Bedarf installiert.
echo   Auswahl I wiederholt diese Pruefung und aktualisiert dabei auch pip.
echo   Die globale Python-Installation wird nicht mit Projektpaketen befuellt.
echo.
echo KICAD-ERKENNUNG
echo   Nach der Python-Einrichtung wird kicad-cli.exe ueber PATH und
 echo   anschliessend in den ueblichen Installationsordnern gesucht.
echo   Der gefundene bin-Ordner wird fuer diesen Lauf zu PATH hinzugefuegt.
echo.
echo KICAD-BENUTZERORDNER
echo   Im tatsaechlichen Windows-Dokumenteordner wird der Ordner kicad
 echo   geprueft und bei Bedarf mit diesen Unterordnern angelegt:
echo   3dmodels, 3rdparty, footprints, plugins, projects, scripting,
echo   symbols und template. Vorhandene Inhalte werden nicht veraendert.
echo.
echo KICAD_Z_-UMGEBUNGSVARIABLEN
echo   Fehlende KICAD_Z_-Eintraege werden vor der Registrierung angezeigt,
echo   automatisch in KiCad hinzugefuegt und anschliessend bestaetigt.
echo   Abweichende vorhandene Pfade werden angezeigt, aber nicht ueberschrieben.
echo   Auswahl A zeigt alle Namen, Pfade und den Registrierungsstatus an.
echo.
echo Z_-QUALITAETSPRUEFUNG
echo   Prueft das Referenzsymbol Z_MCB und den Referenzfootprint
 echo   Z_DIN_Module_18mm mit dem Release-Profil.
echo   Maschinenlesbare Ergebnisse:
echo   build\Z_QUALITY_RESULTS.json
echo.
echo AUTOMATISCHE FEHLERBERICHTE
echo   Einzelpruefungen und der kombinierte Lauf werden live angezeigt
 echo   und gleichzeitig protokolliert. Bei einem Fehler entsteht automatisch:
echo   build\FEHLERBERICHT.md
echo   Die zugehoerige Logdatei liegt ebenfalls unter build\.
echo   Der Markdown-Bericht kann nach einer kurzen Sichtpruefung als Grundlage
 echo   fuer ein GitHub-Issue verwendet werden.
echo.
echo BIBLIOTHEKSREFERENZ
echo   Auswahl 7 erzeugt die Indexdateien neu.
echo   Auswahl 8 prueft, ob sie aktuell sind.
echo.
echo WEITERE ANLEITUNG
echo   docs\02_User\TESTING.md
echo   docs\03_Developer\FEHLERBERICHTE.md
echo.
pause
goto :menu

:ensure_dev_environment
set "DEV_MODE=%~1"
echo.
echo Pruefe pip ...
python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo pip wurde nicht gefunden. Versuche ensurepip ...
    python -m ensurepip --upgrade
    if errorlevel 1 goto :dev_environment_failed
)

if /I "%DEV_MODE%"=="repair" (
    echo Aktualisiere pip ...
    python -m pip install --disable-pip-version-check --upgrade pip
    if errorlevel 1 goto :dev_environment_failed
)

echo Pruefe Entwicklungsabhaengigkeiten ...
python -m pip install --disable-pip-version-check -r requirements-dev.txt
if errorlevel 1 goto :dev_environment_failed

python -m pip check
if errorlevel 1 goto :dev_environment_failed

python -c "import pytest" >nul 2>nul
if errorlevel 1 goto :dev_environment_failed

echo [OK] Entwicklungsumgebung ist vollstaendig.
set "DEV_MODE="
exit /b 0

:dev_environment_failed
echo.
echo ============================================================
echo   FEHLER: Entwicklungsumgebung ist nicht vollstaendig
 echo ============================================================
echo.
echo Pruefe die Internetverbindung und die Python-/pip-Installation.
echo Fuehre bei Bedarf in diesem Repository manuell aus:
echo.
echo   .venv\Scripts\activate.bat
 echo   python -m pip install -r requirements-dev.txt
 echo   python -m pip check
echo.
set "DEV_MODE="
pause
exit /b 1

:show_names
set "Z_NAME_LIST=%~1"
if not defined Z_NAME_LIST exit /b 0
for %%V in (%Z_NAME_LIST:;= %) do echo   %~2 %%V
set "Z_NAME_LIST="
exit /b 0

:run
cls
echo ============================================================
echo   %~1
echo ============================================================
echo.
call "tools\windows\run_with_error_report.bat" "%~1" "build\LETZTER_TESTLAUF.log" %~2
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (
    echo Der Vorgang war erfolgreich.
) else (
    echo Der Vorgang ist fehlgeschlagen. Fehlercode: %RESULT%
    echo.
    echo Ausfuehrlicher Bericht:
    echo   build\FEHLERBERICHT.md
    echo Konsolenprotokoll:
    echo   build\LETZTER_TESTLAUF.log
)
call :finish
exit /b %RESULT%

:finish
echo.
echo Druecke eine Taste, um zum Hauptmenue zurueckzukehren.
pause >nul
exit /b

:end
cls
echo Testmenue beendet.
timeout /t 1 >nul
exit /b 0
