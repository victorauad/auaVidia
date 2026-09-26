# Meu PC — perfil e diagnóstico

Coletado em 2026-09-26 com `01-coletar-sistema.ps1` (relatório estático, sem carga).

| Item | Valor | Leitura |
|---|---|---|
| CPU | Intel Core i7-9700 (8C/8T, sem K) | Gargalo esperado no iRacing com grid cheio. Sem overclock possível. |
| Placa-mãe | ASUS TUF B360M-PLUS GAMING/BR, BIOS 2811 (mai/2020) | Chipset B360: RAM limitada a 2666 MT/s, PCIe 3.0. Verificar BIOS mais nova no site da ASUS (baixa prioridade). |
| RAM | 16 GB = 2× Corsair Vengeance LPX 8 GB DDR4-2400 C16 | Rodando na velocidade nominal dos pentes (2400) — nada errado. Confirmar **dual channel** no HWiNFO/CPU-Z (pentes nos slots A2 e B2). |
| GPU | RTX 3060 **12 GB**, driver 616.92, PCIe 3.0 x16, 170 W | Ok. Folga grande para a resolução atual. |
| Monitor | **1440×900 @ 119 Hz** | ⚠️ Resolução baixa para uma 3060: quase certamente **CPU-bound**. Confirmar se é a resolução nativa do monitor. |
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
2. Com 1440×900, a RTX 3060 deve ficar ociosa → prioridade total para **aliviar a CPU** (lotes 1 e 2 de
   [`kb/revisao-pesquisa.md`](kb/revisao-pesquisa.md)) e **aumentar qualidade de GPU sem custo** (lote 3:
   MSAA 4x/8x, texturas, shaders; talvez até supersampling).
3. 16 GB com Discord + Garage 61 + Coach Dave + Trading Paints: não aumentar o slider de RAM do iRacing;
   observar uso de memória em corrida.
4. `02-otimizar-windows.ps1` teria pouco a fazer aqui: só HAGS (testar) e GPU preferencial para o iRacing.

## Pendências

- [ ] Modelo do monitor e resolução nativa.
- [ ] Benchmark baseline em carga (`04-benchmark.ps1 -Rotulo baseline`) → confirma GPU Busy < 70%.
- [ ] HWiNFO em carga: clock real da CPU (deve ficar perto de 4,6–4,7 GHz), temperatura, "Power Limit Exceeded", dual channel.
- [ ] Screenshots das abas de gráficos do iRacing.
