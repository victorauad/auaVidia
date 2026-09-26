# Revisão da base de conhecimento

Revisão de [`Research_report_Base_de_Conhecimento_iRacing_Graficos.md`](Research_report_Base_de_Conhecimento_iRacing_Graficos.md)
à luz do processo do vídeo ([`descricao-video.md`](descricao-video.md)). O relatório original foi mantido intacto;
as correções ficam aqui.

Legenda: ❌ incorreto · ⚠️ não confirmado / confirmar no seu PC · ✅ ok

## 1. Correções e pontos a confirmar

| # | Trecho do relatório | Situação | Correção / ação |
|---|---|---|---|
| 1 | "C (CPU Physics Thread)… roda estritamente a 60 Hz" | ❌ | A física do iRacing roda a **360 Hz**. O limite de ~16,7 ms citado não se aplica a ela. |
| 2 | Medidores com tecla `F` / `ALT + K` e barras R/G/T/C | ⚠️ | Tecla e rótulos não confirmados (em muitas versões o painel de desempenho abre com `Ctrl+F`). Use o **GPU Busy do PresentMon** como fonte de verdade para CPU × GPU, como no vídeo. |
| 3 | RAM do sim: 12.000–13.000 MB com 16 GB totais | ❌ arriscado | Sobra 3–4 GB para Windows + SimHub/Discord/navegador → paginação e stutter. Comece no padrão (ou ~10 GB) e observe uso de memória com o sim rodando. |
| 4 | VRAM do sim: 9.000–10.000 MB na RTX 3060 12 GB | ✅ | ~75–85% da VRAM é razoável. Confirme que a sua 3060 é a de **12 GB** (existe versão de 8 GB). |
| 5 | Arquivo `rendererDX11v2.ini` | ⚠️ | Não confirmado. Os conhecidos são `rendererDX11Monitor.ini`, `rendererDX11OpenXR.ini`, `rendererDX11Oculus.ini` (e `rendererDX11.ini` legado). Liste a pasta `Documentos\iRacing`. |
| 6 | Chaves `VidMemMB`/`VidMemToUse`, `SysMemToUse`, `LODPctDynoMax/Min`, `MaxPitObjsToDraw*`, `[Misc] showJoinLeave`, `[Graphic Options] pauseReplayOnExit` | ⚠️ | Nomes/seções não verificados (dois nomes alternativos para a mesma chave já indicam incerteza). Antes de editar: `python iracing/iracing_ini.py get <arquivo> <Seção> <Chave>`. |
| 7 | `core.ini` controla "alocação de threads da CPU" | ⚠️ | Não confirmado; não edite sem fonte oficial. |
| 8 | i7-9700 com "ótimo desempenho single-thread" | ⚠️ nuance | CPU de 2019, 8C/8T sem Hyper-Threading, sem sufixo K (sem overclock), TDP 65 W. Em grid cheio será o gargalo — o relatório acerta nisso. Em PCs de fábrica (Dell/HP/Lenovo) o limite de potência pode derrubar o clock em carga: confira no HWiNFO clock real e "Power Limit Exceeded". |
| 9 | (ausente) Velocidade da RAM | ⚠️ | Com i7-9700 em placa **não-Z** (H370/B360/B365), a RAM fica travada em **2666 MT/s** — não é XMP desligado. Em Z370/Z390, ative XMP. Garanta **dual channel** (2 pentes). |
| 10 | Nomes de opções (Shadow "Everything + PCF4", Particles "Full + Soft", Sharpening CAS, Two Pass Trees) | ⚠️ | Podem ter mudado de nome ou sumido na versão atual. É exatamente o problema que o passo 3 do vídeo (screenshots) resolve. |
| 11 | Fontes (tabela da seção 1) | ⚠️ | Não consegui abrir os links deste ambiente para validar; trate valores numéricos como hipóteses. |
| 12 | (ausente) Resolução, Hz do monitor, G-Sync, limitador de FPS | falta | Sem isso não dá para definir meta de FPS. Inclua no prompt. |

## 2. Diferença de abordagem

O relatório entrega uma **receita fixa**; o vídeo defende **gerar a receita a partir de medição + screenshots
e validar em lotes**. Por isso, a seção 5 do relatório vira abaixo um **plano de lotes (hipóteses)** a ser
confirmado pelo benchmark, não uma configuração final.

## 3. Plano de lotes para i7-9700 + RTX 3060 + 16 GB (hipótese)

Expectativa: **gargalo de CPU** em grid cheio (GPU Busy < 70%). Confirme no passo 2 antes de seguir.
Após cada lote: benchmark + `analisar.py comparar` + registro no `diario.md`.

| Lote | Mudanças (3–4) | Lado | Por quê |
|---|---|---|---|
| 1 | Crowd → Off/Low · Pit objects → Low/Off · Grandstands → Low/Medium · Dynamic cube maps → 0 | CPU | Maior redução de draw calls com pouca perda útil para pilotar. |
| 2 | Espelhos do cockpit → virtual mirror (ou menos espelhos) · carros desenhados nos espelhos ↓ · árvores de alta qualidade/dois passes → off · sombras só em objetos dinâmicos | CPU | Cada espelho redesenha a cena. |
| 3 | *Somente se GPU Busy ainda < 70%:* texturas → máx · shader → High · MSAA → 4x · anisotrópico 16x | GPU (grátis) | Recupera qualidade usando a folga da 3060. |
| 4 | VRAM do sim ~9.000–10.000 MB · RAM do sim padrão/~10 GB · limitador de FPS logo abaixo do mínimo sustentado (ou refresh−3 com G-Sync) · `02-otimizar-windows.ps1` | Sistema | Consistência de frametime. |

Se um lote piorar 1% low/p99: desfaça metade, meça, e isole o culpado.

Upgrade com melhor custo-benefício para iRacing neste PC, se um dia fizer sentido: a CPU/plataforma, não a GPU.
32 GB de RAM ajudam se o uso de memória com SimHub/Discord abertos passar de ~14 GB.
