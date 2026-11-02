@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Update this clone from GitHub when possible (fixes stale desks when the folder already exists).
if exist ".git\" (
  where git >nul 2>&1
  if not errorlevel 1 (
    echo Checking GitHub for Evalathan updates...
    git fetch origin
    if not errorlevel 1 (
      for /f "delims=" %%H in ('git rev-parse HEAD') do set "BEFORE=%%H"
      git merge --ff-only origin/main
      if errorlevel 1 (
        echo.
        echo Fast-forward update failed. Local edits may block it.
        echo To take the published desk exactly:
        echo   git fetch origin
        echo   git reset --hard origin/main
        echo.
      ) else (
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
  echo   git reset --hard origin/main
  echo Then run launch.bat again. Expected: v0.3.1 browser desk.
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
"%VENVPY%" -m pip install -U pip
if errorlevel 1 (
  echo pip could not be updated.
  pause
  exit /b 1
)
"%VENVPY%" -m pip install -e "%~dp0."
if errorlevel 1 (
  echo Evalathan could not be installed.
  pause
  exit /b 1
)

echo.
echo Starting Evalathan v0.3.1 browser desk ^(not the old Tk HYDRA window^)...
echo Your browser should open http://127.0.0.1:8787/
echo Keep this window open while you use the desk.
echo.
"%VENVPY%" -c "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
if errorlevel 1 pause
endlocal
