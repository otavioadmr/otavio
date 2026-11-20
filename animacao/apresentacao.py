"""Vídeo de apresentação do Gabriel (mascote do canal) -> ../mascote/Gabriel_apresentacao.mp4"""
import math, os, subprocess, wave
import cairo
import numpy as np
import desenho as D
import mascote as M
import audio as A
from linha_do_tempo import gera_voz, envelope, BUILD

FPS = 24
TINTA = (0.10, 0.09, 0.12)
FALAS = [
    "Fala, galera! Eu sou o Gabriel!",
    "Aqui no canal, toda semana tem história nova... desenhada do zero.",
    "Então já segue aí, porque a próxima tá chegando!",
]

# ---- linha do tempo
os.makedirs(BUILD, exist_ok=True)
t = 0.7
falas = []
for txt in FALAS:
    arq = gera_voz("narrador", txt)
    with wave.open(arq) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    falas.append({"texto": txt, "ini": t, "fim": t + len(a) / A.SR, "audio": a, "env": envelope(a.astype(np.float32))})
    t = falas[-1]["fim"] + 0.35
PISCA = t
FIM = t + 2.6
F1, F2, F3 = falas


def fase(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else float(t >= b)


def fala_em(t):
    for f in falas:
        if f["ini"] <= t < f["fim"]:
            i = int((t - f["ini"]) * FPS)
            v = f["env"][i] if i < len(f["env"]) else 0
            return min(1.0, v * 1.4) if v > 0.12 else 0.0
    return 0.0


def quadro(ctx, f):
    t = f / FPS
    D.S.frame = f
    D.S.ink = TINTA
    D.papel(ctx)
    chao = 1500
    # casinhas sendo desenhadas durante a 2ª fala
    for k, x in enumerate([90, 760]):
        D.casa(ctx, x, chao, 230, 200, telhado=[D.VERMELHO, D.VERDE][k],
               prog=fase(t, F2["ini"] + k * 0.6, F2["ini"] + 1.8 + k * 0.6))
    D.arvore(ctx, 960, chao, 0.7, prog=fase(t, F2["ini"] + 1.5, F2["ini"] + 3.0))
    D.chao(ctx, chao)
    # entrada com pulo
    ent = fase(t, 0.0, 0.5)
    pulo = math.sin(ent * math.pi) * 160 if ent < 1 else 0
    esc = 0.92 * (0.6 + 0.4 * ent)
    humor, bd, dd, be, de, aceno, olhar = "normal", 0.2, 0.1, 0.15, 0.1, False, (0, 0)
    if F1["ini"] - 0.2 <= t < F1["fim"] + 0.2:
        humor, bd, dd, aceno = "feliz" if fala_em(t) == 0 else "normal", 2.5, 0.5, True
    elif F2["ini"] <= t < F2["fim"] + 0.2:
        be, de, bd, dd, olhar = 1.2, 1.2, 1.2, 1.2, (-1, 0)  # braços abertos apresentando
    elif F3["ini"] <= t < PISCA:
        bd, dd, olhar = 2.2, 0.05, (1, -1)  # aponta pro botão
    elif t >= PISCA:
        humor, bd, dd = "piscadinha", 2.6, 0.9  # joinha/aceno final
    if t < 0.5:
        humor = "susto"
    M.desenha(ctx, 540, chao, esc, humor=humor, fala=fala_em(t), t=t, braco_e=be, braco_d=bd, dobra_e=de,
              dobra_d=dd, aceno=aceno, olhar=olhar, pulo=pulo)
    D.brilhos(ctx, 540, chao - 600, fase(t, 0.45, 1.1), 10, 320)
    # nome
    a = fase(t, F1["ini"] + 0.9, F1["ini"] + 1.1)
    if a > 0:
        D.texto(ctx, "GABRIEL", 540, 250, 150 * (1 + 0.15 * math.sin(fase(t, F1["ini"] + 0.9, F1["ini"] + 1.3) * math.pi)),
                fill=M.PALETA["bone"], stroke=TINTA, sw=22, alpha=a)
    # botão "SEGUE"
    if t >= F3["ini"] + 0.6:
        b = fase(t, F3["ini"] + 0.6, F3["ini"] + 0.9)
        pul = 1 + 0.06 * math.sin(t * 9)
        ctx.save()
        ctx.translate(830, 470)
        ctx.scale(b * pul, b * pul)
        D.forma(ctx, [(-150, -60), (150, -60), (150, 60), (-150, 60)], fill=D.VERMELHO, w=8)
        D.texto(ctx, "SEGUE +", 0, 22, 70, fill=D.BRANCO, stroke=TINTA, sw=10)
        ctx.restore()
    # legenda
    for fl in falas:
        if fl["ini"] - 0.05 <= t < fl["fim"] + 0.15:
            linhas = D.quebra(ctx, fl["texto"], 900, 74, "Patrick Hand")
            y0 = 1680 - (len(linhas) - 1) * 42
            for k, l in enumerate(linhas):
                D.texto(ctx, l, 540, y0 + k * 84, 74, "Patrick Hand", fill=D.BRANCO, stroke=TINTA, sw=14)


def video_mudo(out):
    proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s",
                             f"{D.W}x{D.H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                             "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, D.W, D.H)
    ctx = cairo.Context(surf)
    for f in range(int(FIM * FPS)):
        ctx.save()
        quadro(ctx, f)
        ctx.restore()
        surf.flush()
        proc.stdin.write(bytes(surf.get_data()))
    proc.stdin.close()
    proc.wait()


