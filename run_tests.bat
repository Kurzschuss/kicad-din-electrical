@echo off
setlocal
cd /d "%~dp0"
title KiCad DIN Electrical - Test Suite

echo ============================================
echo   KiCad DIN Electrical - Test Suite
echo ============================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

where python >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python wurde nicht gefunden.
    echo Installiere Python oder aktiviere die virtuelle Umgebung.
    pause
    exit /b 1
)

python -m pytest -q
set "TEST_EXIT=%ERRORLEVEL%"

echo.
if "%TEST_EXIT%"=="0" (
    echo Alle Tests waren erfolgreich.
) else (
    echo Tests fehlgeschlagen. Fehlercode: %TEST_EXIT%
)

echo.
pause
exit /b %TEST_EXIT%
