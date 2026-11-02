@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Always take published main when this folder is a git clone (old Tk desk -> browser desk).
if exist ".git\" (
  where git >nul 2>&1
  if not errorlevel 1 (
    echo Updating Evalathan to the published main tree...
    for /f "delims=" %%H in ('git rev-parse HEAD') do set "BEFORE=%%H"
    git fetch origin
    if not errorlevel 1 (
      git checkout main
      git reset --hard origin/main
      for /f "delims=" %%H in ('git rev-parse HEAD') do set "AFTER=%%H"
      if defined BEFORE if defined AFTER if /I not "%BEFORE%"=="%AFTER%" (
        if not defined EVALATHAN_RELAUNCHED (
          echo Update applied. Restarting launcher...
          endlocal
          set "EVALATHAN_RELAUNCHED=1"
          "%~f0" %*
          exit /b %ERRORLEVEL%
        )
      )
    ) else (
      echo git fetch failed. Continuing with the files already on disk.
    )
  )
)

set "PYLAUNCH="
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "PYLAUNCH=py -3"
if not defined PYLAUNCH (
  python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
  if not errorlevel 1 set "PYLAUNCH=python"
)
if not defined PYLAUNCH (
  echo Python 3.10 or newer was not found.
  echo Install it from https://www.python.org/downloads/windows/
  echo On the first installer page, tick Add python.exe to PATH.
  pause
  exit /b 1
)

if not exist "ui\v2\index.html" (
  echo ui\v2 is missing. This checkout is too old or incomplete.
  echo From this folder run:
  echo   git fetch origin
  echo   git checkout main
  echo   git reset --hard origin/main
  echo Then run launch.bat again. Expected: v0.3.2 local desk.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  %PYLAUNCH% -m venv .venv
  if errorlevel 1 (
    echo Could not create the private Python folder .venv
    pause
    exit /b 1
  )
)

set "VENVPY=%~dp0.venv\Scripts\python.exe"
call "%~dp0.venv\Scripts\activate.bat"

REM FUSS launching splash while pip / desk startup runs.
if exist "%~dp0ui\v2\launch_splash.py" (
  if exist "%USERPROFILE%\.evalathan\splash.stop" del /q "%USERPROFILE%\.evalathan\splash.stop" >nul 2>&1
  if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0ui\v2\launch_splash.py"
  ) else (
    start "" "%VENVPY%" "%~dp0ui\v2\launch_splash.py"
  )
)

"%VENVPY%" -m pip install -U pip
if errorlevel 1 (
  echo pip could not be updated.
  if exist "%~dp0ui\v2\launch_splash.py" "%VENVPY%" "%~dp0ui\v2\launch_splash.py" --close >nul 2>&1
  pause
  exit /b 1
)
"%VENVPY%" -m pip install -e "%~dp0."
if errorlevel 1 (
  echo Evalathan could not be installed.
  if exist "%~dp0ui\v2\launch_splash.py" "%VENVPY%" "%~dp0ui\v2\launch_splash.py" --close >nul 2>&1
  pause
  exit /b 1
)

echo.
echo Installing the Evalathan Desktop icon ^(red dragon^)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_desktop_app.ps1"
if errorlevel 1 (
  echo Desktop icon helper failed. You can still open Evalathan.bat in this folder.
)

echo.
echo Starting Evalathan v0.3.2 local desk window...
echo Look for the Evalathan icon on your Desktop ^(and Desktop\Evalathan\^).
echo Keep this console open while the desk is running, or use the Desktop icon next time.
echo.
"%VENVPY%" -c "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
set "EC=%ERRORLEVEL%"
if exist "%~dp0ui\v2\launch_splash.py" "%VENVPY%" "%~dp0ui\v2\launch_splash.py" --close >nul 2>&1
if not "%EC%"=="0" pause
exit /b %EC%
