# Roteiro: benchmark em corrida contra IA (5 voltas)

Repita **exatamente igual** a cada lote. Só as configurações do lote mudam.

## Uma vez só (definir o cenário)

Anote no topo do [`diario.md`](diario.md) e nunca mude:
- Pista e layout, carro.
- Nº de carros da IA (use o tamanho de grid das suas corridas online, ex. 20–30).
- Largada (rolling/standing), horário fixo, **clima e céu estáticos** (sem dinâmico), pista sem evolução se possível.
- Câmera de cockpit, 3 monitores em 1080p, mesmos apps abertos de quando você corre (Discord, Garage 61, Coach Dave, Trading Paints). **TeamViewer fechado de verdade** (ícone da bandeja → Sair).

## A cada rodada

1. **Backup dos .ini** (PowerShell normal):
   ```powershell
   Copy-Item "$env:USERPROFILE\Documents\iRacing\*.ini" (New-Item -ItemType Directory -Force "C:\auaVidia\backup-ini\$(Get-Date -Format yyyyMMdd-HHmm)")
   ```
2. **Prints** de todas as abas de *Options → Graphics* no sim (Win+Shift+S).
3. **HWiNFO64** → *Sensors only* → botão de log (disquete/"Logging start") → salve `hwinfo-<rotulo>.csv`.
4. Entre na corrida contra IA. Quando o carro estiver **no grid / volta de apresentação**, Alt+Tab para o
   PowerShell **como Administrador** e rode (ajuste `-Segundos` = 5 × tempo de volta + 60):
   ```powershell
   cd "C:\auaVidia\auaVidia-claude-amazing-lamport-dyeenr"
   powershell -ExecutionPolicy Bypass -File scripts\windows\04-benchmark.ps1 -Rotulo baseline -Segundos 600 -Atraso 10
   ```
   Alt+Tab de volta ao sim em até 10 s e corra normalmente.
5. Terminada a corrida: pare o log do HWiNFO.
6. Mande: `runs\<rotulo>-*.csv`, `hwinfo-<rotulo>.csv`, os prints e qualquer coisa estranha (batida, pit, travada).

## Dicas

- A largada com o pelotão junto é o pior caso para a CPU — não pule.
- Corridas contra IA não são idênticas (incidentes variam): compare principalmente **1% low e p99**, e desconfie de
  diferenças < 3%. Se um lote ficar na dúvida, repita.
- Próximos lotes: mude as configurações do lote, e repita o roteiro trocando `-Rotulo` (`lote1`, `lote2`...).
