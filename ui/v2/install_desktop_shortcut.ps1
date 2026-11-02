# Thin wrapper: root installer creates the Desktop Evalathan icon.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
& (Join-Path $root "install_desktop_app.ps1")
