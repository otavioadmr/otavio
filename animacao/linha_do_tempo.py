"""Gera as vozes (Piper) e monta a linha do tempo do vídeo -> build/timeline.json"""
import hashlib, json, os, subprocess, wave
import numpy as np
from roteiro import CENAS

AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
VOZES_DIR = os.environ.get("VOZES_DIR", os.path.join(AQUI, "vozes"))
SR = 44100
GAP = 0.22  # respiro depois de cada fala

# voz base, velocidade (length_scale do piper), filtro ffmpeg de personagem
VOZES = {
    "narrador": ("faber", 1.05, "volume=1.0"),
    "teo":      ("cadu", 0.95, "rubberband=pitch=1.32:tempo=1.04"),
    "vo":       ("jeff", 1.05, "rubberband=pitch=1.26:tempo=0.97,vibrato=f=5.5:d=0.18"),
    "nanquim":  ("jeff", 1.0, "rubberband=pitch=0.84:tempo=0.97,aecho=0.8:0.6:30:0.15"),
    "careca":   ("faber", 0.95, "rubberband=pitch=1.12:tempo=1.05"),
    "rabisco":  ("cadu", 1.2, "rubberband=pitch=1.75"),
}


def gera_voz(quem, texto):
    base, ls, filtro = VOZES[quem]
    h = hashlib.md5(f"{quem}|{texto}|{VOZES[quem]}".encode()).hexdigest()[:12]
    out = os.path.join(BUILD, "vozes", f"{quem}_{h}.wav")
    if os.path.exists(out):
        return out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cru = out + ".raw.wav"
    modelo = os.path.join(VOZES_DIR, f"pt_BR-{base}-medium.onnx")
    subprocess.run(["python3", "-m", "piper", "-m", modelo, "--length-scale", str(ls), "-f", cru],
                   input=texto.encode(), check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", cru, "-af",
                    f"{filtro},silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    f"silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                    "-ar", str(SR), "-ac", "1", out], check=True)
    os.remove(cru)
    return out


def le_wav(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a


def envelope(a, fps=24):
    hop = SR // fps
    n = len(a) // hop + 1
    env = [float(np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2) + 1e-9)) for i in range(n)]
    m = max(env) or 1
    return [round(e / m, 3) for e in env]


def monta():
    t = 0.0
    cenas, falas, sfx = [], [], []
    for nome, eventos in CENAS:
        ini = t
        evs = {}
        for ev in eventos:
            if ev[0] == "fala":
                _, quem, texto, eid = ev
                path = gera_voz(quem, texto)
                a = le_wav(path)
                dur = len(a) / SR
                evs[eid] = [round(t - ini, 3), round(t - ini + dur, 3)]
                falas.append({"quem": quem, "texto": texto, "arquivo": path, "ini": round(t, 3),
                              "fim": round(t + dur, 3), "env": envelope(a), "cena": nome})
                t += dur + GAP
            elif ev[0] == "pausa":
                _, dur, eid, s = ev
                evs[eid] = [round(t - ini, 3), round(t - ini + dur, 3)]
                if s:
                    sfx.append({"nome": s, "t": round(t, 3), "dur": dur})
                t += dur
            elif ev[0] == "sfx":
                sfx.append({"nome": ev[1], "t": round(t, 3), "dur": 0})
        cenas.append({"nome": nome, "ini": round(ini, 3), "fim": round(t, 3), "ev": evs})
    tl = {"duracao": round(t, 3), "cenas": cenas, "falas": falas, "sfx": sfx}
    os.makedirs(BUILD, exist_ok=True)
    with open(os.path.join(BUILD, "timeline.json"), "w") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    return tl


if __name__ == "__main__":
    tl = monta()
    for c in tl["cenas"]:
        print(f'{c["nome"]:12s} {c["ini"]:6.2f} -> {c["fim"]:6.2f}')
    print("duração total:", tl["duracao"])
