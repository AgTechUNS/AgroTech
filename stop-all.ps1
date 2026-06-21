$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Deteniendo todos los sistemas de AgroTech ==="

# Stop Mosquitto (Docker) — solo si Docker está disponible
try {
    $null = docker info 2>&1
    Write-Host "  deteniendo Mosquitto..."
    docker compose -f "$Root\deploy\broker\docker-compose.yml" down 2>$null
} catch {
    Write-Host "  (Docker no disponible, se salta Mosquitto)"
}

# Kill backend (uvicorn on port 8000)
netstat -ano | Select-String ":8000 " | ForEach-Object {
    $parts = $_ -split '\s+'
    $procId = $parts[-1]
    if ($procId -match '^\d+$') {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Write-Host "  detenido backend (PID $procId)"
    }
}

# Kill SPA (Next.js on port 3000)
netstat -ano | Select-String ":3000 " | ForEach-Object {
    $parts = $_ -split '\s+'
    $procId = $parts[-1]
    if ($procId -match '^\d+$') {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Write-Host "  detenido SPA (PID $procId)"
    }
}

# Kill MQTT bootstrap processes
Get-Process | Where-Object { $_.ProcessName -eq "python" } | ForEach-Object {
    try {
        $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
        if ($cmd -match "bootstrap") {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "  detenido ingestion (PID $($_.Id))"
        }
    } catch {}
}

# Kill sensor simulator processes
Get-Process | Where-Object { $_.ProcessName -eq "python" } | ForEach-Object {
    try {
        $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
        if ($cmd -match "lns_console") {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "  detenido simulador (PID $($_.Id))"
        }
    } catch {}
}

# Kill any leftover cmd.exe that were serving as hosts
foreach ($port in @(8000, 3000)) {
    netstat -ano | Select-String ":$port " | ForEach-Object {
        $parts = $_ -split '\s+'
        $procId = $parts[-1]
        if ($procId -match '^\d+$') {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host ""
Write-Host "=== Todos los sistemas detenidos ==="
