# Puts Evalathan on the Desktop with the red-dragon icon.
# Program files stay in this clone folder (local). The shortcut only opens them.
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$icon = Join-Path $repo "ui\v2\assets\favicon.ico"
if (-not (Test-Path $icon)) {
  $icon = Join-Path $repo "ui\v2\assets\evalathan-app-icon.png"
}
$launcher = Join-Path $repo "Evalathan.bat"
$desktop = [Environment]::GetFolderPath("Desktop")
$appDir = Join-Path $desktop "Evalathan"
New-Item -ItemType Directory -Force -Path $appDir | Out-Null

# Folder on Desktop that holds the clickable app entry.
$folderLnk = Join-Path $appDir "Evalathan.lnk"
$deskLnk = Join-Path $desktop "Evalathan.lnk"

$shell = New-Object -ComObject WScript.Shell
foreach ($lnkPath in @($folderLnk, $deskLnk)) {
  $lnk = $shell.CreateShortcut($lnkPath)
  $lnk.TargetPath = $launcher
  $lnk.WorkingDirectory = $repo
  $lnk.WindowStyle = 7
  $lnk.Description = "EVALATHAN - local Hydra desk"
  if (Test-Path $icon) {
    if ($icon.ToLower().EndsWith(".ico")) {
      $lnk.IconLocation = "$icon,0"
    }
  }
  $lnk.Save()
}

$readme = @"
EVALATHAN (local)

This folder is only a launcher. The program itself lives here:
$repo

Double-click Evalathan.lnk (or the Evalathan icon on your Desktop).
It opens the local desk window. Nothing is hosted on a public website.
"@
Set-Content -Path (Join-Path $appDir "README.txt") -Value $readme -Encoding UTF8

Write-Host "Desktop icon: $deskLnk"
Write-Host "Desktop folder: $appDir"
Write-Host "Program folder (local): $repo"
