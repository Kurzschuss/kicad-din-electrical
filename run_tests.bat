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
    echo Installiere Python 3.10 oder neuer und starte dieses Skript
    echo danach erneut. Eine vorhandene .venv wird automatisch genutzt.
    echo.
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
    echo Fuehre im Repositoryordner einmal diesen Befehl aus:
    echo.
    echo   python -m pip install -r requirements-dev.txt
    echo.
    pause
    exit /b 1
)

:menu
cls
echo ============================================================
echo   KiCad DIN Electrical - Tests und Werkzeuge
echo ============================================================
echo.
echo Dieses Menue prueft die Bibliotheksstruktur, Dateinamen,
echo Symbol- und Footprint-Referenzen sowie weitere Projektregeln.
echo.
echo   [1] Schneller Testlauf
echo       Alle Tests mit kompakter Ausgabe.
echo.
echo   [2] Ausfuehrlicher Testlauf
echo       Zeigt jeden einzelnen Test und sein Ergebnis.
echo.
echo   [3] Alle Pruefungen
echo       Testsuite plus Python-Syntaxpruefung.
echo.
echo   [4] Beim ersten Fehler stoppen
echo       Hilfreich bei der Fehlersuche.
echo.
echo   [5] Nur zuletzt fehlgeschlagene Tests
echo       Wiederholt die Fehler des vorherigen Testlaufs.
echo.
echo   [6] Hilfe und Erklaerungen
echo       Hinweise zu Tests, .venv und Referenzgenerator.
echo.
echo   [7] Bibliotheksreferenz erzeugen
echo       Aktualisiert Symbol- und Footprint-Index.
echo.
echo   [8] Bibliotheksreferenz pruefen
echo       Prueft, ob die Indexdateien aktuell sind.
echo.
echo   [0] Programm verlassen
echo.
choice /c 123456780 /n /m "Auswahl: "

if errorlevel 9 goto :end
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

:allchecks
cls
echo ============================================================
echo   Alle Pruefungen
echo ============================================================
echo.
echo [1/2] Vollstaendige Testsuite
echo.
python -m pytest -q
if errorlevel 1 (
    set "RESULT=1"
    echo.
    echo FEHLER: Die Testsuite ist fehlgeschlagen.
    call :finish
    goto :menu
)

echo.
echo [2/2] Python-Syntaxpruefung
echo.
python -m compileall -q distributions tests tools
if errorlevel 1 (
    set "RESULT=1"
    echo.
    echo FEHLER: Die Python-Syntaxpruefung ist fehlgeschlagen.
) else (
    set "RESULT=0"
    echo.
    echo Alle Pruefungen waren erfolgreich.
)
call :finish
goto :menu

:help
cls
echo ============================================================
echo   Hilfe
echo ============================================================
echo.
echo SCHNELLER TESTLAUF
echo   Die normale Auswahl fuer eine vollstaendige Kontrolle.
echo.
echo AUSFUEHRLICHER TESTLAUF
echo   Zeigt Namen und Ergebnis jedes einzelnen Tests.
echo.
echo ALLE PRUEFUNGEN
echo   Fuehrt die Tests und die Python-Syntaxpruefung aus.
echo.
echo BIBLIOTHEKSREFERENZ
echo   Auswahl 7 erzeugt die beiden Indexdateien neu.
echo   Auswahl 8 prueft nur, ob sie dem Repository entsprechen.
echo.
echo .VENV
echo   Eine .venv ist eine lokale Python-Umgebung fuer dieses
echo   Projekt. Sie ist optional und wird automatisch aktiviert.
echo.
echo PROGRAMM VERLASSEN
echo   Mit der Taste 0 wird das Testmenue beendet.
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
