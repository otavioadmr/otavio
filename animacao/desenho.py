"""Ferramentas de desenho no estilo "rabisco" (traço tremido) + personagens."""
import math
import cairo
import numpy as np

W, H = 1080, 1920
_NZ = np.random.RandomState(7).uniform(-1, 1, 1 << 16)


class Estado:
    frame = 0
    ink = (0.10, 0.09, 0.12)
    boil = 1.0  # intensidade do tremido


S = Estado()

# paleta
PAPEL = (0.97, 0.94, 0.88)
AZUL_PIJ = (0.50, 0.70, 0.92)
AZUL_PIJ2 = (0.33, 0.52, 0.80)
PELE = (1.0, 0.86, 0.72)
ROSA = (1.0, 0.55, 0.6)
ROXO = (0.62, 0.48, 0.80)
CINZA = (0.80, 0.80, 0.82)
AMARELO = (1.0, 0.82, 0.25)
OURO = (1.0, 0.78, 0.30)
VERMELHO = (0.92, 0.28, 0.25)
VERDE = (0.45, 0.75, 0.45)
MARROM = (0.55, 0.36, 0.22)
BRANCO = (1, 1, 1)
NOITE = (0.12, 0.15, 0.30)


def nz(a, b, c=0):
    i = (int(a) * 73856093 ^ int(b) * 19349663 ^ int(c) * 83492791) & 0xFFFF
    return _NZ[i]


def _sid(pts):
    return int(abs(pts[0][0] * 7.3 + pts[0][1] * 3.1 + len(pts) * 11)) % 100000


def _densifica(pts, passo=22, closed=False):
    if closed:
        pts = list(pts) + [pts[0]]
    out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(d / passo))
        for k in range(n):
            f = k / n
            out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    out.append(pts[-1])
    return out


def _treme(pts, amp, sid):
    bf = S.frame // 3
    a = amp * S.boil
    return [(x + nz(sid, i, bf) * a, y + nz(sid + 999, i, bf) * a) for i, (x, y) in enumerate(pts)]


def _corta(pts, prog):
    if prog >= 1:
        return pts
    if prog <= 0:
        return []
    L = [0.0]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
    alvo = L[-1] * prog
    out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= alvo:
            out.append(pts[i])
        else:
            seg = L[i] - L[i - 1]
            f = (alvo - L[i - 1]) / seg if seg else 0
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
            break
    return out


def _caminho(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)


def linha(ctx, pts, w=7, cor=None, closed=False, prog=1.0, amp=2.2, sid=None, alpha=1.0):
    if len(pts) < 2:
        return
    sid = _sid(pts) if sid is None else sid
    d = _densifica(pts, closed=closed)
    d = _treme(d, amp, sid)
    d = _corta(d, prog)
    if len(d) < 2:
        return
    c = cor or S.ink
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    _caminho(ctx, d)
    ctx.stroke()


def forma(ctx, pts, fill=None, w=7, cor=None, prog=1.0, amp=2.2, alpha=1.0, contorno=True):
    """Polígono fechado: preenchimento levemente deslocado + contorno tremido."""
    sid = _sid(pts)
    if fill is not None and prog >= 1:
        d = _treme(_densifica(pts, 40, closed=True), amp * 0.6, sid + 5)
        ctx.set_source_rgba(*fill[:3], alpha)
        _caminho(ctx, [(x + 5, y + 4) for x, y in d])
        ctx.close_path()
        ctx.fill()
    if contorno:
        linha(ctx, pts, w, cor, closed=True, prog=prog, amp=amp, sid=sid, alpha=alpha)


def pontos_elipse(cx, cy, rx, ry, n=28, a0=0.0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * k / n), cy + ry * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def elipse(ctx, cx, cy, rx, ry, fill=None, w=7, cor=None, prog=1.0, alpha=1.0, contorno=True):
    pts = pontos_elipse(cx, cy, rx, ry)[:-1]
    forma(ctx, pts, fill, w, cor, prog, alpha=alpha, contorno=contorno)


def ret(ctx, x, y, w_, h_, fill=None, w=7, cor=None, prog=1.0, alpha=1.0):
    forma(ctx, [(x, y), (x + w_, y), (x + w_, y + h_), (x, y + h_)], fill, w, cor, prog, alpha=alpha)


