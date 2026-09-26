# Modelo de prompt para a IA (passo 4)

O vídeo fixa o prompt dele nos comentários do YouTube (não está na descrição). Este é um modelo próprio
com a mesma estrutura: **hardware em carga + gargalo medido + screenshots reais → lotes testáveis**.
Se você copiar o prompt original do comentário, cole-o em `docs/kb/prompt-original.md` para comparar.

Anexe: `runs/sistema-*.json`, relatório/log do HWiNFO64, saída do `analisar.py` do baseline e os
screenshots de todas as páginas de configurações gráficas.

---

```text
Você é um especialista em otimização de desempenho para simuladores de corrida.

## Objetivo
Gerar configurações gráficas e de desempenho para o [SIM, ex.: iRacing — versão/season atual] sob medida para o
MEU hardware. Prioridade: frametime consistente (1% low e p99) > FPS médio > qualidade visual.
Meta: [ex.: 144 FPS travados em 1080p/1440p, monitor 144 Hz com G-Sync] no pior cenário:
[ex.: largada com 40 carros em Daytona, noite/chuva].

## Hardware (relatório em carga, anexado)
- CPU: [modelo, núcleos/threads, clocks medidos em carga, temperatura máx, throttling sim/não]
- GPU: [modelo, VRAM, uso %, temperatura, potência em carga]
- RAM: [total, velocidade configurada, canais]
- Armazenamento, versão do driver, Windows: [...]
- Programas rodando junto com o sim: [ex.: SimHub, Discord, Crew Chief]

## Medição atual (baseline, anexada)
[cole a tabela do analisar.py: FPS médio, 1% low, p99, stutters/min, GPU busy %, gargalo]

## Configurações atuais
Os screenshots anexados são as MINHAS páginas de configuração reais desta versão do sim. Use SOMENTE as opções
e nomes que aparecem neles. Se uma configuração que você conhece não aparecer, diga isso em vez de supor que existe.

## O que eu quero
1. Diagnóstico: o gargalo é CPU ou GPU? Justifique com os números (GPU busy < ~70% = CPU-bound).
2. Uma lista de mudanças, cada uma com: nome exatamente como no menu, valor atual → valor novo, se reduz carga
   de CPU ou GPU, impacto visual esperado e confiança (alta/média/baixa).
3. Agrupe em LOTES de 3–4 mudanças, do maior ganho esperado para o menor, para eu testar um lote por vez.
4. Diga o que eu posso AUMENTAR de qualidade sem custo, dado o gargalo.
5. Para mudanças em arquivos .ini, dê arquivo, seção e chave, e marque como "confirmar no arquivo" se não tiver
   certeza de que o nome existe na versão atual.

## Restrições
- Não sugira mudanças de voltagem, overclock, clocks ou curva de ventoinha.
- Não sugira desativar recursos de segurança do Windows sem explicar o risco.
- Se faltar informação para decidir algo, pergunte em vez de supor.
```

---

Depois de cada lote: rode o benchmark, compare com `analisar.py comparar` e devolva a tabela para a IA com
"lote N: mantido/revertido" para ela ajustar o próximo lote.
