<#
.SYNOPSIS
  Coleta um retrato do hardware e das configurações relevantes para FPS e salva em JSON.
  Não altera nada no sistema.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\windows\01-coletar-sistema.ps1
#>
param(
    [string]$Saida = (Join-Path $PSScriptRoot "..\..\runs\sistema-$(Get-Date -Format yyyyMMdd-HHmmss).json")
)
$ErrorActionPreference = 'Continue'

function Get-RegValue($Path, $Name) {
    try { (Get-ItemProperty -Path $Path -Name $Name -ErrorAction Stop).$Name } catch { $null }
}

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$os  = Get-CimInstance Win32_OperatingSystem
$ram = Get-CimInstance Win32_PhysicalMemory
$gpus = Get-CimInstance Win32_VideoController
$board = Get-CimInstance Win32_BaseBoard
$bios = Get-CimInstance Win32_BIOS

$vbs = $null
try {
    $dg = Get-CimInstance -Namespace root\Microsoft\Windows\DeviceGuard -ClassName Win32_DeviceGuard -ErrorAction Stop
    $vbs = @{
        VBSStatus = $dg.VirtualizationBasedSecurityStatus  # 0=desligado, 1=habilitado, 2=rodando
        ServicosRodando = $dg.SecurityServicesRunning      # 2 = HVCI (Integridade de memória)
    }
} catch {}

$nvidia = $null
$smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($smi) {
    $nvidia = & nvidia-smi --query-gpu=name,driver_version,memory.total,pcie.link.gen.max,pcie.link.gen.current,pcie.link.width.current,power.limit,clocks.max.graphics,clocks.max.memory --format=csv,noheader 2>$null
}

$maxRamSpeed = ($ram | Measure-Object -Property Speed -Maximum).Maximum
$cfgRamSpeed = ($ram | Measure-Object -Property ConfiguredClockSpeed -Maximum).Maximum

$info = [ordered]@{
    ColetadoEm = (Get-Date).ToString('s')
    Windows = @{ Nome = $os.Caption; Versao = $os.Version; Build = $os.BuildNumber }
    PlacaMae = @{ Fabricante = $board.Manufacturer; Modelo = $board.Product; BIOS = $bios.SMBIOSBIOSVersion; DataBIOS = $bios.ReleaseDate }
    CPU = @{ Nome = $cpu.Name.Trim(); Nucleos = $cpu.NumberOfCores; Threads = $cpu.NumberOfLogicalProcessors; ClockMaxMHz = $cpu.MaxClockSpeed }
    RAM = @{
        TotalGB = [math]::Round(($ram | Measure-Object -Property Capacity -Sum).Sum / 1GB, 1)
        Pentes = $ram.Count
        VelocidadeNominalMTs = $maxRamSpeed
        VelocidadeConfiguradaMTs = $cfgRamSpeed
        Modulos = @($ram | ForEach-Object { "$($_.Manufacturer) $("$($_.PartNumber)".Trim()) $([math]::Round($_.Capacity/1GB))GB @ $($_.ConfiguredClockSpeed)" })
    }
    GPUs = @($gpus | ForEach-Object { @{ Nome = $_.Name; Driver = $_.DriverVersion; Resolucao = "$($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)"; HzAtual = $_.CurrentRefreshRate } })
    NvidiaSmi = $nvidia
    PlanoEnergia = (powercfg /getactivescheme) -join ' '
    GameMode = Get-RegValue 'HKCU:\Software\Microsoft\GameBar' 'AutoGameModeEnabled'
    GameDVR = Get-RegValue 'HKCU:\System\GameConfigStore' 'GameDVR_Enabled'
    CapturaEmSegundoPlano = Get-RegValue 'HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR' 'AppCaptureEnabled'
    HAGS = Get-RegValue 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers' 'HwSchMode'  # 2 = ligado
    OtimizacaoJanelaDX = Get-RegValue 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences' 'DirectXUserGlobalSettings'
    VBS = $vbs
    ProgramasNaInicializacao = @(Get-CimInstance Win32_StartupCommand | Select-Object -ExpandProperty Name)
}

# Alertas rápidos
$alertas = @()
if ($cfgRamSpeed -and $maxRamSpeed -and $cfgRamSpeed -lt $maxRamSpeed) { $alertas += "RAM rodando abaixo da velocidade nominal ($cfgRamSpeed < $maxRamSpeed): verifique XMP/EXPO na BIOS." }
$intelBloqueado = ($cpu.Name -match 'Intel') -and ($cpu.Name -notmatch '\d{4,5}K') -and ($board.Product -notmatch 'Z\d{3}')
if ($cfgRamSpeed -and $cfgRamSpeed -le 2666) {
    if ($intelBloqueado) { $alertas += "RAM a $cfgRamSpeed MT/s: em Intel sem 'K' e placa não-Z (ex.: H370/B360/B365) esse costuma ser o limite da plataforma, não XMP desligado. Confirme no manual da placa." }
    else { $alertas += "RAM a $cfgRamSpeed MT/s: provavelmente XMP/EXPO desligado. iRacing é sensível a RAM/CPU." }
}
if ($info.RAM.TotalGB -lt 24) { $alertas += "RAM total de $($info.RAM.TotalGB) GB: não reserve mais que ~10 GB para o sim se usar SimHub/Discord/navegador junto; observe uso de memória com o sim rodando." }
if ($ram.Count -eq 1) { $alertas += "Apenas 1 pente de RAM (single channel): perda grande de FPS em jogos limitados por CPU." }
if ($info.PlanoEnergia -match 'Economia|Power saver') { $alertas += "Plano de energia em economia: $($info.PlanoEnergia)" }
if ($info.GameDVR -eq 1 -or $info.CapturaEmSegundoPlano -eq 1) { $alertas += "Xbox Game Bar/captura em segundo plano ligada: custa FPS e causa stutter." }
if ($info.HAGS -ne 2) { $alertas += "HAGS (Agendamento de GPU acelerado por hardware) desligado: teste ligado (necessário para Frame Generation da NVIDIA)." }
if ($vbs -and $vbs.VBSStatus -eq 2) { $alertas += "VBS/Integridade de memória ativo: pode custar alguns % de FPS. É um recurso de SEGURANÇA — desligue só se entender o risco." }
foreach ($g in $info.GPUs) { if ($g.HzAtual -and $g.HzAtual -le 60) { $alertas += "Monitor '$($g.Nome)' a $($g.HzAtual) Hz: confira se o monitor suporta mais e ajuste em Configurações de vídeo." } }
$info.Alertas = $alertas

New-Item -ItemType Directory -Force -Path (Split-Path $Saida) | Out-Null
$info | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 $Saida
Write-Host "Relatório salvo em $Saida" -ForegroundColor Green
if ($alertas) { Write-Host "`nAlertas:" -ForegroundColor Yellow; $alertas | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow } }
