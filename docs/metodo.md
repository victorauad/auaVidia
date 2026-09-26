# Método: otimizar com dados, não com "melhores configurações" genéricas

A ideia central do vídeo *"Your iRacing Settings Are Wrong (And It's Not Your Hardware's Fault)"* é que
configurações copiadas de quem tem uma GPU de US$ 5.000 não servem para o seu PC. O caminho é:

1. **Descobrir o seu gargalo** (CPU ou GPU) com uma medição.
2. **Mudar uma coisa por vez.**
3. **Medir de novo no mesmo cenário** e manter só o que melhorou o **1% low / frametime**, não só o FPS médio.

## 0. Ferramentas

| Ferramenta | Para quê | Link |
|---|---|---|
| PresentMon (Intel) | Captura frametime + GPU busy (usado pelo `04-benchmark.ps1`) | https://github.com/GameTechDev/PresentMon/releases |
| CapFrameX | Alternativa com interface gráfica para capturar/comparar (exporta CSV) | https://www.capframex.com/ |
| HWiNFO64 | Temperaturas, clocks, throttling de CPU/GPU, uso de VRAM | https://www.hwinfo.com/ |
| MSI Afterburner + RTSS | Overlay de FPS/frametime e limitador de FPS | https://www.msi.com/Landing/afterburner |
| DDU | Remoção limpa de driver de vídeo antes de reinstalar | https://www.guru3d.com/download/display-driver-uninstaller-download/ |
| NVIDIA App / Painel de Controle NVIDIA | Configurações do driver por jogo | — |
| NVIDIA Profile Inspector (opcional) | Configurações avançadas de driver | https://github.com/Orbmu2k/nvidiaProfileInspector |

> Se o vídeo lista outras ferramentas na descrição, adicione aqui — não consegui acessar a descrição do
> YouTube a partir do ambiente onde este repositório foi montado.

## 1. Cenário de teste fixo (o mais importante)

Sem cenário repetível, qualquer comparação é ruído.

- Mesma pista, mesmo carro, mesmo horário/clima, **mesmo número de carros** (o que mais pesa na CPU no iRacing).
- Sugestão: grave um **replay** de uma largada com grid cheio e use sempre o mesmo trecho — é o pior caso real.
- Mesma câmera (cockpit), mesma duração (60–90 s), **3 execuções por configuração** (use a média).
- Feche navegador, Discord overlay, gravação etc. — ou deixe exatamente como você usa ao correr, mas sempre igual.

## 2. Linha de base

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\01-coletar-sistema.ps1
python iracing\iracing_ini.py backup "$env:USERPROFILE\Documents\iRacing"
powershell -ExecutionPolicy Bypass -File scripts\windows\04-benchmark.ps1 -Rotulo baseline -Segundos 90 -Atraso 10
```

Leia a coluna **Gargalo** do resumo:
- **GPU busy ≥ 90%** → limitado pela GPU: configurações gráficas viram FPS direto.
- **GPU busy ≤ 75%** → limitado pela CPU (normal no iRacing) ou pelo limitador de FPS/V-Sync.
  Aqui baixar AA/resolução quase não ajuda; o que ajuda é reduzir carga de CPU.

## 3. Ordem de ataque (maior ganho → menor)

### Hardware / BIOS (grátis e costuma ser o maior ganho)
- [ ] **XMP/EXPO ligado** (o `01-coletar-sistema.ps1` avisa se a RAM está abaixo da nominal).
- [ ] RAM em **dual channel** (2 pentes nos slots certos — ver manual da placa, geralmente A2/B2).
- [ ] BIOS atualizada; em Ryzen, testar **PBO/Curve Optimizer**; em Intel 13ª/14ª geração, BIOS com o microcode mais recente.
- [ ] Temperaturas sob controle (HWiNFO: CPU sem "thermal throttling", GPU sem bater limite de temperatura).
- [ ] Monitor na taxa de atualização máxima (Configurações > Vídeo > Avançado) e cabo DisplayPort/HDMI adequado.

### Windows (`02-otimizar-windows.ps1`, reversível)
- [ ] Modo de Jogo ligado, Xbox Game Bar/captura desligada.
- [ ] HAGS: **teste ligado e desligado** — o resultado varia de PC para PC.
- [ ] Otimizações para jogos em janela ligadas.
- [ ] Plano de energia Alto desempenho.
- [ ] Programas na inicialização: desligue o que não precisa (RGB, launchers, atualizadores).
- [ ] (Opcional, avalie o risco) VBS/Integridade de memória: pode custar alguns % em jogos limitados por CPU, mas é uma proteção de segurança.

### Driver de vídeo
- [ ] Driver atualizado; se houver problemas, reinstalar limpo com DDU.
- [ ] Modo de gerenciamento de energia: *Preferir desempenho máximo* (perfil do iRacing).
- [ ] Baixa latência: NVIDIA Reflex/Low Latency Mode *On* — meça.
- [ ] Limitador de FPS: um pouco abaixo do FPS que você sustenta no pior caso (ou do refresh com G-Sync/FreeSync) — frametime estável vale mais que pico.

### iRacing (dentro do sim, *Options > Graphics*)
Se o gargalo é **CPU**, estes costumam pesar mais:
- Número máximo de carros desenhados / detalhe de carros distantes.
- Sombras dinâmicas (especialmente de carros), espelhos (FPS e nº de carros nos espelhos).
- Objetos/crowd/detalhe de pista, "dynamic track" visual.

Se o gargalo é **GPU**:
- MSAA/SSAA, resolução/escala, pós-processamento (HDR/bloom), sombras, reflexos, nuvens.

Configurações que costumam ser "baratas" quando você está limitado por CPU: filtragem anisotrópica,
qualidade de texturas (se houver VRAM sobrando).

Ajustes em `.ini` (via `iracing/iracing_ini.py`): primeiro confira o nome/seção no **seu** arquivo com o
comando `get`. Exemplo relatado pela comunidade: `VisibilityFrameDelay` (padrão 5) → 0 para reduzir stutter
em curvas de pistas grandes. Teste como qualquer outra mudança.

## 4. Loop de iteração

```powershell
# mudou UMA coisa? capture com um rótulo que descreva a mudança
powershell -ExecutionPolicy Bypass -File scripts\windows\04-benchmark.ps1 -Rotulo sombras-carros-off
# compare com a base (a primeira da lista é a referência)
python analysis\analisar.py comparar runs\baseline-*.csv runs\sombras-carros-off-*.csv --markdown runs\comparacao.md --grafico runs\comparacao.png
```

Regras de decisão:
- Mantenha a mudança se **1% low** e **p99 frametime** melhoram (ou ficam iguais) e o visual continua aceitável.
- Diferenças abaixo de ~2–3% entre execuções são ruído: rode mais vezes antes de concluir.
- Anote cada experimento em `docs/diario.md` (o que mudou, resultado, manteve ou não).
