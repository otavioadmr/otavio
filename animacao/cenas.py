"""As 19 cenas do episódio. Cada função recebe (ctx, t, ev, G):
t = tempo local da cena, ev = {id: [ini, fim]} dos eventos, G = utilidades globais."""
import math
import desenho as D
from desenho import W, H

CHAO = 1300
GIZ = (0.95, 0.93, 0.86)
TINTA = (0.10, 0.09, 0.12)


# ------------------------------------------------------------ utilidades
def fase(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return max(0.0, min(1.0, (t - a) / (b - a)))


def suave(x):
    return x * x * (3 - 2 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def pop(t, t0, dur=0.35):
    """escala com 'quique' ao aparecer."""
    x = fase(t, t0, t0 + dur)
    if x <= 0:
        return 0.0
    return 1 + math.sin(x * math.pi) * 0.25 * (1 - x) if x < 1 else 1.0


def camera(ctx, zoom=1.0, cx=W / 2, cy=H / 2):
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-cx, -cy)


def treme(ctx, forca, t):
    if forca > 0:
        ctx.translate(math.sin(t * 90) * forca, math.cos(t * 73) * forca)


def noite(ctx, a=1.0):
    D.papel(ctx, a)
    D.S.ink = GIZ if a > 0.5 else TINTA


def amanhecer(ctx, a):
    """brilho laranja no horizonte (a de 0 a 1)."""
    import cairo
    g = cairo.LinearGradient(0, 300, 0, CHAO)
    g.add_color_stop_rgba(0, 0.95, 0.5, 0.6, 0)
    g.add_color_stop_rgba(1, 1, 0.65, 0.3, 0.75 * a)
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, CHAO)
    ctx.fill()