def disco(ctx, cx, cy, r, cor, alpha=1.0):
    ctx.set_source_rgba(*cor[:3], alpha)
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.fill()


# ---------------------------------------------------------------- texto
def texto(ctx, s, x, y, tam=80, fonte="Luckiest Guy", fill=BRANCO, stroke=None, sw=14, align="c",
          alpha=1.0, rot=0.0):
    if not s:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.select_font_face(fonte)
    ctx.set_font_size(tam)
    ext = ctx.text_extents(s)
    dx = {"c": -ext.width / 2 - ext.x_bearing, "l": 0, "r": -ext.width}[align]
    ctx.move_to(dx, 0)
    ctx.text_path(s)
    if stroke is not None:
        ctx.set_source_rgba(*stroke[:3], alpha)
        ctx.set_line_width(sw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    ctx.set_source_rgba(*fill[:3], alpha)
    ctx.fill()
    ctx.restore()


def quebra(ctx, s, larg, tam, fonte):
    ctx.select_font_face(fonte)
    ctx.set_font_size(tam)
    linhas, atual = [], ""
    for p in s.split():
        teste = (atual + " " + p).strip()
        if ctx.text_extents(teste).x_advance > larg and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = teste
    if atual:
        linhas.append(atual)
    return linhas


# ---------------------------------------------------------------- fundo
def papel(ctx, noite=0.0):
    ctx.set_source_rgb(*PAPEL)
    ctx.paint()
    # linhas de caderno
    ctx.set_line_width(2)
    ctx.set_source_rgba(0.55, 0.7, 0.9, 0.35)
    for y in range(140, H, 72):
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    ctx.stroke()
    ctx.set_source_rgba(0.95, 0.4, 0.4, 0.35)
    ctx.move_to(110, 0)
    ctx.line_to(110, H)
    ctx.stroke()
    if noite > 0:
        ctx.set_source_rgba(*NOITE, 0.88 * noite)
        ctx.paint()


def estrelas(ctx, n=40, alpha=1.0, seed=3):
    for i in range(n):
        x = (nz(seed, i) * 0.5 + 0.5) * W
        y = (nz(seed + 1, i) * 0.5 + 0.5) * 800
        br = 0.6 + 0.4 * math.sin(S.frame * 0.15 + i)
        disco(ctx, x, y, 4 + 2 * (i % 3), (1, 0.97, 0.8), alpha * br)


def lua(ctx, x, y, r=70):
    elipse(ctx, x, y, r, r, fill=(1, 0.96, 0.75), cor=(1, 0.96, 0.8), w=5)
    elipse(ctx, x + 30, y - 10, r * 0.85, r * 0.85, fill=NOITE, contorno=False)


def sol(ctx, x, y, r=90, raio_rot=0):
    for k in range(10):
        a = raio_rot + k * math.pi / 5
        linha(ctx, [(x + math.cos(a) * (r + 25), y + math.sin(a) * (r + 25)),
                    (x + math.cos(a) * (r + 70), y + math.sin(a) * (r + 70))], 9, (1, 0.7, 0.1))
    elipse(ctx, x, y, r, r, fill=AMARELO, cor=(0.95, 0.6, 0.1), w=8)


def chao(ctx, y=1300, cor=None):
    linha(ctx, [(-50, y), (W + 50, y)], 8, cor)


def nuvem(ctx, x, y, s=1.0, alpha=1.0):
    pts = []
    for k, (dx, dy, r) in enumerate([(-90, 10, 55), (-35, -30, 70), (40, -25, 65), (95, 10, 50)]):
        pass
    for dx, dy, r in [(-90, 10, 55), (-35, -30, 70), (40, -25, 65), (95, 10, 50), (0, 25, 80)]:
        elipse(ctx, x + dx * s, y + dy * s, r * s, r * s * 0.8, fill=BRANCO, contorno=False, alpha=alpha)
    linha(ctx, pontos_elipse(x - 35 * s, y - 30 * s, 70 * s, 56 * s, 14, math.pi * 0.9, math.pi * 2.0),
          6, alpha=alpha * 0.8)


# ---------------------------------------------------------------- objetos
def casa(ctx, x, y, w=260, h=220, telhado=VERMELHO, parede=(1, 0.95, 0.8), prog=1.0, alpha=1.0,
         porta=True, janela=True):
    """x,y = canto inferior esquerdo."""
    ret(ctx, x, y - h, w, h, fill=parede, prog=prog, alpha=alpha)
    forma(ctx, [(x - 25, y - h), (x + w / 2, y - h - w * 0.55), (x + w + 25, y - h)], fill=telhado,
          prog=prog, alpha=alpha)
    if porta:
        ret(ctx, x + w * 0.38, y - h * 0.55, w * 0.24, h * 0.55, fill=MARROM, prog=prog, alpha=alpha)
    if janela:
        ret(ctx, x + w * 0.08, y - h * 0.75, w * 0.22, w * 0.22, fill=(0.7, 0.88, 1), prog=prog, alpha=alpha)
        ret(ctx, x + w * 0.70, y - h * 0.75, w * 0.22, w * 0.22, fill=(0.7, 0.88, 1), prog=prog, alpha=alpha)


def arvore(ctx, x, y, s=1.0, prog=1.0, alpha=1.0):
    ret(ctx, x - 15 * s, y - 120 * s, 30 * s, 120 * s, fill=MARROM, prog=prog, alpha=alpha)
    elipse(ctx, x, y - 170 * s, 85 * s, 75 * s, fill=VERDE, prog=prog, alpha=alpha)


def poste(ctx, x, y, alpha=1.0):
    linha(ctx, [(x, y), (x, y - 330)], 9, alpha=alpha)
    linha(ctx, [(x, y - 330), (x + 60, y - 330)], 9, alpha=alpha)
    elipse(ctx, x + 60, y - 312, 22, 16, fill=AMARELO, alpha=alpha)


def banco(ctx, x, y, alpha=1.0):
    ret(ctx, x, y - 70, 180, 22, fill=MARROM, alpha=alpha)
    linha(ctx, [(x + 20, y - 48), (x + 20, y)], 8, alpha=alpha)
    linha(ctx, [(x + 160, y - 48), (x + 160, y)], 8, alpha=alpha)
    ret(ctx, x, y - 130, 180, 20, fill=MARROM, alpha=alpha)


def pombo(ctx, x, y, alpha=1.0):
    elipse(ctx, x, y - 30, 38, 26, fill=CINZA, alpha=alpha)
    elipse(ctx, x + 35, y - 60, 18, 18, fill=CINZA, alpha=alpha)
    forma(ctx, [(x + 50, y - 62), (x + 66, y - 57), (x + 50, y - 52)], fill=AMARELO, w=4, alpha=alpha)
    disco(ctx, x + 40, y - 64, 4, S.ink, alpha)
    linha(ctx, [(x - 5, y - 6), (x - 5, y + 8)], 5, alpha=alpha)
    linha(ctx, [(x + 10, y - 6), (x + 10, y + 8)], 5, alpha=alpha)


def cama(ctx, x, y, w=440, cobertor=AZUL_PIJ):
    """x,y = centro da base."""
    linha(ctx, [(x - w / 2, y), (x - w / 2, y - 200)], 10)
    linha(ctx, [(x + w / 2, y), (x + w / 2, y - 120)], 10)
    ret(ctx, x - w / 2, y - 110, w, 60, fill=(1, 1, 1))
    elipse(ctx, x - w / 2 + 75, y - 125, 60, 30, fill=BRANCO)


def lapis(ctx, x, y, ang=0.0, comp=170, grossura=24, toco=False, etiqueta=None):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    c = 50 if toco else comp
    g = grossura
    forma(ctx, [(0, -g / 2), (c, -g / 2), (c, g / 2), (0, g / 2)], fill=AMARELO, w=5)
    forma(ctx, [(c, -g / 2), (c + 22, -g / 2), (c + 22, g / 2), (c, g / 2)], fill=ROSA, w=5)
    forma(ctx, [(0, -g / 2), (-34, 0), (0, g / 2)], fill=(1, 0.88, 0.7), w=5)
    forma(ctx, [(-22, -5), (-34, 0), (-22, 5)], fill=S.ink, w=3)
    if etiqueta:
        ctx.restore()
        ctx.save()
        ctx.translate(x, y)
        ret(ctx, 40, 30, 120, 60, fill=BRANCO, w=4)
        texto(ctx, etiqueta, 100, 78, 46, "Patrick Hand", fill=S.ink)
    ctx.restore()


def relogio_torre(ctx, x, y, hora, minuto, s=1.0, cor=(0.85, 0.78, 0.65)):
    """x,y = base."""
    ret(ctx, x - 90 * s, y - 520 * s, 180 * s, 520 * s, fill=cor)
    forma(ctx, [(x - 115 * s, y - 520 * s), (x, y - 700 * s), (x + 115 * s, y - 520 * s)], fill=VERMELHO)
    cx, cy, r = x, y - 410 * s, 72 * s
    elipse(ctx, cx, cy, r, r, fill=BRANCO)
    am = (minuto / 60) * 2 * math.pi - math.pi / 2
    ah = ((hora % 12 + minuto / 60) / 12) * 2 * math.pi - math.pi / 2
    linha(ctx, [(cx, cy), (cx + math.cos(ah) * r * 0.5, cy + math.sin(ah) * r * 0.5)], 9)
    linha(ctx, [(cx, cy), (cx + math.cos(am) * r * 0.8, cy + math.sin(am) * r * 0.8)], 6, VERMELHO)


def brilhos(ctx, x, y, t, n=8, raio=120, cor=OURO):
    """explosão de estrelinhas (t de 0 a 1)."""
    if t <= 0 or t >= 1:
        return
    for i in range(n):
        a = i * 2 * math.pi / n + 0.3
        d = raio * (0.3 + t)
        px, py = x + math.cos(a) * d, y + math.sin(a) * d
        r = 22 * (1 - t)
        estrela(ctx, px, py, r, cor, 1 - t)


def estrela(ctx, x, y, r, cor=OURO, alpha=1.0):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.35
        a = k * math.pi / 4 - math.pi / 2
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    ctx.set_source_rgba(*cor[:3], alpha)
    _caminho(ctx, pts)
    ctx.close_path()
    ctx.fill()


def balao(ctx, x, y, s, tam=70, cor=BRANCO):
    ctx.save()
    ctx.select_font_face("Patrick Hand")
    ctx.set_font_size(tam)
    e = ctx.text_extents(s)
    ctx.restore()
    w, h = e.x_advance + 60, tam + 40
    forma(ctx, [(x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y), (x + 20, y), (x - 10, y + 35),
                (x - 15, y), (x - w / 2, y)], fill=cor, w=6)
    texto(ctx, s, x, y - 25, tam, "Patrick Hand", fill=(0.10, 0.09, 0.12))


def luz_borracha(ctx, x, alpha=1.0, largura=260):
    """faixa de luz vertical (a 'borracha' do sol) centrada em x."""
    g = cairo.LinearGradient(x - largura, 0, x + largura, 0)
    g.add_color_stop_rgba(0, 1, 0.85, 0.4, 0)
    g.add_color_stop_rgba(0.45, 1, 0.92, 0.6, 0.85 * alpha)
    g.add_color_stop_rgba(0.5, 1, 1, 0.95, 1.0 * alpha)
    g.add_color_stop_rgba(0.55, 1, 0.92, 0.6, 0.85 * alpha)
    g.add_color_stop_rgba(1, 1, 0.85, 0.4, 0)
    ctx.set_source(g)
    ctx.rectangle(x - largura, -200, largura * 2, H + 400)
    ctx.fill()


# ---------------------------------------------------------------- personagens
def _olhos(ctx, x, y, esp, humor, pisca, olhar=(0, 0), r=20):
    for sx in (-1, 1):
        ex = x + sx * esp
        if humor == "feliz":
            linha(ctx, pontos_elipse(ex, y + 8, r * 0.9, r * 0.9, 10, math.pi * 1.1, math.pi * 1.9), 7)
        elif pisca or humor == "dorme":
            linha(ctx, [(ex - r, y), (ex + r, y)], 7)
        elif humor == "susto":
            elipse(ctx, ex, y, r * 1.35, r * 1.5, fill=BRANCO, w=6)
            disco(ctx, ex + olhar[0], y + olhar[1], r * 0.35, S.ink)
        else:
            elipse(ctx, ex, y, r, r * 1.2, fill=BRANCO, w=6)
            disco(ctx, ex + olhar[0] * 0.6, y + 4 + olhar[1] * 0.6, r * 0.5, S.ink)
        if humor == "triste":
            linha(ctx, [(ex - sx * r, y - r * 2.0 + 0), (ex + sx * r, y - r * 1.4)], 6)
        if humor == "bravo":
            linha(ctx, [(ex - sx * r, y - r * 1.4), (ex + sx * r, y - r * 1.9)], 7)


def _boca(ctx, x, y, humor, fala, larg=34):
    if fala > 0.08:
        h = 10 + 38 * min(1, fala)
        elipse(ctx, x, y + h * 0.3, larg * 0.75, h * 0.5 + 4, fill=(0.55, 0.15, 0.2), w=6)
        return
    if humor in ("feliz", "normal"):
        linha(ctx, pontos_elipse(x, y - 12, larg, 22, 10, math.pi * 0.15, math.pi * 0.85), 7)
    elif humor == "triste":
        linha(ctx, pontos_elipse(x, y + 18, larg * 0.8, 16, 10, math.pi * 1.15, math.pi * 1.85), 7)
    elif humor == "susto":
        elipse(ctx, x, y + 6, 16, 22, fill=(0.55, 0.15, 0.2), w=6)
    elif humor == "sem_graca":
        linha(ctx, [(x - larg, y), (x - larg / 3, y + 6), (x + larg / 3, y - 4), (x + larg, y + 4)], 7)
    else:
        linha(ctx, [(x - larg * 0.7, y), (x + larg * 0.7, y)], 7)


def _pisca(t, seed=0):
    ciclo = 3.3 + seed * 0.7
    return (t + seed) % ciclo < 0.13


def _braco(ctx, sx, sy, ang, comp, cor_manga, w=26):
    """ang: 0 = caído, positivo = abre para fora, pi = pra cima."""
    lado = 1 if sx > 0 else -1
    ex, ey = sx + lado * math.sin(ang) * comp, sy + math.cos(ang) * comp
    linha(ctx, [(sx, sy), (ex, ey)], w + 10)
    linha(ctx, [(sx, sy), (ex, ey)], w, cor_manga, amp=1.2)
    elipse(ctx, ex, ey, 17, 17, fill=PELE, w=5)
    return ex, ey


def teo(ctx, x, y, s=1.0, humor="normal", fala=0.0, t=0.0, braco_e=0.3, braco_d=0.3,
        lapis_mao=False, olhar=(0, 0), pulo=0.0, deitado=False, sem_pernas=False, pe_lapis=False,
        lapis_quebrado=False):
    ctx.save()
    ctx.translate(x, y - pulo)
    ctx.scale(s, s)
    if deitado:
        ctx.rotate(-math.pi / 2)
    # pernas
    if not sem_pernas:
        for sx in (-1, 1):
            linha(ctx, [(sx * 35, -150), (sx * 40, -20)], 30)
            linha(ctx, [(sx * 35, -150), (sx * 40, -20)], 20, AZUL_PIJ2, amp=1)
            elipse(ctx, sx * 48, -12, 34, 16, fill=PELE, w=6)
        if pe_lapis:
            lapis(ctx, 95, -30, -0.35, 170, 30)
    # corpo
    forma(ctx, [(-80, -310), (80, -310), (95, -140), (-95, -140)], fill=AZUL_PIJ)
    for k in range(3):
        yy = -275 + k * 45
        linha(ctx, [(-78 - k * 4, yy), (78 + k * 4, yy)], 5, AZUL_PIJ2, amp=1.5)
    # braços
    hd = _braco(ctx, 75, -290, braco_d, 130, AZUL_PIJ)
    _braco(ctx, -75, -290, braco_e, 130, AZUL_PIJ)
    if lapis_mao:
        lapis(ctx, hd[0], hd[1], -0.9, 150, 22, toco=lapis_quebrado)
    # cabeça
    hx, hy = 0, -405
    elipse(ctx, hx, hy, 100, 95, fill=PELE)
    # cabelo espetado
    pts = [(-100, hy - 10)]
    for k in range(9):
        px = -100 + k * 25
        pts.append((px + 12, hy - 125 - (18 if k % 2 == 0 else 0)))
        pts.append((px + 25, hy - 75))
    pts.append((100, hy - 20))
    pts.append((90, hy - 70))
    pts.append((-90, hy - 70))
    forma(ctx, pts, fill=(0.35, 0.22, 0.14))
    # bochechas
    disco(ctx, hx - 62, hy + 30, 17, ROSA, 0.6)
    disco(ctx, hx + 62, hy + 30, 17, ROSA, 0.6)
    _olhos(ctx, hx, hy - 5, 36, humor, _pisca(t), olhar)
    _boca(ctx, hx, hy + 48, humor, fala)
    ctx.restore()


def vo(ctx, x, y, s=1.0, humor="normal", fala=0.0, t=0.0, braco_e=0.25, braco_d=0.25, toco_mao=False,
       lapis_mao=False, lapis_orelha=True, pulo=0.0):
    ctx.save()
    ctx.translate(x, y - pulo)
    ctx.scale(s, s)
    for sx in (-1, 1):
        linha(ctx, [(sx * 30, -100), (sx * 32, -15)], 10)
        elipse(ctx, sx * 40, -10, 30, 14, fill=(0.5, 0.3, 0.6), w=6)
    # vestido + xale
    forma(ctx, [(-70, -300), (70, -300), (120, -95), (-120, -95)], fill=(0.95, 0.8, 0.55))
    forma(ctx, [(-85, -300), (85, -300), (100, -200), (0, -170), (-100, -200)], fill=ROXO)
    hd = _braco(ctx, 70, -285, braco_d, 120, ROXO)
    he = _braco(ctx, -70, -285, braco_e, 120, ROXO)
    if toco_mao:
        lapis(ctx, hd[0] - 10, hd[1] - 5, -1.2, 0, 20, toco=True)
    if lapis_mao:
        if braco_e > braco_d:
            lapis(ctx, he[0], he[1], math.pi + 0.5, 150, 22)
        else:
            lapis(ctx, hd[0], hd[1], -0.9, 150, 22)
    hx, hy = 0, -380
    elipse(ctx, hx, hy - 95, 50, 42, fill=CINZA)  # coque
    elipse(ctx, hx, hy, 92, 88, fill=PELE)
    forma(ctx, [(-92, hy - 5), (-80, hy - 65), (0, hy - 92), (80, hy - 65), (92, hy - 5), (60, hy - 50),
                (-60, hy - 50)], fill=CINZA)
    if lapis_orelha:
        lapis(ctx, 70, hy - 50, -0.4, 0, 16, toco=True)
    disco(ctx, hx - 58, hy + 32, 15, ROSA, 0.55)
    disco(ctx, hx + 58, hy + 32, 15, ROSA, 0.55)
    _olhos(ctx, hx, hy, 34, humor, _pisca(t, 1), r=15)
    for sx in (-1, 1):
        elipse(ctx, hx + sx * 34, hy + 2, 30, 28, w=5)
    linha(ctx, [(hx - 4, hy), (hx + 4, hy)], 5)
    _boca(ctx, hx, hy + 50, humor, fala, 28)
    ctx.restore()


def nanquim(ctx, x, y, s=1.0, humor="normal", fala=0.0, t=0.0, cueca=False, braco_e=0.2,
            braco_d=0.2, rindo=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sx in (-1, 1):
        linha(ctx, [(sx * 28, -230), (sx * 30, -15)], 22 if cueca else 34)
        if cueca:
            linha(ctx, [(sx * 28, -230), (sx * 30, -15)], 13, PELE, amp=1)
        elipse(ctx, sx * 45, -10, 40, 15, fill=S.ink, w=5)
    if cueca:
        forma(ctx, [(-70, -280), (70, -280), (75, -195), (5, -190), (-75, -195)], fill=BRANCO)
        for k, (cx, cy) in enumerate([(-40, -250), (20, -235), (45, -215), (-20, -210)]):
            coracao(ctx, cx, cy, 13, VERMELHO)
    forma(ctx, [(-70, -470), (70, -470), (75, -270), (-75, -270)], fill=(0.2, 0.2, 0.25) if not cueca else BRANCO)
    forma(ctx, [(-12, -470), (12, -470), (0, -330)], fill=VERMELHO, w=5)
    _braco(ctx, 68, -455, braco_d, 170, (0.2, 0.2, 0.25) if not cueca else BRANCO, 22)
    _braco(ctx, -68, -455, braco_e, 170, (0.2, 0.2, 0.25) if not cueca else BRANCO, 22)
    hx, hy = 0, -560
    elipse(ctx, hx, hy, 70, 85, fill=PELE)
    ret(ctx, -70, hy - 165, 140, 95, fill=(0.15, 0.15, 0.18))
    ret(ctx, -100, hy - 80, 200, 18, fill=(0.15, 0.15, 0.18))
    _olhos(ctx, hx, hy - 10, 28, humor, _pisca(t, 2), r=13)
    elipse(ctx, hx + 28, hy - 10, 24, 24, w=5)  # monóculo
    linha(ctx, [(hx + 50, hy), (hx + 60, hy + 70)], 3)
    # bigode enrolado
    for sx in (-1, 1):
        linha(ctx, [(hx, hy + 36), (hx + sx * 35, hy + 32), (hx + sx * 58, hy + 18), (hx + sx * 56, hy + 6),
                    (hx + sx * 46, hy + 12)], 10)
    _boca(ctx, hx, hy + 58, humor, max(fala, rindo), 24)
    ctx.restore()


def coracao(ctx, x, y, r, cor, alpha=1.0):
    pts = []
    for k in range(30):
        a = k / 30 * 2 * math.pi
        px = 16 * math.sin(a) ** 3
        py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + px * r / 16, y + py * r / 16))
    ctx.set_source_rgba(*cor[:3], alpha)
    _caminho(ctx, pts)
    ctx.close_path()
    ctx.fill()


