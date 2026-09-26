import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RAIZ / "analysis"), str(RAIZ / "iracing")]

import analisar  # noqa: E402
import iracing_ini  # noqa: E402


def escrever_csv(pasta: Path, nome: str, header: str, linhas: list[str]) -> Path:
    p = pasta / nome
    p.write_text(header + "\n" + "\n".join(linhas) + "\n", encoding="utf-8")
    return p


class TestAnalisar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_fps_constante(self):
        p = escrever_csv(self.tmp, "a.csv", "Application,MsBetweenPresents,MsGPUActive",
                         ["iRacingSim64DX11.exe,10.0,9.8"] * 1000)
        r = analisar.analisar_arquivo(p)
        self.assertAlmostEqual(r.fps_medio, 100.0)
        self.assertAlmostEqual(r.low_1, 100.0)
        self.assertEqual(r.stutters, 0)
        self.assertEqual(r.gargalo, "GPU")

    def test_low_e_stutter_e_gargalo_cpu(self):
        linhas = ["x.exe,10.0,5.0"] * 990 + ["x.exe,40.0,5.0"] * 10
        p = escrever_csv(self.tmp, "b.csv", "Application,MsBetweenPresents,MsGPUActive", linhas)
        r = analisar.analisar_arquivo(p)
        self.assertAlmostEqual(r.low_1, 25.0)
        self.assertEqual(r.stutters, 10)
        self.assertTrue(r.gargalo.startswith("CPU"))

    def test_presentmon_v2_e_filtro_processo(self):
        linhas = ["jogo.exe,8.0,7.9"] * 50 + ["outro.exe,100.0,1.0"] * 50
        p = escrever_csv(self.tmp, "c.csv", "Application,FrameTime,GPUBusy", linhas)
        r = analisar.analisar_arquivo(p, processo="jogo.exe")
        self.assertEqual(r.frames, 50)
        self.assertAlmostEqual(r.fps_medio, 125.0)

    def test_presentmon_v2_msgpubusy_e_telemetria(self):
        linhas = ["jogo.exe,10.0,6.0,60,70"] * 99 + ["jogo.exe,10.0,6.0,60,88"]
        p = escrever_csv(self.tmp, "t.csv", "Application,MsBetweenPresents,MsGPUBusy,GPU Utilization,GPU_Temperature", linhas)
        r = analisar.analisar_arquivo(p)
        self.assertAlmostEqual(r.gpu_busy_pct, 60.0)
        self.assertTrue(r.gargalo.startswith("CPU"))
        self.assertEqual(r.telemetria["gpu_temp_c"][1], 88)
        tabela = analisar.tabela_markdown([r])
        self.assertIn("GPU °C", tabela)
        self.assertTrue(any("88 °C" in d for d in analisar.recomendacoes([r])))

    def test_limiar_misto(self):
        p = escrever_csv(self.tmp, "m.csv", "MsBetweenPresents,MsGPUBusy", ["10,8"] * 10)
        self.assertEqual(analisar.analisar_arquivo(p).gargalo, "misto")

    def test_comparar_markdown(self):
        a = escrever_csv(self.tmp, "base.csv", "MsBetweenPresents", ["10"] * 100)
        b = escrever_csv(self.tmp, "novo.csv", "MsBetweenPresents", ["8"] * 100)
        md = self.tmp / "r.md"
        self.assertEqual(analisar.main(["comparar", str(a), str(b), "--markdown", str(md)]), 0)
        texto = md.read_text(encoding="utf-8")
        self.assertIn("+25.0%", texto)

    def test_sem_coluna(self):
        p = escrever_csv(self.tmp, "d.csv", "foo,bar", ["1,2"])
        with self.assertRaises(ValueError):
            analisar.analisar_arquivo(p)


class TestIni(unittest.TestCase):
    INI = [
        "[Drawing]",
        "VisibilityFrameDelay=5                ; comentario",
        "Outra=1",
        "",
        "[Graphics]",
        "fps=0",
    ]

    def test_set_preserva_comentario(self):
        linhas, antigo = iracing_ini.definir(self.INI, "drawing", "visibilityframedelay", "0")
        self.assertEqual(antigo, "5")
        self.assertIn("; comentario", linhas[1])
        self.assertEqual(iracing_ini.parse(linhas)["Drawing"]["VisibilityFrameDelay"], "0")

    def test_set_chave_nova_na_secao_certa(self):
        linhas, antigo = iracing_ini.definir(self.INI, "Drawing", "Nova", "7")
        self.assertIsNone(antigo)
        self.assertEqual(linhas.index("Nova=7"), 3)

    def test_set_secao_nova(self):
        linhas, _ = iracing_ini.definir(self.INI, "Extra", "k", "v")
        self.assertEqual(iracing_ini.parse(linhas)["Extra"], {"k": "v"})

    def test_aplicar_cria_backup(self):
        tmp = Path(tempfile.mkdtemp())
        arq = tmp / "renderer.ini"
        arq.write_text("\n".join(self.INI), encoding="utf-8")
        preset = tmp / "p.ini"
        preset.write_text("[Graphics]\nfps=120\n", encoding="utf-8")
        iracing_ini.main(["aplicar", str(arq), str(preset)])
        self.assertEqual(iracing_ini.parse(iracing_ini.ler(arq))["Graphics"]["fps"], "120")
        self.assertEqual(len(list(tmp.glob("renderer.ini.*.bak"))), 1)


if __name__ == "__main__":
    unittest.main()
