@echo off
setlocal EnableExtensions

cd /d "%~dp0\..\.."

set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

set "RESULT=0"

echo ============================================================
echo   ProjectOS - MCB-1P 3D-Export
echo ============================================================
echo.

echo [1/2] Pruefe OpenSCAD und FreeCADCmd ...
"%PYTHON_EXE%" tools\export_z_mcb_3d.py --check-tools
if errorlevel 1 (
    echo.
    echo FEHLER: Die benoetigten Werkzeuge wurden nicht vollstaendig gefunden.
    echo Installiere OpenSCAD und FreeCAD oder ergaenze sie im PATH.
    set "RESULT=2"
    goto :finish
)

echo.
echo [2/2] Erzeuge STEP und WRL ...
"%PYTHON_EXE%" tools\export_z_mcb_3d.py
if errorlevel 1 (
    echo.
    echo FEHLER: Der 3D-Export ist fehlgeschlagen.
    set "RESULT=1"
    goto :finish
)

echo.
echo Erfolgreich erzeugt:
echo   models\Z_MCB_1P\generated\Z_MCB_1P.step
echo   models\Z_MCB_1P\generated\Z_MCB_1P.wrl
echo.
echo Naechster Schritt: KiCad 3D-Viewer mit
echo   footprints\Z_MCB.pretty\Z_MCB_1P_18mm.kicad_mod
echo pruefen.

:finish
echo.
echo ============================================================
if "%RESULT%"=="0" (
    echo   Vorgang erfolgreich beendet.
) else (
    echo   Vorgang mit Fehlercode %RESULT% beendet.
)
echo ============================================================
echo.
echo Druecke eine beliebige Taste, um dieses Fenster zu schliessen ...
pause >nul
exit /b %RESULT%
