@echo off
setlocal EnableExtensions

cd /d "%~dp0\..\.."

set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo ============================================================
echo   ProjectOS - MCB-1P 3D-Export
echo ============================================================
echo.

echo [1/2] Pruefe OpenSCAD und FreeCADCmd ...
"%PYTHON_EXE%" tools\export_z_mcb_3d.py --check-tools
if errorlevel 1 (
    echo.
    echo Die benoetigten Werkzeuge wurden nicht vollstaendig gefunden.
    echo Installiere OpenSCAD und FreeCAD oder ergaenze sie im PATH.
    exit /b 2
)

echo.
echo [2/2] Erzeuge STEP und WRL ...
"%PYTHON_EXE%" tools\export_z_mcb_3d.py
if errorlevel 1 (
    echo.
    echo Der 3D-Export ist fehlgeschlagen.
    exit /b 1
)

echo.
echo Erfolgreich erzeugt:
echo   models\Z_MCB_1P\generated\Z_MCB_1P.step
echo   models\Z_MCB_1P\generated\Z_MCB_1P.wrl
echo.
echo Naechster Schritt: KiCad 3D-Viewer mit
 echo   footprints\Z_MCB.pretty\Z_MCB_1P_18mm.kicad_mod
 echo pruefen.

exit /b 0
