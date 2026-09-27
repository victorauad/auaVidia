# Plano de lotes — i7-9700 + RTX 3060, triple 1080p @ 120 Hz

Base: linha de base de 2026-09-26 (GPU Busy 92%, GPU a 88 °C em limite térmico). Regra que guia tudo:
**em gargalo de GPU, o que reduz trabalho da GPU dá FPS e, com limitador de FPS, também baixa a temperatura.**
Sem limitador, a GPU volta a 100% e esquenta igual — por isso o limitador entra no fim.

Os nomes das opções podem variar na versão atual do iRacing: confira no menu e anote o que mudou de/para.

## Lote 0b — só a limpeza
Rodar `-Rotulo baseline2` sem mudar nada, para separar o ganho da limpeza do ganho das configurações.

## Lote 1 — maiores custos de GPU em 5760×1080
| Opção | Mudança | Por quê |
|---|---|---|
| MSAA / anti-aliasing | um degrau abaixo (8x→4x, 4x→2x); supersampling/escala de render > 100% → desligar | Custo multiplicado por 3 telas; maior economia isolada |
| Sombras (shadow maps) | um degrau abaixo; sombras só em objetos dinâmicos | Muito custo de GPU (e CPU) |
| Dynamic cube maps / reflexos | 0 / off (ou mínimo) | Renderiza a cena de novo para reflexos |
| Pós-processamento (HDR/bloom/efeitos) | desligar ou mínimo | Custo por pixel ×3 telas |

## Lote 2 — carga de cena (GPU e CPU)
| Opção | Mudança |
|---|---|
| Espelhos | espelho virtual no lugar dos espelhos do cockpit, ou menos carros/detalhe nos espelhos |
| Público / arquibancadas / objetos de pit | Low ou Off |
| Céu/nuvens | Medium |
| Partículas | um degrau abaixo |

Manter (baratas quando há VRAM sobrando — 7 GB livres): texturas, filtragem anisotrópica.

## Lote 3 — driver e Windows (Painel de Controle NVIDIA → Gerenciar configurações 3D → Programa: iRacing)
| Opção | Valor |
|---|---|
| Modo de baixa latência | Ligado (não "Ultra") |
| Modo de gerenciamento de energia | Normal (não forçar desempenho máximo: aquece mais sem ganho em carga) |
| Qualidade da filtragem de texturas | Alto desempenho |
| Tamanho do cache de shader | 10 GB ou Ilimitado |
| Sincronização vertical | Usar configuração do aplicativo |
| Windows | page file gerenciado pelo sistema; desabilitar apps de inicialização desnecessários; pausar Google Drive |
| *Composed: Flip* | iRacing em tela cheia (não janela/borderless); testar com overlays (Coach Dave, Discord) desligados |

## Lote 4 — limitador de FPS (temperatura + consistência)
Depois dos lotes 1–3, com o FPS sem limite medido:
- Se o 1% low ficar ≥ ~115: limitar em **120** (sincroniza com os 120 Hz).
- Senão: limitar logo abaixo do FPS que o PC sustenta na largada (ex.: média do 1% low + ~10) — a GPU deixa de rodar
  a 100%, a temperatura cai e os frametimes ficam regulares.
Use o limitador do iRacing ou "Taxa de quadros máxima" no painel NVIDIA (um só).

## Opcional, avançado — só com cuidado
- **Limite de potência da GPU** no MSI Afterburner (ex.: 85–90%): só reduz, não arrisca o hardware; baixa alguns °C
  com perda pequena de FPS. Bom paliativo até resolver a pasta térmica.
- Undervolt da GPU e aumento do PL1 da CPU na BIOS: mexem em voltagem/energia — não aplicar a partir de sugestão
  de IA sem conferir guia/manual (aviso do próprio vídeo). O definitivo para a GPU é **pasta térmica + pads**
  (hot spot 16 °C acima da média).
