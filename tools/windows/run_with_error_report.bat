@echo off
setlocal EnableExtensions

if "%~3"=="" (
    echo Verwendung:
    echo   run_with_error_report.bat "Pruefung" "Logdatei" Befehl [Argumente ...]
    exit /b 2
)

set "REPORT_TITLE=%~1"
set "REPORT_LOG=%~2"
shift
shift

set "COMMAND_ARGS="

:collect_command_args
if "%~1"=="" goto :run_command
set "COMMAND_ARGS=%COMMAND_ARGS% "%~1""
shift
goto :collect_command_args

:run_command
python -m tools.run_with_error_report ^
  --title "%REPORT_TITLE%" ^
  --log "%REPORT_LOG%" ^
  --report "build\FEHLERBERICHT.md" ^
  -- %COMMAND_ARGS%

set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo.
    echo ============================================================
    echo   Automatischer Fehlerbericht wurde erzeugt
    echo ============================================================
    echo.
    echo   Bericht: build\FEHLERBERICHT.md
    echo   Protokoll: %REPORT_LOG%
    echo.
    call "tools\windows\open_error_report.bat"
)

exit /b %RESULT%
