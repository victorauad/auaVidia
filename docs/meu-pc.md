# Meu PC — perfil e diagnóstico

Coletado em 2026-09-26 com `01-coletar-sistema.ps1` (relatório estático, sem carga).

| Item | Valor | Leitura |
|---|---|---|
| CPU | Intel Core i7-9700 (8C/8T, sem K) | Gargalo esperado no iRacing com grid cheio. Sem overclock possível. |
| Placa-mãe | ASUS TUF B360M-PLUS GAMING/BR, BIOS 2811 (mai/2020) | Chipset B360: RAM limitada a 2666 MT/s, PCIe 3.0. Verificar BIOS mais nova no site da ASUS (baixa prioridade). |
| RAM | 16 GB = 2× Corsair Vengeance LPX 8 GB DDR4-2400 C16 | Rodando na velocidade nominal dos pentes (2400) — nada errado. Confirmar **dual channel** no HWiNFO/CPU-Z (pentes nos slots A2 e B2). |
| GPU | RTX 3060 **12 GB**, driver 616.92, PCIe 3.0 x16, 170 W | ⚠️ **Limite térmico 100% do tempo em corrida**: 88,5 °C, hot spot 105 °C, fans 100%. É o gargalo (GPU Busy 92%). |
| Monitores | **3× 1080p (triple screen, 5760×1080)** ao jogar | O relatório mostrou 1440×900 @ 119 Hz porque o PC estava sendo acessado via TeamViewer. Triple triplica os pixels e, com renderização por tela, também a carga de CPU → gargalo pode ser misto/GPU. 120 Hz, NVIDIA Surround. |
| Windows | 11 Pro 24H2 (26100) | — |
| Plano de energia | Ultimate Performance (ExitLag) | Ok, manter. |
| Game Mode | padrão (ligado) | Ok. |
| Game Bar / captura | desligado | Ok. |
| HAGS | desligado | Testar ligado num lote (meça; exige reiniciar). |
| Otimização p/ jogos em janela | ligado | Ok. |
| VBS / Integridade de memória | desligado | Nada a fazer. |

## Programas na inicialização

| Manter (usados ao correr) | Tirar da inicialização / fechar antes de correr |
|---|---|
| Garage 61 Telemetry Agent, Trading Paints, Coach Dave Delta, Discord, Direct Drive Reset (base do volante) | Google Drive (aparece 5×; sincronização causa picos de disco/CPU — pelo menos **pause a sync** ao correr), OneDriveSetup, Spotify, Steam (se não usar para o iRacing), Edge Update, Logitech/Logi Download Assistant |

Como: Gerenciador de Tarefas → Aplicativos de inicialização → Desabilitar.

## Conclusões até aqui

1. Nada grave de configuração: RAM, energia, Game Bar e VBS já estão bem.
2. Em triple 1080p o gargalo não é óbvio: a CPU sofre com as vistas extras e a 3060 com 5760×1080 + MSAA.
   O benchmark decide a ordem dos lotes de [`kb/revisao-pesquisa.md`](kb/revisao-pesquisa.md); o lote 3
   (subir qualidade de GPU) só entra se o GPU Busy ficar < 70%.
3. 16 GB com Discord + Garage 61 + Coach Dave + Trading Paints: não aumentar o slider de RAM do iRacing;
   observar uso de memória em corrida.
4. `02-otimizar-windows.ps1` teria pouco a fazer aqui: só HAGS (testar) e GPU preferencial para o iRacing.

## Diagnóstico da linha de base (corrida IA, 2026-09-26)

Detalhes em [`diario.md`](diario.md). Resumo: **gargalo de GPU** (92%), agravado por **superaquecimento da GPU**;
CPU logo atrás e limitada a 65 W; apresentação em *Composed: Flip*; page file pequeno com memória virtual a 90%.

Ordem de ataque:
1. **Temperatura da GPU** (físico, antes de mexer em gráficos — senão toda medição fica contaminada).
2. Page file gerenciado pelo sistema.
3. Investigar *Composed: Flip* (tela cheia exclusiva? overlays?).
4. Lotes gráficos focados em GPU (a partir dos `.ini`/prints).
5. Depois: PL1 da CPU na BIOS (opcional, vigiando VRM).

## Pendências

- [x] 120 Hz, NVIDIA Surround.
- [ ] **Medir sempre sem TeamViewer conectado e nos 3× 1080p** (use `-Atraso 120` e desconecte durante a captura).
- [x] Benchmark baseline → GPU Busy 92% (gargalo de GPU).
- [x] HWiNFO em carga (ver diagnóstico acima). Dual channel ainda a confirmar.
- [ ] Configurações gráficas atuais: `app.ini` + `rendererDX11*.ini` (ou prints).
