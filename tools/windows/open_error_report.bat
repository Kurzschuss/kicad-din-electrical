@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."

set "REPORT_FILE=build\FEHLERBERICHT.md"
set "REPORT_DIR=build"
set "ISSUE_PREVIEW=build\GITHUB_ISSUE_VORSCHAU.md"
set "ISSUE_TITLE=build\GITHUB_ISSUE_TITEL.txt"

if not exist "%REPORT_FILE%" (
    echo.
    echo Kein Fehlerbericht gefunden:
    echo   %REPORT_FILE%
    echo.
    exit /b 1
)

:menu
echo.
echo ============================================================
echo   Fehlerbericht
echo ============================================================
echo.
echo   [1] Fehlerbericht oeffnen
echo   [2] Fehlerordner im Explorer oeffnen
echo   [3] GitHub-Issue-Vorschau erzeugen und oeffnen
echo   [0] Zurueck
echo.
choice /c 1230 /n /m "Auswahl: "

if errorlevel 4 exit /b 0
if errorlevel 3 goto :open_issue_preview
if errorlevel 2 goto :open_folder
if errorlevel 1 goto :open_report
goto :menu

:open_report
start "" "%REPORT_FILE%"
goto :menu

:open_folder
start "" explorer.exe /select,"%CD%\%REPORT_FILE%"
goto :menu

:open_issue_preview
python -m tools.create_github_issue_preview
if errorlevel 1 (
    echo.
    echo Die GitHub-Issue-Vorschau konnte nicht erzeugt werden.
    echo Es wurde nichts veroeffentlicht.
    echo.
    goto :menu
)

echo.
echo Lokale GitHub-Issue-Vorschau wurde erzeugt:
echo   Titel:    %ISSUE_TITLE%
echo   Vorschau: %ISSUE_PREVIEW%
echo.
echo Es wurde nichts auf GitHub veroeffentlicht.
start "" "%ISSUE_PREVIEW%"
goto :menu
