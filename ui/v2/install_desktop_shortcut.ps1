# Creates a Desktop shortcut for Evalathan (v0.3.1 desk) with the red dragon icon.
# Run once after download. Does not push or commit anything.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path -Parent (Split-Path -Parent $here)
$icon = Join-Path $here "assets\favicon.ico"
$bat = Join-Path $here "Evalathan.bat"
$desktop = [Environment]::GetFolderPath("Desktop")
$lnkPath = Join-Path $desktop "Evalathan (v0.3.1 desk).lnk"

@"
@echo off
cd /d "$repo"
start "" "http://127.0.0.1:8787/"
python ui\v2\serve.py
"@ | Set-Content -Path $bat -Encoding ASCII

$w = New-Object -ComObject WScript.Shell
$lnk = $w.CreateShortcut($lnkPath)
$lnk.TargetPath = $bat
$lnk.WorkingDirectory = $repo
$lnk.WindowStyle = 7
$lnk.Description = "EVALATHAN - Hydra GUI"
if (Test-Path $icon) { $lnk.IconLocation = "$icon,0" }
$lnk.Save()
Write-Host "Desktop shortcut created: $lnkPath"