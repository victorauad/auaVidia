# Diário de lotes

Cenário de teste: Red Bull Ring GP · Super Formula SF23 · 20 carros IA · largada parada · horário/clima fixos ·
3× 1080p @ 120 Hz em NVIDIA Surround (5760×1080) · captura de 700 s em corrida contra IA.

| Data | Lote | Mudanças (3–4) | Rótulo do run | FPS médio | 1% low | p99 (ms) | GPU busy | Manter? |
|---|---|---|---|---|---|---|---|---|
| 2026-09-26 | 0 | Linha de base (batida na volta 9–10) | baseline | 106.4 | 70.7 | 13.18 | 92% (GPU) | — |

## Lote 0 — linha de base (2026-09-26)

PresentMon (74 464 frames, 700 s):
- FPS médio 106, 1% low 71, 0.1% low 58, p99 13,2 ms; stutters 1,3/min; pior frame ~24 ms (sem travadas grandes).
- **GPU Busy 92% → gargalo de GPU.** CPU Busy médio 9,2 ms (também perto do frametime): para chegar a 120 FPS
  estáveis (8,33 ms) os dois lados precisam aliviar; a GPU primeiro.
- Monitor a 120 Hz, V-Sync off no jogo, **PresentMode = Composed: Flip** (passa pelo compositor do Windows):
  +latência (≈11,7 ms até a tela) e 1% low *exibido* (57, HWiNFO) bem pior que o *apresentado* (76).

HWiNFO (mesma corrida):
- **GPU em limite térmico 100% do tempo**: 88,5 °C média, **hot spot 104–105 °C**, ventoinhas a 100%.
  Clock cai de ~1940 MHz (abaixo de 86 °C) para ~1785 MHz (≥ 88,5 °C): ~8% de desempenho perdido.
- CPU: sem throttling térmico (máx. 76 °C), mas **limite de potência PL1 = 65 W atingido 75% do tempo**
  (clock médio ~4,3 GHz). VRM da placa-mãe chegou a 95 °C.
- RAM: 10,3 GB em uso (6 GB livres); **memória virtual comprometida a 90%** (17,5 GB de ~19,4 GB, page file de só 3 GB).
- VRAM: 5,2 GB de 12 GB — sobra.