def rabisco(ctx, x, y, s=1.0, t=0.0, andando=False, prog=1.0, olhar=1, pulo=0.0):
    """cachorro de palitinho com 3 patas. x,y = chão sob o corpo."""
    ctx.save()
    ctx.translate(x, y - pulo)
    ctx.scale(s * olhar, s)
    sw = math.sin(t * 14) * 0.35 if andando else 0
    by = -90
    linha(ctx, [(-70, by), (60, by - 5)], 9, prog=prog)
    for k, lx in enumerate([-55, 5, 50]):
        a = sw * (1 if k % 2 else -1)
        linha(ctx, [(lx, by), (lx + math.sin(a) * 90 + (12 if k == 1 else 0), by + math.cos(a) * 90)], 9, prog=prog)
    rab = math.sin(t * 18) * 25
    linha(ctx, [(-70, by), (-110, by - 40 + rab), (-125, by - 70 + rab)], 8, prog=prog)
    if prog >= 1:
        elipse(ctx, 90, by - 40, 42, 38, fill=BRANCO)
        forma(ctx, [(62, by - 68), (40, by - 50), (38, by - 15), (55, by - 25), (72, by - 55)], fill=S.ink, w=6)
        elipse(ctx, 132, by - 34, 18, 13, fill=BRANCO, w=5)
        disco(ctx, 100, by - 45, 6, S.ink)
        disco(ctx, 148, by - 38, 9, S.ink)
        linha(ctx, [(100, by - 15), (115, by - 18)], 5)
    ctx.restore()


