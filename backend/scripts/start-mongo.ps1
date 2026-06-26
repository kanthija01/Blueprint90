# Start MongoDB for local Blueprint90 dev (no admin service required).
# Uses backend/.mongo-data — already gitignored.

$ErrorActionPreference = "Stop"

$BackendRoot = Split-Path $PSScriptRoot -Parent
$DbPath = Join-Path $BackendRoot ".mongo-data"
$Mongod = "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe"

if (-not (Test-Path $Mongod)) {
    Write-Error "mongod.exe not found at $Mongod. Install MongoDB Community or update this script."
}

$listening = Test-NetConnection -ComputerName 127.0.0.1 -Port 27017 -WarningAction SilentlyContinue
if ($listening.TcpTestSucceeded) {
    Write-Host "MongoDB already listening on localhost:27017"
    exit 0
}

New-Item -ItemType Directory -Force -Path $DbPath | Out-Null

Write-Host "Starting MongoDB (dbpath: $DbPath)..."
Start-Process -FilePath $Mongod `
    -ArgumentList @("--dbpath", $DbPath, "--port", "27017", "--bind_ip", "127.0.0.1") `
    -WindowStyle Hidden

Start-Sleep -Seconds 3
$check = Test-NetConnection -ComputerName 127.0.0.1 -Port 27017 -WarningAction SilentlyContinue
if (-not $check.TcpTestSucceeded) {
    Write-Error "MongoDB failed to start on port 27017."
}

Write-Host "MongoDB ready on mongodb://localhost:27017"
