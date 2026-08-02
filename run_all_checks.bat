@echo off
setlocal
cd /d "%~dp0"
title KiCad DIN Electrical - All Checks

echo ============================================
echo   KiCad DIN Electrical - All Checks
echo ============================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

where python >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python wurde nicht gefunden.
    pause
    exit /b 1
)

echo [1/2] Vollstaendige Testsuite
python -m pytest -q
if errorlevel 1 (
    set "CHECK_EXIT=%ERRORLEVEL%"
    echo.
    echo FEHLER: Testsuite fehlgeschlagen.
    pause
    exit /b %CHECK_EXIT%
)

echo.
echo [2/2] Python-Syntaxpruefung
python -m compileall -q distributions tests
if errorlevel 1 (
    set "CHECK_EXIT=%ERRORLEVEL%"
    echo.
    echo FEHLER: Python-Syntaxpruefung fehlgeschlagen.
    pause
    exit /b %CHECK_EXIT%
)

echo.
echo Alle Pruefungen waren erfolgreich.
echo.
pause
exit /b 0
