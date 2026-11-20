"""Mascote do canal em estilo 2.5D (volume com luz e sombra): rosto redondo, boné, camiseta, calça e sapato preto.

Uso: mascote.desenha(ctx, x, y, escala, humor=..., fala=..., t=..., braco_e=..., braco_d=...)
x,y = chão entre os pés. Luz vem do alto à esquerda.
"""
import math
import cairo

CONTORNO = (0.16, 0.11, 0.10)

PALETA = {
    "pele": (0.96, 0.76, 0.60), "pele_sombra": (0.80, 0.56, 0.42),
    "bone": (0.22, 0.48, 0.95), "bone_sombra": (0.10, 0.25, 0.62),
    "camiseta": (0.95, 0.30, 0.25), "camiseta_sombra": (0.66, 0.14, 0.14),
    "calca": (0.30, 0.42, 0.68), "calca_sombra": (0.15, 0.22, 0.40),
    "sapato": (0.16, 0.16, 0.18), "sapato_sombra": (0.03, 0.03, 0.04),
    "cabelo": (0.28, 0.18, 0.12), "iris": (0.40, 0.24, 0.12),
}


def _cor(c, a=1.0):
    return (*c[:3], a)


def _grad_lin(x0, y0, x1, y1, c_luz, c_sombra):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    g.add_color_stop_rgba(0, *_cor(c_luz))
    g.add_color_stop_rgba(1, *_cor(c_sombra))
    return g


def _grad_rad(cx, cy, r, c_luz, c_sombra, ox=-0.35, oy=-0.4):
    g = cairo.RadialGradient(cx + ox * r, cy + oy * r, r * 0.05, cx, cy, r * 1.05)
    g.add_color_stop_rgba(0, *_cor(tuple(min(1, v * 1.08) for v in c_luz)))
    g.add_color_stop_rgba(0.55, *_cor(c_luz))
    g.add_color_stop_rgba(1, *_cor(c_sombra))
    return g


def _preenche(ctx, fonte, contorno=6):
    ctx.set_source(fonte) if isinstance(fonte, cairo.Pattern) else ctx.set_source_rgba(*_cor(fonte))
    ctx.fill_preserve()
    if contorno:
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(contorno)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    else:
        ctx.new_path()


def _circulo(ctx, cx, cy, r):
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)


def _elipse(ctx, cx, cy, rx, ry, rot=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(rx, ry)
    ctx.new_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def _tubo(ctx, pts, w, c_luz, c_sombra, brilho=True):
    """membro cilíndrico: contorno escuro + degradê atravessado + filete de brilho."""
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    if nx + ny > 0:  # lado iluminado = alto/esquerda
        nx, ny = -nx, -ny
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2

    def caminho():
        ctx.new_path()
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)

    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    caminho()
    ctx.set_source_rgba(*_cor(CONTORNO))
    ctx.set_line_width(w + 12)
    ctx.stroke()
    caminho()
    ctx.set_source(_grad_lin(mx + nx * w / 2, my + ny * w / 2, mx - nx * w / 2, my - ny * w / 2, c_luz, c_sombra))
    ctx.set_line_width(w)
    ctx.stroke()
    if brilho:
        ctx.new_path()
        ctx.move_to(pts[0][0] + nx * w * 0.25, pts[0][1] + ny * w * 0.25)
        for p in pts[1:]:
            ctx.line_to(p[0] + nx * w * 0.25, p[1] + ny * w * 0.25)
        ctx.set_source_rgba(1, 1, 1, 0.22)
        ctx.set_line_width(w * 0.18)
        ctx.stroke()


def _pisca(t, ciclo=3.7):
    return (t % ciclo) < 0.12


def _braco(ctx, lado, ang, dobra, P, onda=0.0, t=0.0):
    """lado=-1 esquerdo da tela, +1 direito. ang: 0 caído, positivo abre, pi pra cima."""
    ox, oy = lado * 112, -600
    a1 = ang + onda * math.sin(t * 14) * 0.25
    ex, ey = ox + lado * math.sin(a1) * 125, oy + math.cos(a1) * 125
    a2 = a1 + dobra + onda * math.sin(t * 14 + 0.8) * 0.5
    hx, hy = ex + lado * math.sin(a2) * 115, ey + math.cos(a2) * 115
    _tubo(ctx, [(ox, oy), (ex, ey), (hx, hy)], 52, P["pele"], P["pele_sombra"])
    # mão
    _circulo(ctx, hx, hy, 34)
    _preenche(ctx, _grad_rad(hx, hy, 34, P["pele"], P["pele_sombra"]))
    tx, ty = hx - lado * 26 * math.cos(a2), hy + 26 * math.sin(a2) * (1 if lado > 0 else -1) * 0 - 18
    _elipse(ctx, tx, ty, 14, 20, -lado * 0.5)
    _preenche(ctx, _grad_rad(tx, ty, 18, P["pele"], P["pele_sombra"]), 5)
    # manga (desenhada por cima do ombro)
    sx, sy = ox + lado * math.sin(a1) * 52, oy + math.cos(a1) * 52
    _tubo(ctx, [(ox, oy), (sx, sy)], 92, P["camiseta"], P["camiseta_sombra"], brilho=False)
    return hx, hy