def trilha(out):
    n = int((FIM + 0.5) * A.SR)
    voz, efe, mus = np.zeros(n), np.zeros(n), np.zeros(n)
    for f in falas:
        A.add(voz, f["ini"], f["audio"] / (np.max(np.abs(f["audio"])) + 1e-9) * 0.8)
    A.add(efe, 0.0, A.sfx("whoosh", 0), 0.7)
    A.add(efe, 0.45, A.sfx("pop", 0))
    A.add(efe, 0.5, A.sfx("brilho", 0))
    A.add(efe, F1["ini"] + 0.9, A.sfx("plink", 0))
    A.add(efe, F2["ini"], A.sfx("rabisco", 2.5))
    A.add(efe, F3["ini"] + 0.6, A.sfx("boing", 0))
    A.add(efe, PISCA, A.sfx("brilho", 0))
    m = A.tema(FIM + 0.5, 116)
    fade = int(1.0 * A.SR)
    m[-fade:] *= np.linspace(1, 0, fade)
    A.add(mus, 0, m)
    env = np.convolve(np.abs(voz), np.ones(int(0.15 * A.SR)) / int(0.15 * A.SR), mode="same")
    mix = voz + efe * 0.8 + mus * 0.42 * (1 - 0.55 * np.clip(env / 0.05, 0, 1))
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.95
    with wave.open(out, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(A.SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    import sys
    if "--png" in sys.argv:
        for tt in sys.argv[sys.argv.index("--png") + 1:]:
            s = cairo.ImageSurface(cairo.FORMAT_ARGB32, D.W, D.H)
            quadro(cairo.Context(s), int(float(tt) * FPS))
            s.write_to_png(os.path.join(BUILD, f"apres_{float(tt):05.2f}.png"))
        print("tempos:", [(round(f["ini"], 2), round(f["fim"], 2)) for f in falas], "fim", round(FIM, 2))
        sys.exit()
    v, a = os.path.join(BUILD, "apres_mudo.mp4"), os.path.join(BUILD, "apres_audio.wav")
    video_mudo(v)
    trilha(a)
    dest = os.path.join(os.path.dirname(BUILD), "..", "mascote", "Gabriel_apresentacao.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", v, "-i", a, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", "-movflags",
                    "+faststart", "-shortest", dest], check=True)
    print("ok", os.path.abspath(dest), round(FIM, 2), "s")
