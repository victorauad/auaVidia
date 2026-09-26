# Relatório de Pesquisa: Base de Conhecimento de Configuração Gráfica do iRacing

Este relatório reúne informações sobre as configurações gráficas do iRacing, arquivos de configuração do jogo e diretrizes de otimização para um sistema com CPU Intel Core i7-9700, GPU Nvidia GeForce RTX 3060 e 16 GB de RAM.

---

## 1. Fontes Consultadas

### 🔧 Guias e Documentação Técnica

| # | Título | Fonte | Tipo |
|---|--------|-------|------|
| 1 | [iRacing Graphics Settings Guide](https://simracingcockpit.gg/iracing-graphics-settings/) | SimRacingCockpit | Guia Técnico |
| 2 | [Understanding iRacing Performance & Meter Box](https://support.iracing.com/support/solutions/articles/31000133494-meter-box-f-key-in-game-) | iRacing Support | Suporte Oficial |
| 3 | [iRacing Graphic Optimisation Guide](https://byteinsight.co.uk/2022/11/iracing-graphic-optimisation/) | Byte Insight | Guia Técnico |
| 4 | [iRacing CPU and GPU Technical Deep Dive](https://simracingcockpit.gg/iracing-cpu-gpu-technical-deep-dive/) | SimRacingCockpit | Análise de Hardware |
| 5 | [iRacing .ini Files Customization Guide](https://bandofothersgaming.com/forum/threads/iracing-app-ini-settings.3159/) | Band of Others | Guia da Comunidade |

---

## 2. Visão Geral das Configurações Gráficas no iRacing

O motor gráfico do iRacing (baseado em DirectX 11) tem características únicas em comparação com outros simuladores: é altamente **dependente do desempenho de um único núcleo da CPU** (single-core) para construir as chamadas de renderização (*draw calls*), enquanto transfere o processamento de shaders, resolução e filtragem para a GPU.

### Definições dos Principais Parâmetros e Impacto no Desempenho

- **Sky/Clouds (Céu e Nuvens)**:
  - *Opções*: Low, Medium, High.
  - *Impacto*: Médio na GPU/CPU. A opção Medium oferece excelente qualidade visual e reduz quedas de quadros em corridas com clima dinâmico.
- **Cars / Car Detail (Detalhe dos Carros)**:
  - *Opções*: Low, Medium, High, Max.
  - *Impacto*: Médio a Alto na CPU/GPU. Define o nível de detalhe geométrico e texturas dos modelos 3D dos carros.
- **Track Detail (Detalhe da Pista)**:
  - *Opções*: Low, Medium, High.
  - *Impacto*: Médio. Ajusta o detalhamento de zebras, barreiras e estruturas ao redor da pista. Mantendo em High garante referências visuais de frenagem precisas.
- **Dynamic Track Data (Dados Dinâmicos de Pista)**:
  - *Opções*: Desativado, Ativado.
  - *Impacto*: Médio na CPU/GPU. Renderiza o acúmulo de borracha (*marbles*), sujeira e umidade na trajetória ideal.
- **Crowds & Grandstands (Público e Arquibancadas)**:
  - *Opções*: Off, Low, Medium, High.
  - *Impacto*: **ALTÍSSIMO na CPU (Thread R)**. Em largadas com mais de 30-40 carros, público e arquibancadas em níveis altos causam gargalo severo na CPU. Recomendado: Off ou Low para o público.
- **Pit Objects (Objetos do Box)**:
  - *Opções*: Off, Low, Medium, High.
  - *Impacto*: Alto na CPU na passagem pelo pit lane. Ajustar para Low ou Off melhora a estabilidade de FPS nos boxes.
- **Shadow Maps & Night Shadows (Sombras Dinâmicas)**:
  - *Opções*: Off, Dynamic Objects, Everything + PCF4 Filtering.
  - *Impacto*: **ALTÍSSIMO na CPU e GPU**. Ativar sombras em objetos estáticos (walls/track) consome muitos recursos. O ideal é manter apenas "Dynamic Objects" ativado.
- **Shader Quality (Qualidade dos Shaders)**:
  - *Opções*: Low, Medium, High, Ultra.
  - *Impacto*: Alto na GPU. Controla a iluminação de superfícies, reflexos metálicos e efeitos de chuva/pista molhada. Placas modernas como a RTX 3060 suportam High/Ultra sem problemas a 1080p/1440p.
- **Particles & Soft Particles (Partículas)**:
  - *Opções*: Low, High, Full + Soft Particles.
  - *Impacto*: Médio na GPU. Controla fumaça de pneu, faíscas e borrifos de água.
- **Mirrors (Espelhos)**:
  - *Cockpit Mirrors*: Renderiza um ângulo completo de câmera por espelho adicional (impacto altíssimo de CPU/GPU).
  - *Virtual Mirror*: Extremamente otimizado e leve (recomendado para simulação competitiva).
- **Dynamic & Fixed Cubemaps (Reflexos Cúbicos)**:
  - *Impacto*: **Extremamente alto na GPU e CPU**. Devem ser mantidos em 0 para garantir FPS estável.
- **Anti-Aliasing (Serrilhado)**:
  - *MSAA*: 2x ou 4x (melhor nitidez sem borrão).
  - *Sharpening (Cas / FidelityFX)*: Adiciona nitidez com custo insignificante.

---

## 3. Arquivos de Configuração Localizados no PC

Os arquivos de configuração do iRacing ficam salvos no diretório do Windows: `C:\Users\[SeuUsuario]\Documents\iRacing\`.

### Principais Arquivos .ini

1. **`app.ini`**:
   - Controla configurações gerais do simulador, interface do usuário, áudio, chat, spotter e preferências de câmera.
   - *Parâmetros Chave*:
     - `[Graphics] VirtualMirrorSize`: Define a escala do espelho virtual.
     - `[Misc] showJoinLeave`: Ativa/desativa mensagens de entrada/saída de pilotos na pista (desativar evita engasgos durante a pilotagem).
     - `[Drive Sound]`: Ajusta níveis de volume de áudio do motor relativo aos adversários.
     - `[Graphic Options] pauseReplayOnExit`: Define se o replay pausa ao sair do carro.

2. **`rendererDX11v2.ini`** (ou `rendererDX11Monitor.ini` / `rendererDX11Oculus.ini`):
   - Controla o motor gráfico do DirectX 11 específico para a exibição ativa (monitor, VR OpenXR, Oculus).
   - *Parâmetros Chave*:
     - `VidMemMB` / `VidMemToUse`: Limite de memória VRAM em MB alocado para o jogo.
     - `SysMemToUse`: Limite de memória RAM do sistema alocado para o jogo.
     - `LODPctDynoMax` / `LODPctDynoMin`: Controle dinâmico de nível de detalhe (LOD) para manter a taxa de FPS alvo.
     - `MaxPitObjsToDraw` / `MaxPitObjsToDrawInMirrors`: Limita a quantidade de objetos de pit lane renderizados.

3. **`core.ini`**:
   - Armazena parâmetros de baixo nível do motor do iRacing, como alocação de threads da CPU, tamanho de buffers de rede e preferências do sistema de telemetria em disco.

4. **Outros arquivos**:
   - `joyCalib.yaml`: Calibração de volante, pedais e joysticks.
   - `controls.cfg`: Mapeamento de botões e atalhos de teclado.
   - `camera.ini`: Ângulos de visão e configurações das câmeras de pista e replay.

---

## 4. Análise de Benchmarks e Leitura dos Medidores em Jogo (`F` key / `ALT + K`)

Pressionando a tecla **`F`** durante uma sessão (ou ativando a caixa de medidores pelo menu `ALT + K`), o iRacing exibe as barras de desempenho e tempos de quadro em milissegundos:

- **R (Render Thread - CPU)**:
  - Mede o tempo em milissegundos que a CPU leva para desenhar a cena e enviar instruções para a GPU.
  - *Análise*: Se o medidor **R** for maior que o **G** (ou ficar amarelo/vermelho, acima de 16.6 ms para 60 FPS, 11.1 ms para 90 FPS ou 6.9 ms para 144 FPS), o sistema está com **gargalo de CPU**.
- **G (GPU Thread)**:
  - Mede o tempo em milissegundos que a placa de vídeo leva para renderizar o quadro.
  - *Análise*: Se o medidor **G** for maior que o **R**, o limite do sistema é a placa de vídeo (resolução, shaders, anti-aliasing, sombras).
- **T (Total Frame Time)**: Tempo total de processamento do quadro.
- **C (CPU Physics Thread)**: Mede o tempo do ciclo de física (que roda estritamente a 60 Hz no iRacing). Deve ficar abaixo de 14-16.7 ms.
- **L (Latency / Netcode)** e indicadores de **Paging de Memória (RAM/VRAM)**.

---

## 5. Recomendação de Otimização para o Hardware do Usuário

### Especificações do Sistema:
- **CPU**: Intel Core i7-9700 (8 núcleos / 8 threads, até 4.7 GHz Turbo Boost).
- **GPU**: Nvidia GeForce RTX 3060 (12 GB de VRAM).
- **RAM**: 16 GB DDR4.

### Diagnóstico do Perfil de Desempenho:
O processador Intel i7-9700 possui ótimo desempenho por núcleo em single-thread, porém a ausência de Hyper-Threading (8 threads totais) significa que em corridas com mais de 30-40 carros (ex.: IMSA, GT3 em pistas complexas como Portimão ou Daytona), a **Thread R da CPU** será o gargalo primário. A GPU RTX 3060 (com 12 GB de VRAM) tem sobra de potência para 1080p ou 1440p em monitor único.

### Configuração Ideal Sugerida:

1. **Alocação de Memória (Sliders de RAM e VRAM)**:
   - **System RAM Slider**: Defina para aproximadamente **12.000 MB a 13.000 MB** (deixando 3-4 GB livres para o Windows).
   - **Video RAM Slider**: Para a RTX 3060 12GB, defina para **9.000 MB a 10.000 MB** (aproveitando o grande espaço de VRAM para carregar texturas em resolução máxima).

2. **Ajustes para Reduzir Carga na CPU (Gargalo da Thread R)**:
   - **Crowds**: *Off* ou *Low*.
   - **Pit Objects**: *Low* ou *Off*.
   - **Grandstands**: *Medium* ou *Low*.
   - **Cockpit Mirrors**: Máximo de 2 (ou preferencialmente utilize apenas o **Virtual Mirror**).
   - **Dynamic Cube Maps**: Defina em **0**.
   - **Two Pass Trees / High Quality Trees**: Desativados.

3. **Ajustes de Qualidade Visual (Aproveitando a RTX 3060)**:
   - **Shader Quality**: *High* ou *Ultra*.
   - **Car Detail & Track Detail**: *High*.
   - **Texture Quality**: *Max*.
   - **Particles**: *High* com *Soft Particles* ativado.
   - **Shadow Maps**: Ativado apenas em *Dynamic Objects* com filtragem *PCF4*.
   - **Anti-Aliasing**: *4x MSAA* + *Sharpening (CAS)* ativado a 50%.