def _olho(ctx, cx, cy, humor, piscando, olhar, P):
    if humor == "feliz" or (humor == "dorme"):
        ctx.new_path()
        ctx.arc(cx, cy + 12, 30, math.pi * 1.15, math.pi * 1.85)
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(9)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        return
    if piscando:
        ctx.new_path()
        ctx.move_to(cx - 30, cy + 4)
        ctx.curve_to(cx - 10, cy + 14, cx + 10, cy + 14, cx + 30, cy + 4)
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(8)
        ctx.stroke()
        return
    rx, ry = (36, 46) if humor == "susto" else (32, 42)
    _elipse(ctx, cx, cy, rx, ry)
    g = cairo.LinearGradient(cx, cy - ry, cx, cy + ry)
    g.add_color_stop_rgba(0, 1, 1, 1, 1)
    g.add_color_stop_rgba(1, 0.86, 0.88, 0.95, 1)
    _preenche(ctx, g, 6)
    ir = 13 if humor == "susto" else 22
    ix, iy = cx + olhar[0] * 8, cy + 6 + olhar[1] * 8
    _circulo(ctx, ix, iy, ir)
    ctx.set_source(_grad_lin(ix, iy - ir, ix, iy + ir, P["iris"], tuple(v * 0.4 for v in P["iris"])))
    ctx.fill()
    _circulo(ctx, ix, iy, ir * 0.5)
    ctx.set_source_rgba(0.05, 0.03, 0.03, 1)
    ctx.fill()
    _circulo(ctx, ix - ir * 0.35, iy - ir * 0.4, ir * 0.32)
    ctx.set_source_rgba(1, 1, 1, 0.95)
    ctx.fill()
    _circulo(ctx, ix + ir * 0.35, iy + ir * 0.35, ir * 0.15)
    ctx.fill()


def _boca(ctx, x, y, humor, fala):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if fala > 0.08 or humor == "susto":
        h = 18 + 42 * min(1.0, fala) if fala > 0.08 else 30
        w = 48 if humor != "susto" else 26
        ctx.new_path()
        ctx.move_to(x - w, y - 4)
        ctx.curve_to(x - w * 0.6, y - 10, x + w * 0.6, y - 10, x + w, y - 4)
        ctx.curve_to(x + w * 0.9, y + h, x - w * 0.9, y + h, x - w, y - 4)
        ctx.close_path()
        ctx.set_source_rgba(0.45, 0.10, 0.14, 1)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip_preserve()
        _elipse(ctx, x, y + h * 0.85, w * 0.6, h * 0.45)
        ctx.set_source_rgba(0.95, 0.45, 0.50, 1)
        ctx.fill()
        ctx.rectangle(x - w, y - 12, w * 2, 12)
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill()
        ctx.restore()
        ctx.move_to(x - w, y - 4)
        ctx.curve_to(x - w * 0.6, y - 10, x + w * 0.6, y - 10, x + w, y - 4)
        ctx.curve_to(x + w * 0.9, y + h, x - w * 0.9, y + h, x - w, y - 4)
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(6)
        ctx.stroke()
        return
    ctx.new_path()
    if humor == "triste":
        ctx.move_to(x - 34, y + 14)
        ctx.curve_to(x - 12, y - 8, x + 12, y - 8, x + 34, y + 14)
    elif humor == "sem_graca":
        ctx.move_to(x - 36, y + 4)
        ctx.curve_to(x - 12, y + 14, x + 8, y - 8, x + 36, y)
    else:
        ctx.move_to(x - 44, y - 6)
        ctx.curve_to(x - 20, y + 30, x + 20, y + 30, x + 44, y - 6)
    ctx.set_source_rgba(*_cor(CONTORNO))
    ctx.set_line_width(9)
    ctx.stroke()


