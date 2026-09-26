<#
.SYNOPSIS
  Desfaz o 02-otimizar-windows.ps1 usando o JSON de backup que ele gerou.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\windows\03-restaurar-windows.ps1 -Backup runs\backup-windows-20260926-210000.json
#>
param([Parameter(Mandatory)][string]$Backup)
$ErrorActionPreference = 'Stop'

$b = Get-Content $Backup -Raw | ConvertFrom-Json
foreach ($r in $b.Registro) {
    if ($r.Existia) {
        if (-not (Test-Path $r.Path)) { New-Item -Path $r.Path -Force | Out-Null }
        New-ItemProperty -Path $r.Path -Name $r.Name -Value $r.Valor -PropertyType $r.Type -Force | Out-Null
        Write-Host "Restaurado $($r.Path)\$($r.Name) = $($r.Valor)"
    } else {
        Remove-ItemProperty -Path $r.Path -Name $r.Name -ErrorAction SilentlyContinue
        Write-Host "Removido $($r.Path)\$($r.Name) (não existia antes)"
    }
}
if ($b.PlanoEnergia) { powercfg /setactive $b.PlanoEnergia; Write-Host "Plano de energia restaurado: $($b.PlanoEnergia)" }
Write-Host "Reinicie o PC para tudo voltar ao estado anterior." -ForegroundColor Green
