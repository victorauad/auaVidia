# Método: hardware entra, configurações saem

Processo do vídeo *"Your iRacing Settings Are Wrong (And It's Not Your Hardware's Fault)"* (descrição em
[`kb/descricao-video.md`](kb/descricao-video.md)), adaptado para as ferramentas deste repositório.
Serve para iRacing, MSFS 2024, AC, ACC, AMS2, rFactor 2 etc. **Repita depois de cada atualização grande do sim**:
opções mudam de nome, aparecem e somem.

Princípios:
- Relatório de hardware **com o sim rodando em carga**, nunca em idle.
- Medir o **pior cenário** (largada com grid cheio, chuva, noite).
- **GPU Busy / uso da GPU abaixo de ~70% → gargalo de CPU**: configurações gráficas não vão salvar o FPS.
- Mudanças em **lotes de 3–4**, testando após cada lote.
- Buscar **frametime consistente** (1% low, p99), não FPS médio alto.
- IA erra: ela lê seus menus reais (screenshots) e cada lote é verificado com medição.
  Nada de voltagem, clock ou curva de ventoinha vindo de IA sem conferir no manual.

## Ferramentas (todas grátis)

| Ferramenta | Para quê |
|---|---|
| [PresentMon](https://github.com/GameTechDev/PresentMon/releases) | Overlay + captura: frametime, **GPU Busy**, e (no app de captura) potência/temperatura/uso da GPU. Cobre os passos 1 e 2. Funciona em NVIDIA/AMD/Intel. |
| [HWiNFO64](https://www.hwinfo.com/) | Inventário detalhado e exportação de relatório (timings de RAM, discos, drivers); sensores de throttling. |
| `scripts/windows/01-coletar-sistema.ps1` | Resumo rápido do sistema + alertas (complementa o HWiNFO). |
| `scripts/windows/04-benchmark.ps1` + `analysis/analisar.py` | Captura e comparação de frametime entre lotes. |

Opcionais: MSI Afterburner + RTSS (limitador de FPS), DDU (reinstalação limpa de driver).

## Passo 0 — Cenário de teste fixo

Sem cenário repetível, a comparação vira ruído.
- Mesma pista, carro, clima/horário e **número de carros** (o que mais pesa na CPU no iRacing).
- Sugestão: um **replay** de largada com grid cheio, sempre o mesmo trecho, câmera de cockpit.
- 60–90 s por captura, **3 capturas por configuração**.

## Passo 1 — Relatório de hardware (em carga)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\01-coletar-sistema.ps1
```
Depois, **com o sim rodando no cenário de teste**:
- HWiNFO64 → *Sensors* → deixe 2–3 min em carga → salve o log/relatório (clocks reais, temperatura,
  "Power Limit Exceeded"/"Thermal Throttling").
- PresentMon (app) com overlay ligado: anote GPU Busy, uso, temperatura e potência da GPU.

## Passo 2 — CPU-bound ou GPU-bound?

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\04-benchmark.ps1 -Rotulo baseline -Segundos 90 -Atraso 10
```
O resumo mostra **GPU busy** e a coluna **Gargalo**:
- **< 70%** → CPU: reduza o que gera *draw calls* (carros visíveis, público, objetos de pit, espelhos,
  cubemaps, sombras de objetos estáticos). Qualidade de textura/AA/shader tende a ser "grátis".
- **70–90%** → misto: ajuste os dois lados com cuidado.
- **≥ 90%** → GPU: MSAA, resolução, shaders, sombras e pós-processamento viram FPS direto.

## Passo 3 — Screenshot de cada página de configurações

Tire print de **todas** as abas de gráficos do sim (e do painel do driver, se quiser incluí-lo).
Isso impede a IA de "lembrar" menus de versões antigas.

## Passo 4 — O prompt

Use o modelo em [`prompt-ia.md`](prompt-ia.md), anexando: JSON do passo 1, relatório do HWiNFO,
resumo do `analisar.py` do passo 2 e os screenshots do passo 3.

## Passo 5 — Aplicar em lotes e verificar

```powershell
# aplique um lote de 3-4 mudanças, depois:
powershell -ExecutionPolicy Bypass -File scripts\windows\04-benchmark.ps1 -Rotulo lote1
python analysis\analisar.py comparar runs\baseline-*.csv runs\lote1-*.csv --markdown runs\comparacao.md --grafico runs\comparacao.png
```

Regras de decisão:
- **Mantém** o lote se 1% low e p99 melhoram (ou ficam iguais) e o visual continua aceitável.
- **Piorou?** Desfaça metade do lote e meça de novo até achar o culpado.
- Diferença < ~2–3% entre capturas é ruído: repita antes de concluir.
- Registre tudo em [`diario.md`](diario.md).

Os `.ini` do iRacing têm backup/diff/edição em `iracing/iracing_ini.py`. Confira nome e seção de qualquer
chave no **seu** arquivo (`get`) antes de mudar; a pesquisa da KB tem nomes não confirmados
(ver [`kb/revisao-pesquisa.md`](kb/revisao-pesquisa.md)).

## Ajustes fora do sim (fazer uma vez, também medindo)

- **BIOS/RAM:** XMP/EXPO se a placa permitir; dual channel; BIOS atualizada.
- **Windows** (`02-otimizar-windows.ps1`, reversível): Modo de Jogo, Game Bar/captura off, HAGS (teste ligado e
  desligado), otimização para jogos em janela, plano Alto desempenho, limpar programas de inicialização.
- **Driver:** atualizado (DDU se houver problema); gerenciamento de energia "desempenho máximo" no perfil do
  sim; limitador de FPS um pouco abaixo do FPS mínimo sustentado (ou do refresh com G-Sync).
- VBS/Integridade de memória: pode custar alguns % em cenário limitado por CPU, mas é proteção de segurança —
  decisão sua, com medição.
