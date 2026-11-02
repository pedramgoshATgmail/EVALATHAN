@echo off
REM Double-click or Desktop shortcut: opens the local Evalathan desk window.
setlocal
cd /d "%~dp0"

if not exist "ui\v2\index.html" (
  echo Evalathan files are missing. Run the README install block first.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo First-time setup: run launch.bat once, then use this icon.
  pause
  exit /b 1
)

set "VENVPY=%~dp0.venv\Scripts\python.exe"
"%VENVPY%" -c "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
if errorlevel 1 pause
endlocal
