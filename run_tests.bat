@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title KiCad DIN Electrical - Testmenue

if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"

where python >nul 2>nul
if errorlevel 1 (
    cls
    echo ============================================================
    echo   FEHLER: Python wurde nicht gefunden
    echo ============================================================
    echo.
    echo Installiere Python 3.10 oder neuer und starte dieses Skript erneut.
    pause
    exit /b 1
)

python -c "import pytest" >nul 2>nul
if errorlevel 1 (
    cls
    echo ============================================================
    echo   FEHLER: pytest ist nicht installiert
    echo ============================================================
    echo.
    echo   python -m pip install -r requirements-dev.txt
    echo.
    pause
    exit /b 1
)

set "QUALITY_CMD=python -m tools.quality.run_quality --profile release --json-output build\Z_QUALITY_RESULTS.json --footprint footprints\Z_DIN_Module_18mm.pretty\Z_DIN_Module_18mm.kicad_mod symbols\Z_MCB.kicad_sym"

:menu
cls
echo ============================================================
echo   KiCad DIN Electrical - Tests und Werkzeuge
echo ============================================================
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
echo   [0] Programm verlassen
echo.
choice /c 1234567890 /n /m "Auswahl: "

if errorlevel 10 goto :end
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

:allchecks
cls
echo ============================================================
echo   Alle Pruefungen
echo ============================================================
echo.
echo [1/3] Vollstaendige Testsuite
echo.
python -m pytest -q
if errorlevel 1 goto :allchecks_failed

echo.
echo [2/3] Python-Syntaxpruefung
echo.
python -m compileall -q distributions tests tools
if errorlevel 1 goto :allchecks_failed

echo.
echo [3/3] Z_-Qualitaetspruefung fuer Symbol und Footprint
echo.
%QUALITY_CMD%
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
call :finish
goto :menu

:help
cls
echo ============================================================
echo   Hilfe
echo ============================================================
echo.
echo Z_-QUALITAETSPRUEFUNG
echo   Prueft das Referenzsymbol Z_MCB und den Referenzfootprint
 echo   Z_DIN_Module_18mm mit dem Release-Profil.
echo   Maschinenlesbare Ergebnisse:
echo   build\Z_QUALITY_RESULTS.json
echo.
echo BIBLIOTHEKSREFERENZ
echo   Auswahl 7 erzeugt die Indexdateien neu.
echo   Auswahl 8 prueft, ob sie aktuell sind.
echo.
echo WEITERE ANLEITUNG
echo   docs\02_User\TESTING.md
echo.
pause
goto :menu

:run
cls
echo ============================================================
echo   %~1
echo ============================================================
echo.
call %~2
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (
    echo Der Vorgang war erfolgreich.
) else (
    echo Der Vorgang ist fehlgeschlagen. Fehlercode: %RESULT%
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
