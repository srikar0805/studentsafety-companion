$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent
Set-Location $ScriptDir
Write-Output "Starting Backend Server from Project Root: $ScriptDir"
uvicorn src.backend.app.main:app --reload --port 8000