def contorno_tracejado(ctx, pts, alpha=0.5):
    """contorno pontilhado (algo que 'sumiu')."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = int(d / 40)
        for k in range(n):
            f0, f1 = k / n, (k + 0.5) / n
            D.linha(ctx, [(lerp(x0, x1, f0), lerp(y0, y1, f0)), (lerp(x0, x1, f1), lerp(y0, y1, f1))], 5,
                    alpha=alpha)


def casa_sumida(ctx, x=290, w=500, h=420, alpha=0.45):
    contorno_tracejado(ctx, [(x, CHAO), (x, CHAO - h), (x + w / 2, CHAO - h - 250), (x + w, CHAO - h), (x + w, CHAO)],
                       alpha)


def zzz(ctx, x, y, t):
    for k in range(3):
        fz = (t * 0.8 + k / 3) % 1
        D.texto(ctx, "z", x + fz * 60 + k * 10, y - fz * 140, 40 + k * 16, "Luckiest Guy", fill=D.S.ink,
                alpha=1 - fz)


def passou(xobj, t, t0, t1, x0=-300, x1=W + 300):
    """a faixa de luz vai de x0 a x1 entre t0 e t1. Devolve (visível, fase_do_brilho)."""
    tc = t0 + (xobj - x0) / (x1 - x0) * (t1 - t0)
    return t < tc, fase(t, tc, tc + 0.6)


def casa_torta(ctx, x=600, telhado=0.0, alpha=1.0, porta_aberta=0.0, prog=1.0):
    """a casa do Téo: torta, janela no chão, porta que dá numa parede. x = esquerda."""
    pts = [(x, CHAO), (x - 10, CHAO - 330), (x + 330, CHAO - 350), (x + 345, CHAO)]
    D.forma(ctx, pts, fill=(1, 0.93, 0.75), alpha=alpha, prog=prog)
    # porta
    D.ret(ctx, x + 40, CHAO - 210, 110, 210, fill=(0.85, 0.3, 0.25), alpha=alpha, prog=prog)
    # janela no chão
    D.forma(ctx, [(x + 190, CHAO - 5), (x + 300, CHAO - 15), (x + 305, CHAO - 80), (x + 195, CHAO - 70)],
            fill=(0.7, 0.88, 1), alpha=alpha, prog=prog)
    if telhado > 0:
        cx, cy = x + 168, CHAO - 470
        pts = []
        for k in range(41):
            a = k / 40 * 2 * math.pi
            px = 16 * math.sin(a) ** 3
            py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
            pts.append((cx + px * 12.5, cy + py * 11))
        D.forma(ctx, pts, fill=D.VERMELHO if telhado >= 1 else None, prog=telhado, w=9, alpha=alpha)


# ------------------------------------------------------------ cenas
def acordar(ctx, t, ev, G):
    D.papel(ctx)
    ctx.save()
    acorda = ev["acorda"][0]
    z = lerp(1.18, 1.0, suave(fase(t, 0, acorda + 0.3)))
    camera(ctx, z, 540, 1000)
    treme(ctx, 6 * (1 - fase(t, acorda, acorda + 0.5)) if t > acorda else 0, t)
    casa_sumida(ctx)
    D.chao(ctx, CHAO)
    acordou = t >= acorda
    if acordou:
        a = fase(t, acorda + 0.2, acorda + 0.6)
        D.vizinho(ctx, 150, CHAO + 30, 0.85 * a if a > 0 else 0.01, D.VERDE, 1, t)
        D.vizinho(ctx, 935, CHAO + 30, 0.8 * a if a > 0 else 0.01, (0.95, 0.6, 0.4), 2, t)
    D.cama(ctx, 540, CHAO)
    pulo = 40 * math.sin(fase(t, acorda, acorda + 0.35) * math.pi)
    humor = "dorme" if not acordou else "susto"
    olhar = (0, 0)
    if "ue" in ev and t > ev["ue"][0]:
        olhar = (-14, 0) if (t * 1.6) % 2 < 1 else (14, 0)
    D.teo(ctx, 470, CHAO - 20, 0.75, humor=humor, fala=G.fala("teo"), t=t, sem_pernas=True, pulo=pulo,
          olhar=olhar, braco_e=0.9 if acordou else 0.1, braco_d=0.9 if acordou else 0.1)
    D.ret(ctx, 280, CHAO - 125, 455, 80, fill=D.AZUL_PIJ)  # cobertor
    if not acordou:
        zzz(ctx, 560, CHAO - 380, t)
    # despertador
    rx = 840
    sh = math.sin(t * 60) * 8 if acorda <= t < acorda + 1.0 else 0
    D.elipse(ctx, rx + sh, CHAO - 55, 50, 50, fill=D.VERMELHO)
    D.elipse(ctx, rx + sh, CHAO - 55, 36, 36, fill=D.BRANCO, w=5)
    D.linha(ctx, [(rx + sh, CHAO - 55), (rx + sh, CHAO - 80)], 5)
    D.linha(ctx, [(rx + sh, CHAO - 55), (rx + sh + 20, CHAO - 55)], 5)
    if acorda <= t < acorda + 1.0:
        D.texto(ctx, "TRIIIM!", rx - 10, CHAO - 150, 62, fill=D.AMARELO, stroke=TINTA, sw=12, rot=-0.15)
    ctx.restore()
    # gancho no topo
    a = fase(t, 0.0, 0.25)
    D.texto(ctx, "ELE ESQUECEU DE", 540, 330, 82, fill=D.BRANCO, stroke=TINTA, sw=16, alpha=a)
    D.texto(ctx, "DESENHAR A CASA", 540, 430, 92, fill=D.AMARELO, stroke=TINTA, sw=16, alpha=a)
    D.texto(ctx, "6:00", 540, 560, 70, fill=D.VERMELHO, stroke=TINTA, sw=12, alpha=fase(t, acorda, acorda + .2))


def titulo(ctx, t, ev, G):
    D.papel(ctx)
    p = fase(t, 0.1, 1.5)
    l1, l2 = "A CIDADE QUE", "APAGA ÀS 6"
    total = len(l1) + len(l2)
    n = int(p * total)
    s1, s2 = l1[:min(n, len(l1))], l2[:max(0, n - len(l1))]
    D.texto(ctx, s1, 540, 700, 110, fill=D.BRANCO, stroke=TINTA, sw=18, align="c")
    D.texto(ctx, s2, 540, 850, 140, fill=D.AMARELO, stroke=TINTA, sw=20)
    if p < 1:
        ctx.save()
        ctx.select_font_face("Luckiest Guy")
        ctx.set_font_size(140 if n > len(l1) else 110)
        ref = s2 if n > len(l1) else s1
        full = l2 if n > len(l1) else l1
        wfull = ctx.text_extents(full).width
        wref = ctx.text_extents(ref).width if ref else 0
        ctx.restore()
        px = 540 - wfull / 2 + wref
        py = 850 if n > len(l1) else 700
        D.lapis(ctx, px + 30, py - 30, -0.9, 200, 28)
    # cidade sendo rabiscada embaixo
    for k, x in enumerate([130, 420, 700]):
        D.casa(ctx, x, CHAO + 150, 230, 190, telhado=[D.VERMELHO, D.ROXO, D.VERDE][k],
               prog=fase(t, 0.3 + k * 0.3, 1.2 + k * 0.3))
    D.chao(ctx, CHAO + 150)


def cidade(ctx, t, ev, G):
    n1a, n1b = ev["n1"]
    p = fase(t, n1a, n1b)
    if t < n1b and p < 0.52:
        D.papel(ctx)
        ctx.save()
        camera(ctx, lerp(1.0, 1.08, p / 0.52), 540, 1000)
        D.sol(ctx, 880, 380, 70, t * 0.3)
        for k, x in enumerate([60, 360, 680]):
            D.casa(ctx, x, CHAO, 260, 230, telhado=[D.VERMELHO, D.ROXO, D.VERDE][k],
                   prog=fase(p, 0.0 + k * 0.08, 0.2 + k * 0.08))
        for k, x in enumerate([330, 640, 1000]):
            D.arvore(ctx, x, CHAO, 0.8, prog=fase(p, 0.28 + k * 0.05, 0.42 + k * 0.05))
        D.chao(ctx, CHAO)
        # lápis gigante desenhando
        if p < 0.45:
            px = lerp(100, 1000, (p * 6) % 1)
            D.lapis(ctx, px, CHAO - 260 + math.sin(t * 20) * 30, -0.9, 220, 30)
        ctx.restore()
    elif t < n1b and p < 0.72:
        # pão sendo desenhado
        D.papel(ctx)
        q = fase(p, 0.52, 0.66)
        D.elipse(ctx, 540, 900, 300, 150, fill=(0.9, 0.65, 0.35) if q >= 1 else None, prog=q, w=10)
        if q >= 1:
            for k in range(3):
                D.linha(ctx, [(420 + k * 110, 830), (470 + k * 110, 960)], 9)
        D.lapis(ctx, 540 + math.cos(q * 6.3) * 300, 900 + math.sin(q * 6.3) * 150 - 20, -0.9, 220, 30)
        D.texto(ctx, "PÃO", 540, 1200, 90, fill=D.AMARELO, stroke=TINTA, sw=14, alpha=fase(p, 0.6, 0.64))
    elif t < n1b:
        # bigode do prefeito
        D.papel(ctx)
        ctx.save()
        camera(ctx, 1.6, 540, 820)
        D.careca(ctx, 540, CHAO, 1.0, cabelo=1.0, t=t)
        D.forma(ctx, [(430, 1020), (650, 1100), (630, 1160), (450, 1080)], fill=D.VERMELHO, w=6)
        q = fase(p, 0.74, 0.95)
        hx, hy = 540, CHAO - 420
        for sx in (-1, 1):
            D.linha(ctx, [(hx, hy + 45), (hx + sx * 45, hy + 40), (hx + sx * 75, hy + 20), (hx + sx * 70, hy + 2),
                          (hx + sx * 58, hy + 12)], 14, prog=q)
        if q < 1:
            D.lapis(ctx, hx + 70 * (q * 2 - 1), hy + 30, -0.9, 180, 24)
        ctx.restore()
        D.texto(ctx, "PREFEITO", 540, 420, 90, fill=D.BRANCO, stroke=TINTA, sw=14)
    else:
        # noite: todo mundo desenhando
        n2a, n2b = ev["n2"]
        p2 = fase(t, n2a, n2b)
        noite(ctx, 1.0)
        D.estrelas(ctx, 40)
        D.lua(ctx, 850, 330)
        ctx.save()
        camera(ctx, lerp(1.05, 1.0, p2), 540, 1000)
        for k, x in enumerate([60, 380, 700]):
            pr = (fase(t, n2a + k * 0.4, n2a + 2.2 + k * 0.4))
            D.casa(ctx, x, CHAO, 250, 230, telhado=[D.VERMELHO, D.ROXO, D.VERDE][k], prog=pr)
        for k, x in enumerate([200, 520, 840]):
            D.vizinho(ctx, x, CHAO + 210, 0.55, [D.VERDE, (0.95, 0.6, 0.4), D.ROXO][k], k, t)
            D.lapis(ctx, x + 40, CHAO + 20 + math.sin(t * 18 + k) * 25, -2.2, 140, 20)
        D.chao(ctx, CHAO)
        ctx.restore()
        D.texto(ctx, "TODA NOITE...", 540, 560, 90, fill=D.AMARELO, stroke=TINTA, sw=14)


def borracha(ctx, t, ev, G):
    n3a, n3b = ev["n3"]
    n4a, n4b = ev["n4"]
    ca = ev["careca"][0]
    if t < n4b:
        D.papel(ctx)
        amanhecer(ctx, 1 - fase(t, n3a, n3b) * 0.6)
        sy = lerp(1350, 450, suave(fase(t, n3a, n3a + 2.0)))
        D.sol(ctx, 900, sy, 85, t * 0.5)
        t0, t1 = n3a + 2.0, n4b
        for k, x in enumerate([60, 640]):
            D.casa(ctx, x, CHAO, 240, 220, telhado=[D.VERMELHO, D.VERDE][k])
        D.relogio_torre(ctx, 460, CHAO, 6, 0, 0.75)
        # banco "não desenhado" (tracejado) que some
        vis, br = passou(800, t, t0, t1)
        if vis:
            contorno_tracejado(ctx, [(720, CHAO - 120), (900, CHAO - 120), (900, CHAO), (720, CHAO)], 0.6)
            D.texto(ctx, "?", 810, CHAO - 150, 70, fill=TINTA, alpha=fase(t, n4a, n4a + .3))
        D.brilhos(ctx, 810, CHAO - 60, br)
        D.chao(ctx, CHAO)
        if t > t0:
            D.luz_borracha(ctx, lerp(-300, W + 300, fase(t, t0, t1)))
        D.texto(ctx, "6:00", 540, 400, 120, fill=D.AMARELO, stroke=TINTA, sw=18)
        D.texto(ctx, "SOL-BORRACHA", 540, 520, 80, fill=D.ROSA, stroke=TINTA, sw=14,
                alpha=fase(t, n3a + 2.0, n3a + 2.4))
    else:
        D.papel(ctx)
        ctx.save()
        camera(ctx, 1.25, 540, 950)
        g = ev["grito"][0]
        treme(ctx, 9 if g <= t < g + 0.6 else 0, t)
        vis = t < ca + 0.25
        D.careca(ctx, 540, CHAO, 1.0, cabelo=1.0 if vis else 0.0, fala=G.fala("careca"), t=t,
                 humor="bravo" if t >= g else ("susto" if not vis else "normal"))
        D.brilhos(ctx, 540, CHAO - 560, fase(t, ca + 0.25, ca + 0.85), 10, 160)
        D.chao(ctx, CHAO)
        ctx.restore()
        if t < ca + 0.5:
            D.luz_borracha(ctx, lerp(-300, W + 300, fase(t, ca - 0.3, ca + 0.5)))


def explica(ctx, t, ev, G):
    D.papel(ctx)
    ctx.save()
    camera(ctx, 1.12, 540, 980)
    casa_sumida(ctx)
    D.chao(ctx, CHAO)
    D.cama(ctx, 760, CHAO, 340)
    t2 = ev["t2"][0]
    if t < t2:
        be, bd, humor = 2.5, 2.5, "susto"
    else:
        be, bd, humor = 1.3 + math.sin(t * 6) * 0.1, 1.3, "sem_graca"
    D.teo(ctx, 400, CHAO, 1.0, humor=humor, fala=G.fala("teo"), t=t, braco_e=be, braco_d=bd)
    ctx.restore()
    if t >= t2:
        D.texto(ctx, "???", 400, 420, 100, fill=D.AMARELO, stroke=TINTA, sw=14, rot=0.1)


def vo(ctx, t, ev, G):
    D.papel(ctx)
    chega = ev["chega"]
    v2a = ev["v2"][0]
    culpa = ev["culpa"]
    v3a = ev["v3"][0]
    la = ev["lapis"][0]
    if v2a <= t < culpa[0]:
        # close no toco de lápis
        ctx.save()
        camera(ctx, 2.2, 700, 820)
        D.vo(ctx, 700, CHAO, 1.0, fala=G.fala("vo"), t=t, braco_d=2.4, toco_mao=True, humor="triste")
        ctx.restore()
        D.texto(ctx, "11 ANOS", 540, 380, 110, fill=D.AMARELO, stroke=TINTA, sw=16)
        return
    ctx.save()
    zoom = 1.1 if t < culpa[0] else lerp(1.1, 1.3, fase(t, culpa[0], culpa[1]))
    camera(ctx, zoom, 540, 960)
    D.chao(ctx, CHAO)
    casa_sumida(ctx, 200, 500, 380, 0.3)
    vx = lerp(1250, 740, suave(fase(t, chega[0], chega[1])))
    andando = t < chega[1]
    humor_t = "triste" if t >= culpa[0] else "normal"
    tem_lapis = t >= la + 0.3
    D.teo(ctx, 320, CHAO, 0.95, humor=humor_t if not tem_lapis else "susto", fala=G.fala("teo"), t=t,
          olhar=(14, 0), lapis_mao=tem_lapis, braco_d=1.6 if tem_lapis else 0.3)
    estende = t >= v3a
    D.vo(ctx, vx, CHAO - (abs(math.sin(t * 12)) * 12 if andando else 0), 0.95, fala=G.fala("vo"), t=t,
         lapis_mao=estende and not tem_lapis, braco_e=1.5 if estende and not tem_lapis else 0.25,
         humor="feliz" if estende else "normal")
    if estende and not tem_lapis:
        D.ret(ctx, 470, CHAO - 470, 140, 70, fill=D.BRANCO, w=5)
        D.texto(ctx, "TÉO", 540, CHAO - 418, 54, "Luckiest Guy", fill=D.VERMELHO)
    D.brilhos(ctx, 420, CHAO - 330, fase(t, la, la + 0.8), 10, 150)
    if culpa[0] <= t < culpa[1]:
        D.texto(ctx, "...", 320, CHAO - 560, 90, fill=TINTA)
    ctx.restore()


def noite_c(ctx, t, ev, G):
    noite(ctx, 0.92)
    D.estrelas(ctx, 30)
    D.lua(ctx, 880, 320)
    n6a = ev["n6"][0]
    ctx.save()
    camera(ctx, lerp(1.0, 1.12, fase(t, 0, ev["fim"][1])), 540, 1000)
    D.relogio_torre(ctx, 900, CHAO, 22, 0, 0.6, (0.6, 0.55, 0.5))
    D.chao(ctx, CHAO)
    humor = "sem_graca" if t >= n6a else "normal"
    D.teo(ctx, 430, CHAO, 1.0, humor=humor, t=t, lapis_mao=True, braco_d=1.5, fala=G.fala("teo"))
    ctx.restore()
    D.texto(ctx, "22:00", 540, 420, 100, fill=D.AMARELO, stroke=TINTA, sw=14)
    if t >= n6a:
        a = fase(t, n6a, n6a + 0.25)
        D.texto(ctx, "NÍVEL DE DESENHO: 0", 560, 560, 70, fill=D.VERMELHO, stroke=D.BRANCO, sw=12, alpha=a, rot=-0.05)


def porta(ctx, t, ev, G):
    noite(ctx, 0.92)
    D.estrelas(ctx, 20)
    da, db = ev["desenha"]
    ab = ev["abre"][0]
    ctx.save()
    camera(ctx, 1.25, 600, 950)
    D.chao(ctx, CHAO)
    px, pw, ph = 560, 200, 380
    pr = fase(t, da, db)
    aberta = suave(fase(t, ab, ab + 0.35))
    if pr >= 1:
        # parede de tijolos atrás da porta
        D.ret(ctx, px, CHAO - ph, pw, ph, fill=(0.85, 0.4, 0.3))
        for r in range(7):
            y = CHAO - ph + r * 55
            D.linha(ctx, [(px, y), (px + pw, y)], 4, alpha=0.6)
            off = 50 if r % 2 else 0
            for c in range(3):
                D.linha(ctx, [(px + off + c * 100, y), (px + off + c * 100, y + 55)], 4, alpha=0.6)
    w_porta = pw * (1 - aberta * 0.85)
    D.ret(ctx, px, CHAO - ph, w_porta, ph, fill=D.MARROM if pr >= 1 else None, prog=pr)
    if pr >= 1:
        D.disco(ctx, px + w_porta - 25, CHAO - ph / 2, 10, D.AMARELO)
    D.teo(ctx, 320, CHAO, 1.0, humor="reto" if t >= ab + 0.4 else "normal", fala=G.fala("teo"), t=t,
          lapis_mao=True, braco_d=1.4 if t < db else 0.4, olhar=(14, 0))
    if t < db:
        D.lapis(ctx, px + pw / 2 + math.cos(pr * 12) * 100, CHAO - ph / 2 + math.sin(pr * 9) * 180, -0.9, 170, 24)
    ctx.restore()


def cachorro(ctx, t, ev, G):
    noite(ctx, 0.92)
    D.estrelas(ctx, 20)
    da, db = ev["desenha"]
    na = ev["nasce"][0]
    ctx.save()
    camera(ctx, 1.25, 560, 980)
    D.chao(ctx, CHAO)
    pr = fase(t, da, db)
    esc = pop(t, na) if t >= na else 1.0
    nome = ev["nome"][0]
    D.teo(ctx, 330, CHAO, 1.0, humor="feliz" if t >= nome else "normal", fala=G.fala("teo"), t=t,
          lapis_mao=True, braco_d=1.2, olhar=(14, 6))
    ctx.save()
    ctx.translate(720, CHAO)
    ctx.scale(esc, esc)
    D.rabisco(ctx, 0, 0, 1.0, t=t, prog=pr if t < na else 1.0)
    ctx.restore()
    D.brilhos(ctx, 720, CHAO - 120, fase(t, na, na + 0.6), 8, 140)
    if t < db:
        D.lapis(ctx, 650 + math.cos(pr * 10) * 90, CHAO - 120 + math.sin(pr * 7) * 60, -0.9, 150, 22)
    aua, aub = ev["au"]
    if aua <= t < nome:
        D.balao(ctx, 800, CHAO - 260, "Au?", 70)
    ctx.restore()


def privada(ctx, t, ev, G):
    noite(ctx, 0.92)
    D.estrelas(ctx, 20)
    da, db = ev["desenha"]
    pa = ev["pernas"][0]
    fa = ev["foge"][0]
    ctx.save()
    camera(ctx, 1.15, 560, 980)
    treme(ctx, 5 if pa <= t < pa + 0.3 else 0, t)
    D.chao(ctx, CHAO)
    pr = fase(t, da, db)
    pernas = suave(fase(t, pa, pa + 0.4))
    fx = 700 + max(0.0, t - fa) * 900
    D.teo(ctx, 300, CHAO, 1.0, humor="susto" if t >= pa else "normal", fala=G.fala("teo"), t=t,
          lapis_mao=True, braco_d=2.6 if t >= ev["grito"][0] else 1.2, olhar=(14, 0))
    D.privada(ctx, fx, CHAO, 0.9, t=t, pernas=pernas, correndo=t >= fa, prog=pr)
    if t >= fa:
        D.rabisco(ctx, fx - 330 + max(0, t - fa - 0.3) * 200, CHAO, 0.8, t=t, andando=True)
    if t < db:
        D.lapis(ctx, fx + math.cos(pr * 10) * 80, CHAO - 150 + math.sin(pr * 7) * 100, -0.9, 150, 22)
    if pa <= t < pa + 0.6:
        D.texto(ctx, "BOING!", fx, CHAO - 380, 60, fill=D.AMARELO, stroke=TINTA, sw=10)
    ctx.restore()


def mansao(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    D.ret(ctx, -300, -420, 600, 420, fill=(0.97, 0.97, 1))
    D.forma(ctx, [(-340, -420), (0, -620), (340, -420)], fill=(0.3, 0.35, 0.6))
    for k in range(5):
        D.ret(ctx, -270 + k * 120, -400, 30, 400, fill=D.BRANCO, w=5)
    D.ret(ctx, -60, -210, 120, 210, fill=D.MARROM)
    for k in (-1, 1):
        D.ret(ctx, k * 190 - 45, -330, 90, 90, fill=(0.7, 0.88, 1))
    D.texto(ctx, "N", 0, -480, 80, fill=D.OURO, stroke=TINTA, sw=8)
    ctx.restore()


def nanquim(ctx, t, ev, G):
    pe = ev["pe"]
    if t < pe[0]:
        D.papel(ctx, 0.5)
        D.S.ink = TINTA
        D.estrelas(ctx, 15)
        ctx.save()
        camera(ctx, 0.95, 540, 980)
        mansao(ctx, 560, CHAO, 0.95)
        D.chao(ctx, CHAO)
        rindo = abs(math.sin(t * 14)) if t < ev["riso"][1] else 0
        D.nanquim(ctx, 330, CHAO + 20 - rindo * 10, 1.0, fala=G.fala("nanquim"), t=t, humor="feliz",
                  braco_d=2.3, braco_e=0.5)
        ctx.restore()
        D.texto(ctx, "SEU NANQUIM", 540, 380, 80, fill=D.BRANCO, stroke=TINTA, sw=14)
        D.texto(ctx, "(o vizinho exibido)", 540, 460, 54, "Patrick Hand", fill=TINTA,
                alpha=fase(t, 0.3, 0.6))
        return
    noite(ctx, 0.92)
    ctx.save()
    # câmera desce até o pé
    cy = lerp(950, 1150, suave(fase(t, pe[0], pe[0] + 0.5)))
    camera(ctx, lerp(1.2, 1.7, fase(t, pe[0], pe[0] + 0.5)), 500, cy)
    casa_torta(ctx, 620)
    D.chao(ctx, CHAO)
    D.teo(ctx, 430, CHAO, 1.0, humor="sem_graca", fala=G.fala("teo"), t=t, pe_lapis=True,
          braco_e=0.2, braco_d=0.2)
    ctx.restore()
    if t >= pe[0] + 0.4:
        D.texto(ctx, "...COM O PÉ.", 540, 1330, 90, fill=D.AMARELO, stroke=TINTA, sw=14,
                alpha=fase(t, pe[0] + 0.4, pe[0] + 0.6))


def relogio(ctx, t, ev, G):
    n7a, n7b = ev["n7"]
    cr = ev["crack"][0]
    if t < n7a + (n7b - n7a) * 0.5:
        noite(ctx, 0.92)
        amanhecer(ctx, 0.35)
        ctx.save()
        camera(ctx, lerp(1.6, 1.9, fase(t, 0, n7b)), 540, 1000)
        mins = 58 + (0.3 if (t * 2) % 2 < 1 else 0)
        D.relogio_torre(ctx, 540, CHAO + 200, 5, mins, 1.0, (0.6, 0.55, 0.5))
        ctx.restore()
        D.texto(ctx, "5:58", 540, 420, 140, fill=D.VERMELHO, stroke=D.BRANCO, sw=16)
        return
    noite(ctx, 0.92)
    amanhecer(ctx, 0.4)
    ctx.save()
    camera(ctx, 1.12, 560, 980)
    treme(ctx, 10 if cr <= t < cr + 0.4 else 0, t)
    casa_torta(ctx, 600)
    D.texto(ctx, "?", 770, CHAO - 420, 120, fill=GIZ, stroke=TINTA, sw=10)
    D.chao(ctx, CHAO)
    quebrado = t >= cr
    nao = ev["nao"][0]
    D.teo(ctx, 360, CHAO, 1.0, humor="susto" if quebrado else "normal", fala=G.fala("teo"), t=t,
          lapis_mao=True, lapis_quebrado=quebrado, braco_d=2.8 if t >= nao else 1.3,
          braco_e=2.8 if t >= nao else 0.3)
    if quebrado:
        q = fase(t, cr, cr + 0.8)
        D.lapis(ctx, 470 + q * 200, CHAO - 420 + q * q * 400, q * 8, 90, 22)
        if t < cr + 0.5:
            D.texto(ctx, "CRACK!", 560, CHAO - 600, 90, fill=D.VERMELHO, stroke=D.BRANCO, sw=14, rot=-0.1)
    ctx.restore()


def luz(ctx, t, ev, G):
    n8a, n8b = ev["n8"]
    D.papel(ctx)
    amanhecer(ctx, 0.9)
    t0, t1 = 0.0, ev["fim"][1] + 4.0  # a faixa não termina nessa cena
    ctx.save()
    camera(ctx, 1.0, 540, 980)
    D.sol(ctx, 160, lerp(800, 560, fase(t, 0, ev["fim"][1])), 80, t * 0.4)
    objs = [(180, "banco"), (430, "poste"), (560, "pombo")]
    for x, tipo in objs:
        vis, br = passou(x, t, t0, t1, -400, 1500)
        if vis:
            {"banco": lambda: D.banco(ctx, x - 90, CHAO), "poste": lambda: D.poste(ctx, x, CHAO),
             "pombo": lambda: D.pombo(ctx, x, CHAO)}[tipo]()
        D.brilhos(ctx, x, CHAO - 80, br, 8, 120)
    casa_torta(ctx, 680)
    D.chao(ctx, CHAO)
    ctx.restore()
    bx = lerp(-400, 1500, fase(t, t0, t1))
    D.luz_borracha(ctx, bx)
    D.texto(ctx, "5:59", 540, 400, 140, fill=D.VERMELHO, stroke=D.BRANCO, sw=16)
    for k, (x, _) in enumerate(objs):
        tc = t0 + (x + 400) / 1900 * (t1 - t0)
        if tc <= t < tc + 0.5:
            D.texto(ctx, "PLIM!", x, CHAO - 380, 60, fill=D.AMARELO, stroke=TINTA, sw=10)


def vo_salva(ctx, t, ev, G):
    chega = ev["chega"]
    v4a, v4b = ev["v4"]
    maos = ev["maos"]
    D.papel(ctx)
    amanhecer(ctx, 0.9)
    if t >= maos[0]:
        # close nas duas mãos segurando o toquinho
        ctx.save()
        camera(ctx, 1.0 + 0.1 * fase(t, maos[0], maos[1]), 540, 900)
        D.linha(ctx, [(0, 1300), (430, 900)], 80, D.AZUL_PIJ)
        D.linha(ctx, [(1080, 1300), (650, 900)], 80, D.ROXO)
        D.elipse(ctx, 470, 880, 90, 80, fill=D.PELE)
        D.elipse(ctx, 610, 870, 95, 85, fill=D.PELE)
        D.lapis(ctx, 540, 760, -1.2, 0, 40, toco=True)
        ctx.restore()
        D.texto(ctx, "SÓ UMA LINHA", 540, 420, 100, fill=D.AMARELO, stroke=TINTA, sw=16)
        return
    ctx.save()
    camera(ctx, 1.1, 560, 980)
    D.luz_borracha(ctx, lerp(-250, -100, fase(t, 0, maos[0])), 0.8)
    casa_torta(ctx, 640)
    D.chao(ctx, CHAO)
    vx = lerp(-200, 460, suave(fase(t, chega[0], chega[1])))
    D.teo(ctx, 300, CHAO, 0.95, humor="triste", t=t, braco_e=0.2, braco_d=0.2, olhar=(-14, 0))
    D.vo(ctx, vx, CHAO - (abs(math.sin(t * 16)) * 20 if t < chega[1] else 0), 0.95, fala=G.fala("vo"), t=t,
         braco_d=2.6 if t >= v4a else 0.5, toco_mao=True, lapis_orelha=False, humor="feliz")
    ctx.restore()


def telhado(ctx, t, ev, G):
    da, db = ev["desenha"]
    la, lb = ev["luz"]
    br = ev["branco"]
    D.papel(ctx)
    amanhecer(ctx, 1.0)
    ctx.save()
    camera(ctx, lerp(1.05, 1.15, fase(t, da, db)), 560, 950)
    tl = suave(fase(t, da, db - 0.3))
    casa_torta(ctx, 560, telhado=tl if tl < 1 else 1.0)
    D.chao(ctx, CHAO)
    D.teo(ctx, 210, CHAO, 0.95, humor="susto", t=t, lapis_mao=False, braco_d=2.1, olhar=(10, -10))
    D.vo(ctx, 420, CHAO, 0.9, humor="normal", t=t, braco_e=2.0, lapis_orelha=False)
    if t < db:
        cx, cy = 728, CHAO - 470
        a = tl * 2 * math.pi
        D.lapis(ctx, cx + 16 * math.sin(a) ** 3 * 12.5,
                cy - (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * 11,
                -1.2, 0, 26, toco=True)
    ctx.restore()
    if t < la:
        D.texto(ctx, "5:59:59", 540, 400, 110, fill=D.VERMELHO, stroke=D.BRANCO, sw=14)
    if t >= la:
        D.luz_borracha(ctx, lerp(-300, W + 300, fase(t, la, lb)), largura=420)
    # clarão branco
    a = fase(t, lb - 0.5, lb) if t < br[0] else 1.0
    if a > 0:
        ctx.set_source_rgba(1, 1, 0.97, a)
        ctx.paint()


def sobreviveu(ctx, t, ev, G):
    rv = ev["revela"]
    pl = ev["plim"][0]
    rip = ev["rip"][0]
    D.papel(ctx)
    ctx.save()
    camera(ctx, lerp(1.2, 1.05, suave(fase(t, rv[0], rv[1]))), 560, 960)
    D.sol(ctx, 900, 420, 85, t * 0.4)
    casa_torta(ctx, 560, telhado=1.0)
    D.chao(ctx, CHAO)
    D.brilhos(ctx, 730, CHAO - 400, fase(t, rv[0] + 0.1, rv[0] + 1.0), 12, 260)
    # privada (não redesenhada) some
    if t < pl + 0.1:
        D.privada(ctx, 960, CHAO, 0.6, t=t, pernas=1.0, alpha=0.9)
    D.brilhos(ctx, 960, CHAO - 150, fase(t, pl + 0.1, pl + 0.7), 8, 120)
    if t >= pl + 0.4:
        D.forma(ctx, [(910, CHAO), (910, CHAO - 120), (960, CHAO - 160), (1010, CHAO - 120), (1010, CHAO)],
                fill=D.CINZA)
        D.texto(ctx, "RIP", 960, CHAO - 50, 40, fill=TINTA)
    pulo = 50 * abs(math.sin(t * 8)) if ev["au"][0] <= t < ev["au"][1] + 0.4 else 0
    D.rabisco(ctx, 470, CHAO, 0.8, t=t, pulo=pulo)
    D.teo(ctx, 250, CHAO, 0.9, humor="feliz" if t < rip else "triste", fala=G.fala("teo"), t=t,
          braco_e=0.3, braco_d=2.2 if t < rip else 1.0)
    ctx.restore()
    if ev["au"][0] <= t < pl:
        D.balao(ctx, 560, 1000, "AU!", 80)
    if pl <= t < pl + 0.6:
        D.texto(ctx, "PLIM!", 900, 900, 80, fill=D.AMARELO, stroke=TINTA, sw=12)
    a = 1 - fase(t, rv[0], rv[0] + 0.6)
    if a > 0:
        ctx.set_source_rgba(1, 1, 0.97, a)
        ctx.paint()


def cueca(ctx, t, ev, G):
    D.papel(ctx)
    en = ev["entra"]
    rs = ev["risada"][0]
    ctx.save()
    camera(ctx, 1.1, 560, 960)
    D.sol(ctx, 950, 380, 75, t * 0.4)
    mansao(ctx, 620, CHAO, 0.8)
    D.chao(ctx, CHAO)
    nx = lerp(640, 380, suave(fase(t, en[0], en[1] + 0.3)))
    humor = "feliz" if t < ev["calcas"][0] + 0.3 else "sem_graca"
    D.nanquim(ctx, nx, CHAO, 1.0, cueca=True, fala=G.fala("nanquim"), t=t, humor=humor, braco_e=0.35, braco_d=0.35)
    ctx.restore()
    if t >= rs:
        for k, (x, y, r) in enumerate([(200, 450, -0.2), (800, 520, 0.15), (540, 340, 0)]):
            D.texto(ctx, "HA HA HA", x, y + math.sin(t * 20 + k) * 8, 70, fill=D.AMARELO, stroke=TINTA, sw=12,
                    rot=r, alpha=fase(t, rs + k * 0.15, rs + k * 0.15 + 0.1))


def final(ctx, t, ev, G):
    D.papel(ctx)
    ctx.save()
    camera(ctx, 1.12, 540, 960)
    D.sol(ctx, 930, 360, 80, t * 0.4)
    casa_torta(ctx, 620, telhado=1.0)
    D.chao(ctx, CHAO)
    v5 = ev["v5"]
    t2 = ev["t2"][0]
    D.teo(ctx, 230, CHAO, 0.9, humor="feliz" if t >= t2 else "normal", fala=G.fala("teo"), t=t,
          olhar=(14, 0), braco_d=0.6)
    D.vo(ctx, 470, CHAO, 0.9, humor="feliz" if t >= v5[0] else "normal", fala=G.fala("vo"), t=t,
         lapis_orelha=False)
    D.rabisco(ctx, 345, CHAO, 0.55, t=t)
    ctx.restore()
    if t >= v5[0] and t < t2:
        D.texto(ctx, "COM O PÉ?", 540, 420, 90, fill=D.AMARELO, stroke=TINTA, sw=14)


def mao(ctx, t, ev, G):
    so = ev["sobe"]
    n9 = ev["n9"]
    fim = ev["fim"]
    up = suave(fase(t, so[0], so[1]))
    D.papel(ctx)
    ctx.set_source_rgba(0.55, 0.75, 0.95, 0.5 + 0.3 * up)
    ctx.paint()
    escuro = fase(t, n9[0], n9[1])
    ctx.save()
    ctx.translate(0, up * 1400)
    casa_torta(ctx, 380, telhado=1.0)
    D.chao(ctx, CHAO)
    ctx.restore()
    for k in range(4):
        y = (k * 520 + up * 1300) % 2300 - 200
        D.nuvem(ctx, 250 + (k % 2) * 560, y, 1.2)
    if escuro > 0:
        ctx.set_source_rgba(0.1, 0.05, 0.2, 0.45 * escuro)
        ctx.paint()
    my = lerp(-800, 600, suave(fase(t, n9[0], n9[0] + 1.4)))
    D.mao_gigante(ctx, 540, my, 1.3)
    if t >= fim[0]:
        a = fase(t, fim[0], fim[0] + 0.3)
        D.texto(ctx, "CONTINUA...", 540, 1250, 110, fill=D.AMARELO, stroke=TINTA, sw=16, alpha=a)
        D.texto(ctx, "O que VOCÊ esqueceria", 540, 1400, 64, "Patrick Hand", fill=D.BRANCO, stroke=TINTA,
                sw=12, alpha=fase(t, fim[0] + 0.6, fim[0] + 0.9))
        D.texto(ctx, "de desenhar? Comenta!", 540, 1480, 64, "Patrick Hand", fill=D.BRANCO, stroke=TINTA,
                sw=12, alpha=fase(t, fim[0] + 0.6, fim[0] + 0.9))


CENAS = {
    "acordar": acordar, "titulo": titulo, "cidade": cidade, "borracha": borracha, "explica": explica,
    "vo": vo, "noite": noite_c, "porta": porta, "cachorro": cachorro, "privada": privada,
    "nanquim": nanquim, "relogio": relogio, "luz": luz, "vo_salva": vo_salva, "telhado": telhado,
    "sobreviveu": sobreviveu, "cueca": cueca, "final": final, "mao": mao,
}
