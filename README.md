# auaVidia

Kit para otimizar um PC de jogo/sim racing **com base em medições**, replicando o processo do vídeo
[Your iRacing Settings Are Wrong (And It's Not Your Hardware's Fault)](https://www.youtube.com/watch?v=ZMgnmJRoGVk):
relatório de hardware em carga → gargalo CPU × GPU (GPU Busy) → screenshots das configurações → prompt para IA →
aplicar em lotes de 3–4 e medir → manter só o que melhora o frametime.

Objetivos:
- otimizar as configurações do PC (BIOS, Windows, driver, jogo);
- analisar dados de benchmark (frametime, 1% low, gargalo CPU × GPU);
- aumentar a eficiência para ter mais FPS, mais estável, com a melhor qualidade possível.

## Estrutura

| Caminho | O que faz |
|---|---|
| `scripts/windows/01-coletar-sistema.ps1` | Inventário do hardware/config + alertas (XMP, single channel, Game Bar, HAGS, Hz do monitor…). Só lê. |
| `scripts/windows/02-otimizar-windows.ps1` | Ajustes seguros do Windows. Simula por padrão; `-Aplicar` grava e faz backup. |
| `scripts/windows/03-restaurar-windows.ps1` | Desfaz o anterior a partir do backup. |
| `scripts/windows/04-benchmark.ps1` | Captura frametimes do jogo com PresentMon em `runs/`. |
| `analysis/analisar.py` | Resumo e comparação de capturas (PresentMon/CapFrameX CSV): FPS, 1%/0.1% low, p99, stutters, gargalo. |
| `iracing/iracing_ini.py` | Backup, diff e edição dos `.ini` do iRacing preservando comentários. |
| `docs/metodo.md` | Os 5 passos do vídeo com os comandos deste repositório. |
| `docs/prompt-ia.md` | Modelo de prompt para a IA (passo 4). |
| `docs/kb/` | Base de conhecimento: descrição do vídeo, pesquisa sobre gráficos do iRacing e a revisão dela (`revisao-pesquisa.md`, com correções e plano de lotes para i7-9700 + RTX 3060). |
| `docs/meu-pc.md` | Perfil e diagnóstico do meu PC (i7-9700 + RTX 3060). |
| `docs/roteiro-corrida-ia.md` | Passo a passo do benchmark em corrida contra IA. |
| `docs/plano-lotes.md` | Plano de lotes para o meu PC (GPU-bound, triple 1080p). |
| `docs/diario.md` | Registro dos lotes testados. |

## Início rápido (Windows)

Requisitos: Windows 10/11, Python 3.10+ (`matplotlib` opcional para gráficos), [PresentMon](https://github.com/GameTechDev/PresentMon/releases) em `tools/PresentMon.exe`.

```powershell
# 1. Retrato do sistema (não altera nada)
powershell -ExecutionPolicy Bypass -File scripts\windows\01-coletar-sistema.ps1

# 2. Backup dos .ini do iRacing
python iracing\iracing_ini.py backup "$env:USERPROFILE\Documents\iRacing"

# 3. Benchmark de base (com o iRacing rodando no cenário de teste)
powershell -ExecutionPolicy Bypass -File scripts\windows\04-benchmark.ps1 -Rotulo baseline -Segundos 90 -Atraso 10

# 4. Ver o que o script do Windows mudaria, e aplicar (PowerShell como Administrador)
powershell -ExecutionPolicy Bypass -File scripts\windows\02-otimizar-windows.ps1
powershell -ExecutionPolicy Bypass -File scripts\windows\02-otimizar-windows.ps1 -Aplicar

# 5. Reiniciar, medir de novo e comparar
python analysis\analisar.py comparar runs\baseline-*.csv runs\windows-*.csv --grafico runs\comparacao.png
```

Detalhes e a ordem recomendada dos ajustes: [`docs/metodo.md`](docs/metodo.md).

## Testes

```bash
python -m unittest discover -s tests
```

## Segurança

Nada aqui desliga proteções de segurança automaticamente nem faz "debloat" agressivo. Todo ajuste de
registro/`.ini` tem backup e restauração.
