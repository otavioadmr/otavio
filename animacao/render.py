"""Renderiza os quadros (em paralelo) -> build/video_mudo.mp4

uso: python3 render.py            (vídeo inteiro)
     python3 render.py --png 12.5 (salva um quadro de teste no tempo dado)
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import cairo
import desenho as D
from cenas import CENAS, TINTA

FPS = 24
AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
TL = json.load(open(os.path.join(BUILD, "timeline.json")))

COR_FALA = {"narrador": D.BRANCO, "teo": (0.7, 0.88, 1.0), "vo": (0.88, 0.78, 1.0),
            "nanquim": (0.85, 0.85, 0.85), "careca": (0.75, 1.0, 0.75)}
SEM_LEGENDA = {"rabisco"}


class G:
    t = 0.0

    @staticmethod
    def fala(quem):
        for f in TL["falas"]:
            if f["quem"] == quem and f["ini"] <= G.t < f["fim"]:
                i = int((G.t - f["ini"]) * FPS)
                env = f["env"]
                v = env[i] if i < len(env) else 0
                return min(1.0, v * 1.4) if v > 0.12 else 0.0
        return 0.0


def legenda(ctx, t):
    for f in TL["falas"]:
        if f["cena"] == "titulo" or f["quem"] in SEM_LEGENDA:
            continue
        if f["ini"] - 0.05 <= t < f["fim"] + 0.15:
            linhas = D.quebra(ctx, f["texto"], 900, 74, "Patrick Hand")
            a = min(1.0, (t - f["ini"] + 0.05) / 0.12)
            y0 = 1560 - (len(linhas) - 1) * 42
            for k, l in enumerate(linhas):
                D.texto(ctx, l, 540, y0 + k * 84, 74, "Patrick Hand", fill=COR_FALA.get(f["quem"], D.BRANCO),
                        stroke=TINTA, sw=14, alpha=a)
            return


def desenha_quadro(ctx, f):
    t = f / FPS
    G.t = t
    D.S.frame = f
    D.S.ink = TINTA
    cena = TL["cenas"][-1]
    for c in TL["cenas"]:
        if c["ini"] <= t < c["fim"]:
            cena = c
            break
    ctx.save()
    CENAS[cena["nome"]](ctx, t - cena["ini"], cena["ev"], G)
    ctx.restore()
    D.S.ink = TINTA
    legenda(ctx, t)


def render_trecho(args):
    i, f0, f1 = args
    out = os.path.join(BUILD, f"trecho_{i:02d}.mp4")
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                             "-s", f"{D.W}x{D.H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                             "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                            stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, D.W, D.H)
    ctx = cairo.Context(surf)
    for f in range(f0, f1):
        ctx.save()
        desenha_quadro(ctx, f)
        ctx.restore()
        surf.flush()
        proc.stdin.write(bytes(surf.get_data()))
    proc.stdin.close()
    proc.wait()
    return out


def main():
    if "--png" in sys.argv:
        for tt in sys.argv[sys.argv.index("--png") + 1:]:
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, D.W, D.H)
            ctx = cairo.Context(surf)
            desenha_quadro(ctx, int(float(tt) * FPS))
            surf.write_to_png(os.path.join(BUILD, f"quadro_{float(tt):06.2f}.png"))
        return
    total = int(math.ceil(TL["duracao"] * FPS))
    n = int(os.environ.get("TRECHOS", "16"))
    passo = math.ceil(total / n)
    tarefas = [(i, i * passo, min(total, (i + 1) * passo)) for i in range(n) if i * passo < total]
    with Pool(os.cpu_count()) as p:
        outs = p.map(render_trecho, tarefas)
    lista = os.path.join(BUILD, "trechos.txt")
    with open(lista, "w") as fh:
        for o in outs:
            fh.write(f"file '{o}'\n")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy",
                    os.path.join(BUILD, "video_mudo.mp4")], check=True)
    for o in outs:
        os.remove(o)
    print("ok:", total, "quadros")


if __name__ == "__main__":
    main()
