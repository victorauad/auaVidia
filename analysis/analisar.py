#!/usr/bin/env python3
"""Analisa capturas de frametime (PresentMon / CapFrameX CSV) e compara execuções.

Uso:
    python analysis/analisar.py resumo runs/baseline.csv
    python analysis/analisar.py comparar runs/baseline.csv runs/sombras-baixo.csv [...]
    python analysis/analisar.py comparar runs/*.csv --markdown relatorio.md --grafico grafico.png

Só usa a biblioteca padrão; matplotlib é opcional (apenas para --grafico).
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

# Colunas de frametime por ordem de preferência (PresentMon 1.x/2.x e CapFrameX).
FRAMETIME_COLS = ("MsBetweenPresents", "FrameTime", "msBetweenPresents")
# Tempo em que a GPU esteve ocupada no frame (serve para dizer se o gargalo é CPU ou GPU).
GPU_BUSY_COLS = ("MsGPUBusy", "GPUBusy", "MsGPUActive", "msGPUActive")
APP_COLS = ("Application", "ProcessName")
# Telemetria opcional (PresentMon 2.x / app de captura). Casamento ignora maiúsculas, espaços e "_".
TELEMETRIA_COLS = {
    "gpu_util_pct": ("GPUUtilization", "GPU Utilization", "GPUUtil"),
    "gpu_temp_c": ("GPUTemperature", "GPU Temperature", "GPUTemp"),
    "gpu_power_w": ("GPUPower", "GPU Power"),
    "cpu_util_pct": ("CPUUtilization", "CPU Utilization"),
    "cpu_temp_c": ("CPUTemperature", "CPU Temperature"),
}
# Limiares de GPU Busy (% do frametime). O vídeo usa ~70%: abaixo disso, gargalo de CPU.
LIMIAR_CPU = 70.0
LIMIAR_GPU = 90.0

# Um frame é considerado "stutter" se demorar mais que N vezes a mediana.
STUTTER_FACTOR = 2.0


@dataclass
class Resultado:
    nome: str
    frames: int
    duracao_s: float
    fps_medio: float
    fps_mediana: float
    low_1: float
    low_01: float
    p99_ms: float
    desvio_ms: float
    stutters: int
    gpu_busy_pct: float | None
    gargalo: str
    telemetria: dict[str, tuple[float, float]] | None = None  # nome -> (média, máximo)

    @property
    def stutters_por_min(self) -> float:
        return self.stutters / (self.duracao_s / 60) if self.duracao_s else 0.0


def _norm(nome: str) -> str:
    return nome.replace(" ", "").replace("_", "").lower()


def _col(header: list[str], opcoes: tuple[str, ...]) -> str | None:
    por_nome = {_norm(h): h for h in header}
    for c in opcoes:
        if _norm(c) in por_nome:
            return por_nome[_norm(c)]
    return None


def _float(v: str) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) and f > 0 else None


def ler_csv(path: Path, processo: str | None = None) -> tuple[list[float], list[float], dict[str, list[float]]]:
    """Retorna (frametimes_ms, gpu_busy_ms, telemetria) do CSV."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        # CapFrameX às vezes coloca linhas de comentário antes do cabeçalho.
        linhas = [l for l in fh if not l.startswith("//") and l.strip()]
    reader = csv.DictReader(linhas)
    header = reader.fieldnames or []
    ft_col = _col(header, FRAMETIME_COLS)
    if ft_col is None:
        raise ValueError(f"{path}: nenhuma coluna de frametime encontrada ({', '.join(FRAMETIME_COLS)})")
    gpu_col = _col(header, GPU_BUSY_COLS)
    app_col = _col(header, APP_COLS)
    tele_cols = {k: c for k, opcoes in TELEMETRIA_COLS.items() if (c := _col(header, opcoes))}

    frametimes: list[float] = []
    gpu: list[float] = []
    tele: dict[str, list[float]] = {k: [] for k in tele_cols}
    for row in reader:
        if processo and app_col and row.get(app_col, "").lower() != processo.lower():
            continue
        ft = _float(row.get(ft_col, ""))
        if ft is None:
            continue
        frametimes.append(ft)
        if gpu_col:
            g = _float(row.get(gpu_col, ""))
            if g is not None:
                gpu.append(g)
        for k, c in tele_cols.items():
            if (v := _float(row.get(c, ""))) is not None:
                tele[k].append(v)
    if not frametimes:
        raise ValueError(f"{path}: nenhum frame válido")
    return frametimes, gpu, {k: v for k, v in tele.items() if v}


