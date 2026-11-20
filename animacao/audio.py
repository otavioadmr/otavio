"""Trilha original + efeitos sonoros + vozes -> build/audio.wav (tudo sintetizado, sem direitos autorais)."""
import json, os, wave
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
TL = N = None


def carrega_timeline():
    global TL, N
    TL = json.load(open(os.path.join(BUILD, "timeline.json")))
    N = int((TL["duracao"] + 0.5) * SR)
rng = np.random.RandomState(42)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def filtro(x, tipo, f):
    sos = butter(2, f, btype=tipo, fs=SR, output="sos")
    return sosfilt(sos, x)


def add(buf, t0, x, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * g


# ------------------------------------------------------------ instrumentos
def pluck(f, d=0.5, brilho=1.0):
    t = tt(d)
    x = (np.sin(2 * np.pi * f * t) + 0.5 * brilho * np.sin(4 * np.pi * f * t) + 0.25 * brilho * np.sin(6 * np.pi * f * t))
    env = np.exp(-t * 7) * np.minimum(1, t * 400)
    return x * env * 0.35


def marimba(f, d=0.4):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)
    return x * np.exp(-t * 9) * np.minimum(1, t * 600) * 0.4


def baixo(f, d=0.4):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    return x * np.exp(-t * 4) * np.minimum(1, t * 300) * 0.45


def bumbo():
    t = tt(0.25)
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.8


def estalo():
    t = tt(0.15)
    return filtro(rng.randn(len(t)), "highpass", 1500) * np.exp(-t * 35) * 0.35


def chocalho():
    t = tt(0.06)
    return filtro(rng.randn(len(t)), "highpass", 6000) * np.exp(-t * 60) * 0.15


def sino(f, d=1.5):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 4) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 8)
    return x * np.exp(-t * 3) * np.minimum(1, t * 800) * 0.3


def pad(freqs, d):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t + 1) + 0.2 * np.sin(4 * np.pi * f * t)
            for f in freqs) / len(freqs)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.8)
    return x * env * 0.3


# ------------------------------------------------------------ estilos de música
ACORDES = {"C": [48, 52, 55], "Am": [45, 48, 52], "F": [41, 45, 48], "G": [43, 47, 50], "Em": [40, 43, 47],
           "Dm": [38, 41, 45]}
MELODIA = [  # (batida, nota midi, duração) em 4 compassos
    (0, 76, .5), (1, 79, .5), (2, 81, .5), (2.5, 79, .5), (3, 76, .5),
    (4, 72, .5), (5, 76, .5), (6, 74, .5), (7, 72, .5), (7.5, 69, .5),
    (8, 69, .5), (9, 72, .5), (10, 77, .5), (10.5, 76, .5), (11, 74, .5), (11.5, 72, .5),
    (12, 74, .5), (13.5, 71, .5), (14, 67, 1.0),
]


