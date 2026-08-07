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
    echo Installiere Python 3.11 oder neuer und starte dieses Skript erneut.
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
    python -m venv .venv
    if errorlevel 1 (
        echo FEHLER: Die virtuelle Umgebung konnte nicht erstellt werden.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo FEHLER: .venv konnte nicht aktiviert werden.
    pause
    exit /b 1
)

call :ensure_dev_environment startup
if errorlevel 1 exit /b 1

call "tools\windows\detect_kicad.bat"
set "QUALITY_CMD=python -m tools.quality.run_quality --profile release --json-output build\Z_QUALITY_RESULTS.json --footprint footprints\Z_DIN_Module_18mm.pretty\Z_DIN_Module_18mm.kicad_mod symbols\Z_MCB.kicad_sym"
set "HEALTH_TEST=tests\test_projectos_repository_consistency.py"

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
echo.
echo   AUTOMATISCHE FEHLERBERICHTE
echo   Fehlgeschlagene Pruefungen erzeugen build\FEHLERBERICHT.md
echo   und bieten eine lokale Aktion zur Erstellung eines GitHub-Issue an.
echo.
echo   [1] Schneller Testlauf
echo   [2] Ausfuehrlicher Testlauf
echo   [3] Alle Pruefungen
echo   [4] Beim ersten Fehler stoppen
echo   [5] Nur zuletzt fehlgeschlagene Tests
echo   [6] Repository-Health-Check
echo   [7] Bibliotheksreferenz erzeugen
echo   [8] Bibliotheksreferenz pruefen
echo   [9] Z_-Qualitaetspruefung fuer Symbol und Footprint
echo   [A] KiCad-Umgebungsvariablen anzeigen
echo   [T] 3D-Werkzeuge OpenSCAD/FreeCAD pruefen
echo   [I] Entwicklungsumgebung reparieren
echo   [0] Programm verlassen
echo.
choice /c 123456789ATI0 /n /m "Auswahl: "

if errorlevel 13 goto :end
if errorlevel 12 goto :repair_environment
if errorlevel 11 goto :toolchain
if errorlevel 10 goto :environment
if errorlevel 9 goto :quality
if errorlevel 8 goto :referencecheck
if errorlevel 7 goto :referencewrite
if errorlevel 6 goto :healthonly
if errorlevel 5 goto :lastfailed
if errorlevel 4 goto :firstfailure
if errorlevel 3 goto :allchecks
if errorlevel 2 goto :verbose
if errorlevel 1 goto :quick
goto :menu

:quick
call :run_pytest "Schneller Testlauf" "python -m pytest -q"
goto :menu

:verbose
call :run_pytest "Ausfuehrlicher Testlauf" "python -m pytest -vv"
goto :menu

:firstfailure
call :run_pytest "Testlauf bis zum ersten Fehler" "python -m pytest -x"
goto :menu

:lastfailed
call :run_pytest "Zuletzt fehlgeschlagene Tests" "python -m pytest --lf"
goto :menu

:healthonly
call :run "Repository-Health-Check" "python -m pytest -q %HEALTH_TEST%"
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

:toolchain
call :run "3D-Werkzeuge OpenSCAD/FreeCAD" "python tools\export_z_mcb_3d.py --check-tools"
goto :menu

:allchecks
cls
echo ============================================================
echo   Alle Pruefungen
 echo ============================================================
echo.

echo [1/5] Repository-Health-Check
echo.
call "tools\windows\run_with_error_report.bat" "Repository-Health-Check" "build\ALLE_PRUEFUNGEN_HEALTH.log" python -m pytest -q %HEALTH_TEST%
if errorlevel 1 goto :allchecks_failed

echo.
echo [2/5] Vollstaendige Testsuite
echo.
call "tools\windows\run_with_error_report.bat" "Vollstaendige Testsuite" "build\ALLE_PRUEFUNGEN_PYTEST.log" python -m pytest -q
if errorlevel 1 goto :allchecks_failed

echo.
echo [3/5] Python-Syntaxpruefung
echo.
call "tools\windows\run_with_error_report.bat" "Python-Syntaxpruefung" "build\ALLE_PRUEFUNGEN_SYNTAX.log" python -m compileall -q distributions tests tools
if errorlevel 1 goto :allchecks_failed

