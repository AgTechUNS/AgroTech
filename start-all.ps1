param(
    [switch]$Simulador,
    [switch]$SinBroker
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = "$Root\src"
$ErrorActionPreference = "Stop"

Write-Host "=== AgroTech - iniciando todos los sistemas ==="
Write-Host ""

# 1. FastAPI backend
Write-Host ">>> [1] FastAPI backend -> http://localhost:8000"
$bp = Start-Process -WindowStyle Normal -PassThru -FilePath "cmd.exe" `
    -ArgumentList "/k python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload" `
    -WorkingDirectory $Root

# 2. Next.js SPA
Write-Host ">>> [2] Next.js SPA -> http://localhost:3000"
$sp = Start-Process -WindowStyle Normal -PassThru -FilePath "cmd.exe" `
    -ArgumentList "/k npx next dev -p 3000" `
    -WorkingDirectory "$Root\agtech-spa"

# 3. Mosquitto broker (opcional, requiere Docker)
$dockerOk = $false
if (-not $SinBroker) {
    try {
        $null = docker info 2>&1
        $dockerOk = $true
    } catch {
        $dockerOk = $false
    }
}

if ($dockerOk) {
    Write-Host ">>> [3] Mosquitto MQTT broker (Docker)"
    Start-Process -WindowStyle Normal -PassThru -FilePath "cmd.exe" `
        -ArgumentList "/k docker compose -f deploy/broker/docker-compose.yml up" `
        -WorkingDirectory $Root

    Start-Sleep -Seconds 4

    Write-Host ">>> [4] MQTT ingestion pipeline (subscriber LoRaWAN -> InfluxDB)"
    Start-Process -WindowStyle Normal -PassThru -FilePath "cmd.exe" `
        -ArgumentList "/k python -m src.infrastructure.time_series_repo.bootstrap" `
        -WorkingDirectory $Root

    $stepMqtt = "3-4"
    $stepSim = "5"
} else {
    Write-Host ">>> [!] Docker no disponible - se salta Mosquitto + ingestion MQTT"
    Write-Host "       Para que el pipeline MQTT funcione instalá Docker Desktop"
    Write-Host "       y ejecutá: docker compose -f deploy/broker/docker-compose.yml up -d"
    $stepMqtt = "-"
    $stepSim = "3"
}

# 5 (o 3). Sensor simulator (opcional)
if ($Simulador) {
    if ($dockerOk) {
        Write-Host ">>> [$stepSim] Sensor simulator (curses TUI)"
    } else {
        Write-Host ">>> [$stepSim] Sensor simulator (curses TUI - necesita Mosquitto en localhost:1883)"
    }
    Start-Process -WindowStyle Normal -PassThru -FilePath "cmd.exe" `
        -ArgumentList "/k python tools/simulador_sensores/lns_console.py" `
        -WorkingDirectory $Root
}

Write-Host ""
Write-Host "=== AgroTech iniciado ==="
Write-Host ""
Write-Host "  Backend:   http://localhost:8000"
Write-Host "  SPA:       http://localhost:3000"
Write-Host ""
if (-not $dockerOk) {
    Write-Host "  (MQTT saltado - Docker no disponible)"
    Write-Host ""
}
Write-Host "  Login:     test@agtechuns.com / password123"
Write-Host ""
Write-Host "Para detener: .\stop-all.ps1"