def desenha(ctx, x, y, s=1.0, humor="normal", fala=0.0, t=0.0, braco_e=0.25, braco_d=0.25, dobra_e=0.15,
            dobra_d=0.15, aceno=False, olhar=(0, 0), pulo=0.0, paleta=None):
    P = dict(PALETA, **(paleta or {}))
    ctx.save()
    # sombra no chão (não sobe com o pulo)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s * 0.18)
    g = cairo.RadialGradient(0, 0, 10, 0, 0, 200)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.35 / (1 + pulo / 150))
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    ctx.arc(0, 0, 200, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    ctx.translate(x, y - pulo)
    ctx.scale(s, s)

    # --- pernas (calça) + sapatos
    for lado in (-1, 1):
        _tubo(ctx, [(lado * 48, -400), (lado * 54, -60)], 84, P["calca"], P["calca_sombra"])
        ctx.new_path()
        ctx.move_to(lado * 54 - 30, -150)
        ctx.line_to(lado * 54 - 26, -70)
        ctx.set_source_rgba(1, 0.85, 0.5, 0.5)
        ctx.set_line_width(3)
        ctx.set_dash([8, 6])
        ctx.stroke()
        ctx.set_dash([])
    for lado in (-1, 1):
        ctx.save()
        ctx.translate(lado * 62, 0)
        ctx.scale(lado, 1)
        bx = 0
        ctx.new_path()
        ctx.move_to(bx - 40, -8)
        ctx.curve_to(bx - 44, -50, bx - 16, -72, bx + 8, -70)
        ctx.curve_to(bx + 40, -68, bx + 66, -40, bx + 68, -12)
        ctx.line_to(bx + 68, 0)
        ctx.line_to(bx - 40, 0)
        ctx.close_path()
        _preenche(ctx, _grad_lin(bx, -72, bx, 0, P["sapato"], P["sapato_sombra"]), 6)
        ctx.rectangle(bx - 42, -12, 112, 14)
        ctx.set_source_rgba(0.45, 0.45, 0.48, 1)
        ctx.fill()
        _elipse(ctx, bx + 4, -52, 22, 8, -0.15)
        ctx.set_source_rgba(1, 1, 1, 0.45)
        ctx.fill()
        ctx.restore()

    # --- tronco (camiseta)
    ctx.new_path()
    ctx.move_to(-120, -620)
    ctx.curve_to(-60, -655, 60, -655, 120, -620)
    ctx.curve_to(128, -520, 122, -440, 116, -385)
    ctx.curve_to(40, -370, -40, -370, -116, -385)
    ctx.curve_to(-122, -440, -128, -520, -120, -620)
    ctx.close_path()
    _preenche(ctx, _grad_lin(-120, -650, 130, -380, P["camiseta"], P["camiseta_sombra"]), 7)
    # dobrinhas e barra
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for (a, b, c, d) in [(-80, -470, -40, -455), (60, -500, 90, -470), (-10, -420, 30, -415)]:
        ctx.move_to(a, b)
        ctx.line_to(c, d)
        ctx.stroke()
    ctx.move_to(-114, -400)
    ctx.curve_to(-40, -386, 40, -386, 114, -400)
    ctx.set_source_rgba(0, 0, 0, 0.22)
    ctx.stroke()

    # --- braços
    _braco(ctx, -1, braco_e, dobra_e, P)
    _braco(ctx, 1, braco_d, dobra_d, P, onda=1.0 if aceno else 0.0, t=t)

    # --- pescoço + gola
    _tubo(ctx, [(0, -640), (0, -680)], 70, P["pele"], P["pele_sombra"], brilho=False)
    _elipse(ctx, 0, -640, 58, 18)
    _preenche(ctx, P["camiseta_sombra"], 6)

    # --- cabeça
    hx, hy, r = 0, -830, 165
    for lado in (-1, 1):
        _circulo(ctx, lado * 160, hy + 10, 32)
        _preenche(ctx, _grad_rad(lado * 160, hy + 10, 32, P["pele"], P["pele_sombra"]))
        _circulo(ctx, lado * 160, hy + 10, 15)
        ctx.set_source_rgba(*_cor(P["pele_sombra"], 0.7))
        ctx.fill()
    _circulo(ctx, hx, hy, r)
    _preenche(ctx, _grad_rad(hx, hy, r, P["pele"], P["pele_sombra"]), 8)
    # costeletas de cabelo
    for lado in (-1, 1):
        ctx.new_path()
        ctx.move_to(lado * 150, hy - 70)
        ctx.curve_to(lado * 165, hy - 40, lado * 160, hy - 20, lado * 148, hy - 10)
        ctx.line_to(lado * 132, hy - 60)
        ctx.close_path()
        _preenche(ctx, P["cabelo"], 5)
    # bochechas
    for lado in (-1, 1):
        g = cairo.RadialGradient(lado * 92, hy + 40, 2, lado * 92, hy + 40, 34)
        g.add_color_stop_rgba(0, 1, 0.45, 0.45, 0.55)
        g.add_color_stop_rgba(1, 1, 0.45, 0.45, 0)
        ctx.set_source(g)
        ctx.arc(lado * 92, hy + 40, 34, 0, 2 * math.pi)
        ctx.fill()
    # olhos
    piscando = _pisca(t)
    if humor == "piscadinha":
        _olho(ctx, -58, hy - 10, "normal", False, olhar, P)
        _olho(ctx, 58, hy - 10, "feliz", False, olhar, P)
    else:
        for lado in (-1, 1):
            _olho(ctx, lado * 58, hy - 10, humor, piscando, olhar, P)
    # sobrancelhas
    for lado in (-1, 1):
        ctx.new_path()
        sob = {"susto": -22, "triste": 6, "bravo": 10}.get(humor, 0)
        incl = {"triste": -14, "bravo": 14}.get(humor, 0)
        ctx.move_to(lado * 30, hy - 66 + sob + incl)
        ctx.curve_to(lado * 50, hy - 76 + sob, lado * 70, hy - 76 + sob, lado * 88, hy - 66 + sob - incl * 0.3)
        ctx.set_source_rgba(*_cor(P["cabelo"]))
        ctx.set_line_width(11)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    # nariz
    ctx.new_path()
    ctx.arc(hx + 4, hy + 30, 14, math.pi * 0.1, math.pi * 0.9)
    ctx.set_source_rgba(*_cor(P["pele_sombra"]))
    ctx.set_line_width(6)
    ctx.stroke()
    _boca(ctx, hx, hy + 78, "feliz" if humor in ("normal", "piscadinha") else humor, fala)

    # --- boné
    # sombra da aba no rosto
    ctx.save()
    _circulo(ctx, hx, hy, r - 4)
    ctx.clip()
    g = cairo.LinearGradient(0, hy - 100, 0, hy - 55)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.28)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    ctx.rectangle(-r, hy - 110, 2 * r, 60)
    ctx.fill()
    ctx.restore()
    cy0 = hy - 92
    ctx.new_path()
    ctx.move_to(-r - 8, cy0)
    ctx.curve_to(-r - 6, hy - 250, r + 6, hy - 250, r + 8, cy0)
    ctx.curve_to(r * 0.5, cy0 + 14, -r * 0.5, cy0 + 14, -r - 8, cy0)
    ctx.close_path()
    _preenche(ctx, _grad_rad(hx - 10, hy - 150, 190, P["bone"], P["bone_sombra"], -0.3, -0.5), 8)
    # costuras + botão + furinhos
    ctx.set_source_rgba(*_cor(P["bone_sombra"]))
    ctx.set_line_width(4)
    for cx in (-70, 0, 70):
        ctx.new_path()
        ctx.move_to(cx * 0.08, hy - 184)
        ctx.curve_to(cx * 0.8, hy - 200, cx * 1.1, hy - 140, cx * 1.15, cy0 + 8)
        ctx.stroke()
    _elipse(ctx, 0, hy - 186, 16, 8)
    _preenche(ctx, P["bone_sombra"], 5)
    # aba (em perspectiva, virada um pouco pra direita)
    ctx.new_path()
    ctx.move_to(-r * 0.9, cy0 + 6)
    ctx.curve_to(-r * 0.5, cy0 + 40, r * 0.9, cy0 + 55, r + 75, cy0 + 22)
    ctx.curve_to(r + 60, cy0 - 6, r * 0.4, cy0 - 2, -r * 0.9, cy0 + 6)
    ctx.close_path()
    _preenche(ctx, _grad_lin(0, cy0 - 5, 0, cy0 + 50, P["bone"], P["bone_sombra"]), 8)
    ctx.new_path()
    ctx.move_to(-r * 0.7, cy0 + 16)
    ctx.curve_to(-r * 0.3, cy0 + 38, r * 0.8, cy0 + 44, r + 50, cy0 + 22)
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.set_line_width(4)
    ctx.set_dash([10, 7])
    ctx.stroke()
    ctx.set_dash([])
    # brilho na copa
    _elipse(ctx, -75, hy - 150, 38, 16, -0.5)
    ctx.set_source_rgba(1, 1, 1, 0.3)
    ctx.fill()
    ctx.restore()
