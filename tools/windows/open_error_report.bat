@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."

set "REPORT_FILE=build\FEHLERBERICHT.md"
set "REPORT_DIR=build"

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
 echo   [0] Zurueck
 echo.
choice /c 120 /n /m "Auswahl: "

if errorlevel 3 exit /b 0
if errorlevel 2 goto :open_folder
if errorlevel 1 goto :open_report
goto :menu

:open_report
start "" "%REPORT_FILE%"
goto :menu

:open_folder
start "" explorer.exe /select,"%CD%\%REPORT_FILE%"
goto :menu