def tema(d, bpm=112, suave=False, melodia=True):
    buf = np.zeros(int(d * SR) + SR)
    b = 60 / bpm
    prog = ["C", "Am", "F", "G"]
    beat = 0
    while beat * b < d:
        compasso = int(beat // 4) % 4
        ac = ACORDES[prog[compasso]]
        t0 = beat * b
        # baixo nos tempos 1 e 3
        if beat % 2 == 0:
            add(buf, t0, baixo(mtof(ac[0] - 12 + (7 if beat % 4 == 2 else 0)), b * 1.8))
        # acorde em contratempo (ukulele)
        for k, n in enumerate(ac):
            add(buf, t0 + b * 0.5 + k * 0.012, pluck(mtof(n + 12), 0.35, 0.6), 0.5 if suave else 0.6)
        if not suave:
            if beat % 2 == 0:
                add(buf, t0, bumbo(), 0.7)
            else:
                add(buf, t0, estalo(), 0.8)
            add(buf, t0 + b * 0.5, chocalho())
            add(buf, t0, chocalho(), 0.6)
        beat += 1
    if melodia:
        ciclo = 16 * b
        c = 0
        while c * ciclo < d:
            for bt, nota, du in MELODIA:
                tm = c * ciclo + bt * b
                if tm < d:
                    add(buf, tm, marimba(mtof(nota), du * b * 2), 0.55 if suave else 0.75)
            c += 1
    return buf[:int(d * SR)]


def tensao(d):
    buf = np.zeros(int(d * SR) + SR)
    t = tt(d)
    # pulso grave que acelera e sobe
    f = 55 * (1 + 0.5 * t / d)
    drone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.08
    buf[:len(t)] += drone * np.minimum(1, t / 0.5) * (0.6 + 0.6 * t / d)
    pos, intervalo = 0.0, 0.5
    while pos < d:
        add(buf, pos, bumbo(), 0.5)
        pos += intervalo
        intervalo = max(0.18, intervalo * 0.97)
    for k, n in enumerate([57, 58, 59, 60, 61, 62, 63, 64]):
        tm = k * d / 8
        add(buf, tm, pluck(mtof(n), 0.6, 0.3), 0.6)
    return buf[:len(t)]


def emocional(d):
    buf = np.zeros(int(d * SR) + SR)
    seq = [("F", 0), ("C", 1), ("G", 2), ("Am", 3)]
    passo = d / 4
    for nome, k in seq:
        ac = ACORDES[nome]
        add(buf, k * passo, pad([mtof(n + 12) for n in ac], passo + 0.6), 0.9)
        for j, n in enumerate(ac + [ac[0] + 12, ac[1] + 12]):
            add(buf, k * passo + j * passo / 6, sino(mtof(n + 24), 1.4), 0.35)
    return buf[:int(d * SR)]


def misterio(d):
    buf = np.zeros(int(d * SR) + SR)
    t = tt(d)
    buf[:len(t)] += (np.sin(2 * np.pi * 41.2 * t) * 0.3 + np.sin(2 * np.pi * 61.7 * t) * 0.12) * np.minimum(1, t / 1.0)
    for k, n in enumerate([84, 83, 79, 76, 75, 72, 71, 67]):
        add(buf, 0.3 + k * d / 9, sino(mtof(n), 2.0), 0.45)
    return buf[:len(t)]


# ------------------------------------------------------------ efeitos sonoros
def sfx(nome, dur):
    if nome == "alarme":
        t = tt(1.1)
        f = np.where((t * 16).astype(int) % 2 == 0, 1050, 1320)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25
        return filtro(x, "lowpass", 5000) * np.minimum(1, (1.1 - t) * 20)
    if nome in ("rabisco", "rabisco_lento"):
        d = max(dur, 0.3)
        t = tt(d)
        rate = 9 if nome == "rabisco" else 4
        mod = np.abs(np.sin(np.pi * rate * t + 2 * np.sin(t * 3))) ** 0.7
        x = filtro(rng.randn(len(t)), "bandpass", [2500, 7000]) * mod
        return x * 0.22 * np.minimum(1, t * 20) * np.minimum(1, (d - t) * 20)
    if nome == "plim":
        x = sino(2093, 1.2) + sino(3136, 1.2) * 0.6
        out = np.zeros(int(1.3 * SR))
        add(out, 0, x)
        add(out, 0.07, sino(4186, 0.8), 0.4)
        return out * 1.1
    if nome == "brilho":
        out = np.zeros(int(1.6 * SR))
        for k, n in enumerate([84, 88, 91, 96, 100]):
            add(out, k * 0.07, sino(mtof(n), 1.0), 0.5)
        return out
    if nome == "passos":
        out = np.zeros(int(1.0 * SR))
        for k in range(4):
            t = tt(0.12)
            add(out, k * 0.2, filtro(rng.randn(len(t)), "lowpass", 400) * np.exp(-t * 40) * 0.6)
        return out
    if nome == "porta":
        t = tt(0.7)
        f = 300 + 120 * np.sin(t * 23) + 80 * t
        x = (2 * ((np.cumsum(f) / SR) % 1) - 1) * np.abs(np.sin(t * 40)) * 0.18
        return filtro(x, "bandpass", [300, 2500]) * np.minimum(1, (0.7 - t) * 10)
    if nome == "pop":
        t = tt(0.18)
        f = 900 * np.exp(-t * 20) + 200
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.5
    if nome == "boing":
        t = tt(0.7)
        f = 220 + 160 * np.sin(t * 50) * np.exp(-t * 4) + 120 * t
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.45
    if nome == "corrida":
        out = np.zeros(int(1.2 * SR))
        for k in range(12):
            t = tt(0.04)
            add(out, k * 0.085, filtro(rng.randn(len(t)), "bandpass", [600, 2500]) * np.exp(-t * 80) * 0.4)
        t = tt(1.0)
        add(out, 0.2, filtro(rng.randn(len(t)), "bandpass", [400, 3000]) * np.sin(np.pi * t) * 0.12)
        return out
    if nome == "plink":
        return pluck(mtof(88), 0.5, 1.0) * 1.3
    if nome == "crack":
        t = tt(0.4)
        x = filtro(rng.randn(len(t)), "highpass", 800) * np.exp(-t * 25) * 0.8
        x += np.sin(2 * np.pi * 90 * t) * np.exp(-t * 20) * 0.6
        return x
    if nome == "whoosh":
        t = tt(1.4)
        x = rng.randn(len(t))
        lo = filtro(x, "bandpass", [300, 2000])
        hi = filtro(x, "bandpass", [2000, 8000])
        env = np.sin(np.pi * t / 1.4) ** 2
        return (lo * (1 - t / 1.4) + hi * t / 1.4) * env * 0.35
    if nome == "misterio":
        t = tt(3.0)
        return (np.sin(2 * np.pi * 36 * t) * 0.7 + filtro(rng.randn(len(t)), "lowpass", 200) * 0.3) * np.exp(-t * 1.2) * 0.6
    if nome == "tique":
        d = max(dur, 1.0)
        out = np.zeros(int(d * SR))
        k = 0
        while k * 0.5 < d:
            t = tt(0.03)
            f = 2500 if k % 2 == 0 else 1800
            add(out, k * 0.5, np.sin(2 * np.pi * f * t) * np.exp(-t * 200) * 0.5)
            k += 1
        return out
    if nome == "zumbido":
        d = max(dur, 1.0)
        t = tt(d)
        f = 80 + 140 * t / d
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + filtro(rng.randn(len(t)), "bandpass", [1000, 4000]) * 0.05
        return x * (t / d) * np.minimum(1, (d - t) * 5)
    raise ValueError(nome)


# ------------------------------------------------------------ mixagem
def le_wav(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768


def cena(nome):
    for c in TL["cenas"]:
        if c["nome"] == nome:
            return c


def main():
    carrega_timeline()
    voz = np.zeros(N)
    for f in TL["falas"]:
        a = le_wav(f["arquivo"])
        a = a / (np.max(np.abs(a)) + 1e-9) * 0.8
        add(voz, f["ini"], a)

    efeitos = np.zeros(N)
    for s in TL["sfx"]:
        dur = s["dur"]
        if s["nome"] == "tique":
            c = cena("relogio")
            dur = c["ini"] + c["ev"]["crack"][0] - s["t"]
        if s["nome"] == "zumbido":
            c = cena("luz")
            dur = c["fim"] - s["t"]
        add(efeitos, s["t"], sfx(s["nome"], dur))
    # plins calculados pela posição da faixa de luz
    c = cena("borracha")
    t0 = c["ini"] + c["ev"]["n3"][0] + 2.0
    t1 = c["ini"] + c["ev"]["n4"][1]
    add(efeitos, t0 + (800 + 300) / (1080 + 600) * (t1 - t0), sfx("plim", 0))
    c = cena("luz")
    t0, t1 = c["ini"], c["ini"] + c["ev"]["fim"][1] + 4.0
    for x in (180, 430, 560):
        tc = t0 + (x + 400) / 1900 * (t1 - t0)
        if tc < c["fim"]:
            add(efeitos, tc, sfx("plim", 0), 0.8)
    # "HA HA HA"
    c = cena("cueca")
    for k in range(3):
        add(efeitos, c["ini"] + c["ev"]["risada"][0] + k * 0.15, sfx("pop", 0), 0.6)

    musica = np.zeros(N)

    def faixa(ini_nome, fim_nome, gerador, fade=0.4):
        a = cena(ini_nome)["ini"]
        b = cena(fim_nome)["fim"]
        x = gerador(b - a + fade)
        env = np.ones(len(x))
        nf = int(fade * SR)
        env[:nf] = np.linspace(0, 1, nf)
        env[-nf:] = np.linspace(1, 0, nf)
        add(musica, a, x * env)

    faixa("titulo", "explica", lambda d: tema(d))
    faixa("vo", "vo", lambda d: tema(d, 96, suave=True, melodia=False))
    faixa("noite", "nanquim", lambda d: tema(d, 120))
    faixa("relogio", "vo_salva", tensao)
    faixa("telhado", "telhado", emocional)
    faixa("sobreviveu", "final", lambda d: tema(d, 116))
    faixa("mao", "mao", misterio)

    # ducking: música abaixa quando alguém fala
    env_voz = np.abs(voz)
    jan = int(0.15 * SR)
    env_voz = np.convolve(env_voz, np.ones(jan) / jan, mode="same")
    duck = 1 - 0.55 * np.clip(env_voz / 0.05, 0, 1)
    mix = voz * 1.0 + efeitos * 0.8 + musica * 0.42 * duck
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.95
    out = os.path.join(BUILD, "audio.wav")
    with wave.open(out, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("ok", out)


if __name__ == "__main__":
    main()