def percentil(valores_ordenados: list[float], p: float) -> float:
    """Percentil com interpolação linear (p entre 0 e 100)."""
    if not valores_ordenados:
        return float("nan")
    k = (len(valores_ordenados) - 1) * p / 100
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return valores_ordenados[int(k)]
    return valores_ordenados[f] + (valores_ordenados[c] - valores_ordenados[f]) * (k - f)


def low_pct(frametimes: list[float], pct: float) -> float:
    """"1% low" = FPS médio dos pct% frames mais lentos (definição usada pelo CapFrameX)."""
    piores = sorted(frametimes, reverse=True)
    n = max(1, int(len(piores) * pct / 100))
    return 1000 / statistics.fmean(piores[:n])


def analisar(frametimes: list[float], gpu_busy: list[float], nome: str,
             telemetria: dict[str, list[float]] | None = None) -> Resultado:
    ordenados = sorted(frametimes)
    total_ms = sum(frametimes)
    mediana = statistics.median(frametimes)
    stutters = sum(1 for f in frametimes if f > mediana * STUTTER_FACTOR)

    gpu_pct = None
    gargalo = "desconhecido (sem coluna de GPU busy)"
    if gpu_busy and len(gpu_busy) == len(frametimes):
        gpu_pct = 100 * sum(gpu_busy) / total_ms
        if gpu_pct >= LIMIAR_GPU:
            gargalo = "GPU"
        elif gpu_pct < LIMIAR_CPU:
            gargalo = "CPU (ou limitador de FPS/V-Sync)"
        else:
            gargalo = "misto"

    return Resultado(
        nome=nome,
        frames=len(frametimes),
        duracao_s=total_ms / 1000,
        fps_medio=1000 * len(frametimes) / total_ms,
        fps_mediana=1000 / mediana,
        low_1=low_pct(frametimes, 1),
        low_01=low_pct(frametimes, 0.1),
        p99_ms=percentil(ordenados, 99),
        desvio_ms=statistics.pstdev(frametimes),
        stutters=stutters,
        gpu_busy_pct=gpu_pct,
        gargalo=gargalo,
        telemetria={k: (statistics.fmean(v), max(v)) for k, v in (telemetria or {}).items()} or None,
    )


def analisar_arquivo(path: Path, processo: str | None = None) -> Resultado:
    ft, gpu, tele = ler_csv(path, processo)
    return analisar(ft, gpu, path.stem, tele)


def _delta(novo: float, base: float, maior_melhor: bool = True) -> str:
    if not base:
        return ""
    d = 100 * (novo - base) / base
    melhor = d > 0 if maior_melhor else d < 0
    sinal = "+" if d >= 0 else ""
    marca = "▲" if melhor and abs(d) >= 1 else ("▼" if not melhor and abs(d) >= 1 else "=")
    return f" ({sinal}{d:.1f}% {marca})"