echo.
echo [4/5] 3D-Werkzeuge OpenSCAD/FreeCAD
echo.
call "tools\windows\run_with_error_report.bat" "3D-Werkzeuge OpenSCAD/FreeCAD" "build\ALLE_PRUEFUNGEN_3D_WERKZEUGE.log" python tools\export_z_mcb_3d.py --check-tools
if errorlevel 1 goto :allchecks_failed

echo.
echo [5/5] Z_-Qualitaetspruefung fuer Symbol und Footprint
echo.
call "tools\windows\run_with_error_report.bat" "Z_-Qualitaetspruefung" "build\ALLE_PRUEFUNGEN_QUALITAET.log" %QUALITY_CMD%
if errorlevel 1 goto :allchecks_failed

echo.
echo Alle Pruefungen waren erfolgreich.
call :finish
goto :menu

:allchecks_failed
echo.
echo FEHLER: Mindestens eine Pruefung ist fehlgeschlagen.
echo Ausfuehrlicher Bericht: build\FEHLERBERICHT.md
echo Das zugehoerige Schrittprotokoll liegt unter build\.
call :finish
goto :menu

:run_pytest
call :repository_health
if errorlevel 1 exit /b 1
call :run "%~1" "%~2"
exit /b %ERRORLEVEL%

:repository_health
cls
echo ============================================================
echo   Repository-Health-Check
 echo ============================================================
echo.
echo Pruefe AP-Nummern, Arbeitsstand, Fehlercodes und Paketexporte ...
call "tools\windows\run_with_error_report.bat" "Repository-Health-Check" "build\REPOSITORY_HEALTH.log" python -m pytest -q %HEALTH_TEST%
set "HEALTH_RESULT=%ERRORLEVEL%"
if not "%HEALTH_RESULT%"=="0" (
    echo.
    echo FEHLER: Der Repository-Health-Check ist fehlgeschlagen.
    echo Der eigentliche Testlauf wird nicht gestartet.
    echo Bericht: build\FEHLERBERICHT.md
    echo Protokoll: build\REPOSITORY_HEALTH.log
    call :finish
)
exit /b %HEALTH_RESULT%

:repair_environment
cls
echo ============================================================
echo   Entwicklungsumgebung reparieren
 echo ============================================================
echo.
choice /c JN /n /m "Reparatur jetzt starten? [J/N]: "
if errorlevel 2 goto :menu
call :ensure_dev_environment repair
call :finish
goto :menu

:environment
cls
echo ============================================================
echo   KiCad-Umgebungsvariablen
 echo ============================================================
echo.
set KICAD_ 2>nul
if errorlevel 1 echo Keine KICAD_-Variablen im aktuellen Prozess vorhanden.
echo.
echo KICAD_Z_-Registrierung: %KICAD_Z_REGISTRATION%
echo KICAD_Z_-Stammordner : %KICAD_Z_ROOT_DIR%
echo.
pause
goto :menu

:ensure_dev_environment
set "DEV_MODE=%~1"
echo.
echo Pruefe pip und Entwicklungsabhaengigkeiten ...
python -m pip --version >nul 2>nul
if errorlevel 1 (
    python -m ensurepip --upgrade
    if errorlevel 1 goto :dev_environment_failed
)
if /I "%DEV_MODE%"=="repair" (
    python -m pip install --disable-pip-version-check --upgrade pip
    if errorlevel 1 goto :dev_environment_failed
)
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
echo FEHLER: Entwicklungsumgebung ist nicht vollstaendig.
echo Fuehre bei Bedarf manuell aus:
echo   .venv\Scripts\activate.bat
echo   python -m pip install -r requirements-dev.txt
set "DEV_MODE="
pause
exit /b 1

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
    echo Bericht: build\FEHLERBERICHT.md
    echo Protokoll: build\LETZTER_TESTLAUF.log
)
call :finish
exit /b %RESULT%

:finish
echo.
echo Druecke eine Taste, um zum Hauptmenue zurueckzukehren.
pause >nul
exit /b 0

:end
cls
echo Testmenue beendet.
timeout /t 1 >nul
exit /b 0