def privada(ctx, x, y, s=1.0, t=0.0, pernas=0.0, correndo=False, prog=1.0, alpha=1.0):
    """x,y = chão."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    lift = pernas * 80
    if pernas > 0:
        for k, sx in enumerate((-1, 1)):
            a = math.sin(t * 22 + k * math.pi) * 0.6 if correndo else 0
            fx, fy = sx * 35 + math.sin(a) * 60, -10 + (1 - pernas) * 80
            linha(ctx, [(sx * 35, -lift), (fx, fy)], 9, alpha=alpha)
            forma(ctx, [(fx - 10, fy - 15), (fx + 40, fy - 15), (fx + 45, fy + 5), (fx - 10, fy + 5)],
                  fill=VERMELHO, w=5, alpha=alpha)
    ctx.translate(0, -lift)
    ret(ctx, 40, -290, 80, 170, fill=BRANCO, prog=prog, alpha=alpha)
    forma(ctx, [(-50, 0), (50, 0), (60, -90), (-60, -90)], fill=BRANCO, prog=prog, alpha=alpha)
    elipse(ctx, 0, -110, 120, 34, fill=BRANCO, prog=prog, alpha=alpha)
    if prog >= 1:
        linha(ctx, [(70, -260), (95, -260)], 6, alpha=alpha)
    ctx.restore()


def careca(ctx, x, y, s=1.0, cabelo=1.0, fala=0.0, t=0.0, humor="normal"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sx in (-1, 1):
        linha(ctx, [(sx * 30, -150), (sx * 30, -10)], 28)
        linha(ctx, [(sx * 30, -150), (sx * 30, -10)], 18, (0.45, 0.45, 0.5), amp=1)
    forma(ctx, [(-90, -330), (90, -330), (100, -140), (-100, -140)], fill=VERDE)
    _braco(ctx, 85, -315, 2.6 if humor == "bravo" else 0.2, 130, VERDE)
    _braco(ctx, -85, -315, 2.6 if humor == "bravo" else 0.2, 130, VERDE)
    hx, hy = 0, -420
    elipse(ctx, hx, hy, 95, 92, fill=PELE)
    if cabelo > 0:
        pts = [(-95, hy - 10), (-110, hy - 100), (-60, hy - 150), (0, hy - 165), (60, hy - 150),
               (110, hy - 100), (95, hy - 10), (70, hy - 70), (-70, hy - 70)]
        forma(ctx, pts, fill=(0.95, 0.65, 0.2), alpha=cabelo)
    else:
        linha(ctx, pontos_elipse(hx + 35, hy - 55, 25, 15, 8, math.pi * 1.1, math.pi * 1.6), 5, BRANCO)
    _olhos(ctx, hx, hy, 32, humor, _pisca(t, 3), r=17)
    elipse(ctx, hx, hy + 30, 22, 18, fill=(1, 0.7, 0.6), w=5)
    _boca(ctx, hx, hy + 60, humor, fala, 28)
    ctx.restore()


def vizinho(ctx, x, y, s=1.0, cor=VERDE, seed=0, t=0.0):
    """silhueta simples de vizinho olhando."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    forma(ctx, [(-60, -260), (60, -260), (75, -10), (-75, -10)], fill=cor)
    elipse(ctx, 0, -330, 70, 70, fill=PELE)
    _olhos(ctx, 0, -335, 25, "susto", _pisca(t, seed), (0, 2), r=12)
    elipse(ctx, 0, -295, 10, 13, fill=(0.55, 0.15, 0.2), w=4)
    ctx.restore()


def mao_gigante(ctx, x, y, s=1.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    # borracha
    forma(ctx, [(-150, 120), (150, 120), (170, 300), (-170, 300)], fill=ROSA, w=10, alpha=alpha)
    forma(ctx, [(-150, 120), (150, 120), (150, 60), (-150, 60)], fill=(0.4, 0.55, 0.85), w=10, alpha=alpha)
    # dedos
    for k, dx in enumerate([-120, -45, 30, 105]):
        forma(ctx, [(dx - 32, 80), (dx + 32, 80), (dx + 32, -120 - (k % 2) * 30), (dx - 32, -120 - (k % 2) * 30)],
              fill=PELE, w=9, alpha=alpha)
    forma(ctx, [(-160, -150), (160, -150), (160, -500), (-160, -500)], fill=PELE, w=9, alpha=alpha)
    forma(ctx, [(160, -60), (230, -150), (200, -200), (150, -150)], fill=PELE, w=9, alpha=alpha)
    ctx.restore()