def tabela_markdown(resultados: list[Resultado]) -> str:
    base = resultados[0]
    linhas = [
        "| Execução | FPS médio | 1% low | 0.1% low | p99 frametime | Stutters/min | GPU busy | Gargalo |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in resultados:
        eh_base = r is base
        gpu = f"{r.gpu_busy_pct:.0f}%" if r.gpu_busy_pct is not None else "—"
        linhas.append(
            "| {nome} | {fps:.1f}{dfps} | {l1:.1f}{dl1} | {l01:.1f}{dl01} | {p99:.2f} ms{dp99} | {st:.1f}{dst} | {gpu} | {garg} |".format(
                nome=r.nome + (" (base)" if eh_base else ""),
                fps=r.fps_medio, dfps="" if eh_base else _delta(r.fps_medio, base.fps_medio),
                l1=r.low_1, dl1="" if eh_base else _delta(r.low_1, base.low_1),
                l01=r.low_01, dl01="" if eh_base else _delta(r.low_01, base.low_01),
                p99=r.p99_ms, dp99="" if eh_base else _delta(r.p99_ms, base.p99_ms, maior_melhor=False),
                st=r.stutters_por_min, dst="" if eh_base else _delta(r.stutters_por_min, base.stutters_por_min, maior_melhor=False),
                gpu=gpu, garg=r.gargalo,
            )
        )
    tele = [r for r in resultados if r.telemetria]
    if tele:
        nomes = {"gpu_util_pct": "GPU uso %", "gpu_temp_c": "GPU °C", "gpu_power_w": "GPU W",
                 "cpu_util_pct": "CPU uso %", "cpu_temp_c": "CPU °C"}
        chaves = [k for k in nomes if any(k in r.telemetria for r in tele)]
        linhas += ["", "| Execução | " + " | ".join(f"{nomes[k]} (méd/máx)" for k in chaves) + " |",
                   "|---|" + "---|" * len(chaves)]
        for r in tele:
            cel = [f"{r.telemetria[k][0]:.0f} / {r.telemetria[k][1]:.0f}" if k in r.telemetria else "—" for k in chaves]
            linhas.append(f"| {r.nome} | " + " | ".join(cel) + " |")
    return "\n".join(linhas)


def recomendacoes(resultados: list[Resultado]) -> list[str]:
    """Dicas simples baseadas na última execução comparada à base."""
    dicas: list[str] = []
    ultimo = resultados[-1]
    if ultimo.gargalo.startswith("CPU"):
        dicas.append(
            "Gargalo de CPU: no iRacing isso é o normal. Reduza o que pesa na CPU (nº de carros visíveis, "
            "detalhe de carros/pista distantes, sombras dinâmicas, espelhos, crowd/objetos) antes de mexer em "
            "resolução/AA. Aumentar qualidade de texturas/AA/anisotrópico tende a ser 'grátis' nesse cenário."
        )
    elif ultimo.gargalo == "GPU":
        dicas.append(
            "Gargalo de GPU: reduza MSAA/SSAA, resolução, pós-processamento e sombras; aqui cada ajuste gráfico "
            "vira FPS direto."
        )
    t = ultimo.telemetria or {}
    if "gpu_temp_c" in t and t["gpu_temp_c"][1] >= 83:
        dicas.append(f"GPU chegou a {t['gpu_temp_c'][1]:.0f} °C: verifique fluxo de ar/curva de ventoinha antes de mexer em gráficos.")
    if "cpu_temp_c" in t and t["cpu_temp_c"][1] >= 95:
        dicas.append(f"CPU chegou a {t['cpu_temp_c'][1]:.0f} °C: provável thermal throttling (confirme no HWiNFO).")
    if ultimo.low_1 < 0.6 * ultimo.fps_medio:
        dicas.append(
            "1% low muito abaixo da média → stutter. Verifique VRAM/RAM, gravação em segundo plano, overlays, "
            "e use um limitador de FPS (ex.: RTSS/driver) um pouco abaixo do FPS mínimo sustentado."
        )
    if len(resultados) > 1:
        base = resultados[0]
        if ultimo.fps_medio > base.fps_medio * 1.02 and ultimo.low_1 < base.low_1 * 0.97:
            dicas.append(
                f"'{ultimo.nome}' subiu o FPS médio mas piorou o 1% low: para simulador, prefira consistência "
                "(1% low e p99) ao FPS médio."
            )
    return dicas


def grafico(resultados_ft: list[tuple[str, list[float]]], saida: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado; pulei o gráfico (pip install matplotlib)", file=sys.stderr)
        return
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8))
    for nome, ft in resultados_ft:
        t, acc = [], 0.0
        for f in ft:
            acc += f
            t.append(acc / 1000)
        ax1.plot(t, ft, linewidth=0.7, label=nome)
        ordenados = sorted(ft)
        ax2.plot([100 * i / len(ordenados) for i in range(len(ordenados))], ordenados, label=nome)
    ax1.set(title="Frametime ao longo do tempo", xlabel="segundos", ylabel="ms (menor = melhor)")
    ax2.set(title="Distribuição de frametime (percentis)", xlabel="percentil", ylabel="ms", xlim=(90, 100))
    for ax in (ax1, ax2):
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(saida, dpi=120)
    print(f"Gráfico salvo em {saida}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome in ("resumo", "comparar"):
        s = sub.add_parser(nome)
        s.add_argument("arquivos", nargs="+", type=Path)
        s.add_argument("--processo", help="filtra por nome do executável (ex.: iRacingSim64DX11.exe)")
        s.add_argument("--markdown", type=Path, help="salva a tabela em um arquivo .md")
        s.add_argument("--grafico", type=Path, help="salva um gráfico .png (requer matplotlib)")
    args = p.parse_args(argv)

    resultados, series = [], []
    for arq in args.arquivos:
        ft, gpu, tele = ler_csv(arq, args.processo)
        resultados.append(analisar(ft, gpu, arq.stem, tele))
        series.append((arq.stem, ft))

    tabela = tabela_markdown(resultados)
    dicas = recomendacoes(resultados)
    texto = tabela + ("\n\n**Leitura:**\n" + "\n".join(f"- {d}" for d in dicas) if dicas else "")
    print(texto)
    if args.markdown:
        args.markdown.write_text("# Comparação de benchmarks\n\n" + texto + "\n", encoding="utf-8")
    if args.grafico:
        grafico(series, args.grafico)
    return 0


if __name__ == "__main__":
    sys.exit(main())
