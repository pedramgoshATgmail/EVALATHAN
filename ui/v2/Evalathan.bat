@echo off
REM Prefer the repo-root Evalathan.bat (Desktop shortcut points there).
cd /d "%~dp0..\.."
if exist "Evalathan.bat" (
  call "Evalathan.bat"
  exit /b %ERRORLEVEL%
)
echo Run launch.bat once from the Evalathan program folder.
pause
