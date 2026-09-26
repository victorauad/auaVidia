<#
.SYNOPSIS
  Aplica ajustes seguros e reversíveis do Windows para jogos. Por padrão só MOSTRA o que faria.

.DESCRIPTION
  Antes de mudar qualquer coisa, salva os valores atuais em runs\backup-windows-<data>.json.
  Para desfazer: 03-restaurar-windows.ps1 -Backup <arquivo>.

  O que NÃO é feito aqui de propósito (faça manualmente, se quiser, depois de medir):
   - Desligar VBS/Integridade de memória (é proteção de segurança).
   - "Debloat", desativar serviços, mexer em timer resolution/HPET, tweaks de rede "mágicos":
     ganhos raramente mensuráveis e risco alto de quebrar algo.

.EXAMPLE
  # Só mostra
  powershell -ExecutionPolicy Bypass -File scripts\windows\02-otimizar-windows.ps1
  # Aplica (rodar como Administrador)
  powershell -ExecutionPolicy Bypass -File scripts\windows\02-otimizar-windows.ps1 -Aplicar -ExeJogo "C:\Program Files (x86)\iRacing\iRacingSim64DX11.exe"
#>
param(
    [switch]$Aplicar,
    [string]$ExeJogo = "C:\Program Files (x86)\iRacing\iRacingSim64DX11.exe",
    [ValidateSet('AltoDesempenho', 'DesempenhoMaximo', 'Manter')]
    [string]$PlanoEnergia = 'AltoDesempenho'
)
$ErrorActionPreference = 'Stop'

$ehAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($Aplicar -and -not $ehAdmin) { throw "Rode o PowerShell como Administrador para aplicar." }

$dxKey = 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences'
# Cada ajuste: caminho, nome, valor, tipo, motivo
$ajustes = @(
    @{ Path = 'HKCU:\Software\Microsoft\GameBar'; Name = 'AutoGameModeEnabled'; Value = 1; Type = 'DWord'; Motivo = 'Modo de Jogo: prioriza o jogo e segura o Windows Update durante a sessão.' }
    @{ Path = 'HKCU:\System\GameConfigStore'; Name = 'GameDVR_Enabled'; Value = 0; Type = 'DWord'; Motivo = 'Desliga gravação do Xbox Game Bar (causa stutter).' }
    @{ Path = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR'; Name = 'AppCaptureEnabled'; Value = 0; Type = 'DWord'; Motivo = 'Desliga captura em segundo plano.' }
    @{ Path = 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers'; Name = 'HwSchMode'; Value = 2; Type = 'DWord'; Motivo = 'HAGS ligado (requer reiniciar). Meça: em alguns PCs piora, em outros melhora.' }
    @{ Path = $dxKey; Name = 'DirectXUserGlobalSettings'; Value = 'SwapEffectUpgradeEnable=1;'; Type = 'String'; Motivo = 'Otimizações para jogos em janela/borderless (menor latência).' }
)
if ($ExeJogo) {
    $ajustes += @{ Path = $dxKey; Name = $ExeJogo; Value = 'GpuPreference=2;'; Type = 'String'; Motivo = 'Força a GPU dedicada para o executável do jogo (útil em notebooks).' }
}

function Get-Atual($a) {
    try { (Get-ItemProperty -Path $a.Path -Name $a.Name -ErrorAction Stop).($a.Name) } catch { $null }
}

$backup = [ordered]@{ Data = (Get-Date).ToString('s'); PlanoEnergia = $null; Registro = @() }
$planoAtual = (powercfg /getactivescheme) -join ' '
if ($planoAtual -match '([0-9a-fA-F-]{36})') { $backup.PlanoEnergia = $Matches[1] }

Write-Host "Modo: $(if ($Aplicar) { 'APLICAR' } else { 'SIMULAÇÃO (use -Aplicar para gravar)' })`n" -ForegroundColor Cyan
foreach ($a in $ajustes) {
    $atual = Get-Atual $a
    $backup.Registro += @{ Path = $a.Path; Name = $a.Name; Type = $a.Type; Valor = $atual; Existia = ($null -ne $atual) }
    $status = if ("$atual" -eq "$($a.Value)") { 'OK   ' } else { 'MUDAR' }
    Write-Host ("[{0}] {1}\{2}: '{3}' -> '{4}'`n        {5}" -f $status, $a.Path, $a.Name, $atual, $a.Value, $a.Motivo)
}

$guidAlto = '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
$guidMaximo = 'e9a42b02-d5df-448d-aa00-03f14749eb61'
if ($PlanoEnergia -ne 'Manter' -and $planoAtual -match 'Ultimate|Desempenho M|Alto desempenho|High performance') {
    Write-Host "`nPlano de energia já é de alto desempenho; mantendo." -ForegroundColor DarkGray
    $PlanoEnergia = 'Manter'
}
Write-Host "`nPlano de energia atual: $planoAtual -> $PlanoEnergia"

if (-not $Aplicar) { return }

$arqBackup = Join-Path $PSScriptRoot "..\..\runs\backup-windows-$(Get-Date -Format yyyyMMdd-HHmmss).json"
New-Item -ItemType Directory -Force -Path (Split-Path $arqBackup) | Out-Null
$backup | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $arqBackup
Write-Host "Backup salvo em $arqBackup" -ForegroundColor Green

foreach ($a in $ajustes) {
    if (-not (Test-Path $a.Path)) { New-Item -Path $a.Path -Force | Out-Null }
    New-ItemProperty -Path $a.Path -Name $a.Name -Value $a.Value -PropertyType $a.Type -Force | Out-Null
}

switch ($PlanoEnergia) {
    'AltoDesempenho' { powercfg /setactive $guidAlto }
    'DesempenhoMaximo' {
        $saida = powercfg /duplicatescheme $guidMaximo
        if ($saida -match '([0-9a-fA-F-]{36})') { powercfg /setactive $Matches[1] }
    }
}
Write-Host "`nPronto. Reinicie o PC (HAGS só vale depois do reboot) e rode um benchmark novo para comparar." -ForegroundColor Green
