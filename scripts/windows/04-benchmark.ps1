<#
.SYNOPSIS
  Captura frametimes do jogo com o PresentMon e salva em runs\<rótulo>.csv.

.DESCRIPTION
  Baixe o PresentMon (console) em https://github.com/GameTechDev/PresentMon/releases e
  coloque o .exe em tools\PresentMon.exe (ou passe -PresentMon <caminho>).

  Para resultados comparáveis, repita SEMPRE o mesmo cenário:
   - mesma pista, carro, clima/horário, nº de carros (ex.: replay salvo ou test drive com IA),
   - mesma câmera (cockpit), mesma duração, e rode 3x cada configuração.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\windows\04-benchmark.ps1 -Rotulo baseline -Segundos 90 -Atraso 10
#>
param(
    [Parameter(Mandatory)][string]$Rotulo,
    [int]$Segundos = 60,
    [int]$Atraso = 5,
    [string]$Processo = 'iRacingSim64DX11.exe',
    [string]$PresentMon = (Join-Path $PSScriptRoot '..\..\tools\PresentMon.exe')
)
$ErrorActionPreference = 'Stop'

if (-not (Test-Path $PresentMon)) {
    throw "PresentMon não encontrado em $PresentMon. Baixe em https://github.com/GameTechDev/PresentMon/releases"
}
$pasta = Join-Path $PSScriptRoot '..\..\runs'
New-Item -ItemType Directory -Force -Path $pasta | Out-Null
$saida = Join-Path $pasta ("{0}-{1}.csv" -f $Rotulo, (Get-Date -Format yyyyMMdd-HHmmss))

Write-Host "Coloque o jogo em foco. Captura começa em $Atraso s e dura $Segundos s..." -ForegroundColor Cyan
# Sintaxe do PresentMon 2.x. Para a 1.x troque '--' por '-' nos parâmetros.
& $PresentMon --process_name $Processo --output_file $saida --delay $Atraso --timed $Segundos --terminate_after_timed --no_console_stats
if (-not (Test-Path $saida)) { throw "Nenhum CSV gerado. O jogo ($Processo) estava rodando?" }

Write-Host "Captura salva em $saida" -ForegroundColor Green
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) { & python (Join-Path $PSScriptRoot '..\..\analysis\analisar.py') resumo $saida }
