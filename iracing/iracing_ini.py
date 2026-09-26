#!/usr/bin/env python3
"""Ferramenta para versionar e ajustar os .ini do iRacing sem perder comentários.

Os arquivos ficam em  Documentos\\iRacing\\  (app.ini, rendererDX11Monitor.ini, rendererDX11.ini ...).
Feche o iRacing antes de editar: o sim reescreve os .ini ao sair.

Uso:
    python iracing/iracing_ini.py backup  "C:/Users/voce/Documents/iRacing"
    python iracing/iracing_ini.py get     app.ini Graphics
    python iracing/iracing_ini.py set     rendererDX11Monitor.ini Drawing SomeKey 0
    python iracing/iracing_ini.py diff    backup/rendererDX11Monitor.ini rendererDX11Monitor.ini
    python iracing/iracing_ini.py aplicar rendererDX11Monitor.ini iracing/presets/exemplo.ini

Um "preset" é um .ini com apenas as chaves que você quer mudar; tudo o que não está nele fica igual.
Toda escrita cria antes um .bak com data/hora ao lado do arquivo.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

SECAO = re.compile(r"^\s*\[(?P<nome>[^\]]+)\]")
CHAVE = re.compile(r"^(?P<ind>\s*)(?P<k>[^;=\[\s][^=]*?)\s*=\s*(?P<v>[^;]*?)(?P<resto>\s*;.*)?$")


def ler(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def parse(linhas: list[str]) -> dict[str, dict[str, str]]:
    dados: dict[str, dict[str, str]] = {}
    secao = ""
    for l in linhas:
        if m := SECAO.match(l):
            secao = m["nome"].strip()
            dados.setdefault(secao, {})
        elif m := CHAVE.match(l):
            dados.setdefault(secao, {})[m["k"].strip()] = m["v"].strip()
    return dados


def definir(linhas: list[str], secao: str, chave: str, valor: str) -> tuple[list[str], str | None]:
    """Define secao/chave=valor preservando comentários. Retorna (linhas, valor_antigo)."""
    atual = ""
    inicio_secao = fim_secao = None
    for i, l in enumerate(linhas):
        if m := SECAO.match(l):
            if atual.lower() == secao.lower() and fim_secao is None:
                fim_secao = i
            atual = m["nome"].strip()
            if atual.lower() == secao.lower():
                inicio_secao = i
            continue
        if atual.lower() == secao.lower() and (m := CHAVE.match(l)) and m["k"].strip().lower() == chave.lower():
            antigo = m["v"].strip()
            linhas = linhas.copy()
            linhas[i] = f"{m['ind']}{m['k'].strip()}={valor}{m['resto'] or ''}"
            return linhas, antigo
    linhas = linhas.copy()
    if inicio_secao is None:
        linhas += ["", f"[{secao}]", f"{chave}={valor}"]
    else:
        pos = fim_secao if fim_secao is not None else len(linhas)
        while pos > inicio_secao + 1 and not linhas[pos - 1].strip():
            pos -= 1
        linhas.insert(pos, f"{chave}={valor}")
    return linhas, None


def backup(path: Path) -> Path:
    destino = path.with_suffix(path.suffix + f".{datetime.now():%Y%m%d-%H%M%S}.bak")
    shutil.copy2(path, destino)
    return destino


def gravar(path: Path, linhas: list[str]) -> None:
    b = backup(path)
    path.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Salvo {path} (backup: {b.name})")


def cmd_backup(pasta: Path, destino: Path) -> None:
    alvo = destino / datetime.now().strftime("%Y%m%d-%H%M%S")
    alvo.mkdir(parents=True, exist_ok=True)
    arquivos = sorted(pasta.glob("*.ini"))
    for arq in arquivos:
        shutil.copy2(arq, alvo / arq.name)
    print(f"{len(arquivos)} arquivos .ini copiados para {alvo}")


def cmd_diff(a: Path, b: Path) -> int:
    da, db = parse(ler(a)), parse(ler(b))
    mudancas = 0
    for secao in sorted(set(da) | set(db)):
        ka, kb = da.get(secao, {}), db.get(secao, {})
        for k in sorted(set(ka) | set(kb)):
            if ka.get(k) != kb.get(k):
                mudancas += 1
                print(f"[{secao}] {k}: {ka.get(k, '(ausente)')} -> {kb.get(k, '(ausente)')}")
    if not mudancas:
        print("Sem diferenças.")
    return mudancas


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("backup", help="copia todos os .ini da pasta do iRacing")
    s.add_argument("pasta", type=Path)
    s.add_argument("--destino", type=Path, default=Path("iracing/backups"))
    s = sub.add_parser("get", help="mostra uma seção (ou uma chave)")
    s.add_argument("arquivo", type=Path)
    s.add_argument("secao")
    s.add_argument("chave", nargs="?")
    s = sub.add_parser("set", help="altera uma chave")
    s.add_argument("arquivo", type=Path)
    s.add_argument("secao")
    s.add_argument("chave")
    s.add_argument("valor")
    s = sub.add_parser("diff", help="diferenças entre dois .ini")
    s.add_argument("a", type=Path)
    s.add_argument("b", type=Path)
    s = sub.add_parser("aplicar", help="aplica um preset (.ini parcial)")
    s.add_argument("arquivo", type=Path)
    s.add_argument("preset", type=Path)
    args = p.parse_args(argv)

    if args.cmd == "backup":
        cmd_backup(args.pasta, args.destino)
    elif args.cmd == "get":
        secao = next((v for k, v in parse(ler(args.arquivo)).items() if k.lower() == args.secao.lower()), {})
        for k, v in secao.items():
            if args.chave is None or k.lower() == args.chave.lower():
                print(f"{k}={v}")
    elif args.cmd == "set":
        linhas, antigo = definir(ler(args.arquivo), args.secao, args.chave, args.valor)
        print(f"[{args.secao}] {args.chave}: {antigo if antigo is not None else '(nova)'} -> {args.valor}")
        gravar(args.arquivo, linhas)
    elif args.cmd == "diff":
        cmd_diff(args.a, args.b)
    elif args.cmd == "aplicar":
        linhas = ler(args.arquivo)
        for secao, chaves in parse(ler(args.preset)).items():
            for k, v in chaves.items():
                linhas, antigo = definir(linhas, secao, k, v)
                print(f"[{secao}] {k}: {antigo if antigo is not None else '(nova)'} -> {v}")
        gravar(args.arquivo, linhas)
    return 0


if __name__ == "__main__":
    sys.exit(main())
