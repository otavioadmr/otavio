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


# proporções de adulto (unidades com os pés em y=0)
QUADRIL = -540
OMBRO_Y = -905
OMBRO_X = 138
CAB_Y, CAB_RX, CAB_RY = -1085, 112, 124


def _braco(ctx, lado, ang, dobra, P, onda=0.0, t=0.0):
    """lado=-1 esquerdo da tela, +1 direito. ang: 0 caído, positivo abre, pi pra cima."""
    ox, oy = lado * OMBRO_X, OMBRO_Y + 30
    a1 = ang + onda * math.sin(t * 14) * 0.25
    ex, ey = ox + lado * math.sin(a1) * 175, oy + math.cos(a1) * 175
    a2 = a1 + dobra + onda * math.sin(t * 14 + 0.8) * 0.5
    hx, hy = ex + lado * math.sin(a2) * 160, ey + math.cos(a2) * 160
    _tubo(ctx, [(ox, oy), (ex, ey), (hx, hy)], 60, P["pele"], P["pele_sombra"])
    # mão
    _elipse(ctx, hx, hy + 6, 32, 38, a2 * -lado * 0.3)
    _preenche(ctx, _grad_rad(hx, hy, 36, P["pele"], P["pele_sombra"]))
    tx, ty = hx - lado * 30, hy - 12
    _elipse(ctx, tx, ty, 13, 22, -lado * 0.6)
    _preenche(ctx, _grad_rad(tx, ty, 20, P["pele"], P["pele_sombra"]), 5)
    # manga
    sx, sy = ox + lado * math.sin(a1) * 70, oy + math.cos(a1) * 70
    _tubo(ctx, [(ox, oy), (sx, sy)], 104, P["camiseta"], P["camiseta_sombra"], brilho=False)
    return hx, hy


def _olho(ctx, cx, cy, humor, piscando, olhar, P):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if humor in ("feliz", "dorme"):
        ctx.new_path()
        ctx.arc(cx, cy + 10, 22, math.pi * 1.15, math.pi * 1.85)
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(8)
        ctx.stroke()
        return
    if piscando:
        ctx.new_path()
        ctx.move_to(cx - 22, cy + 3)
        ctx.curve_to(cx - 8, cy + 10, cx + 8, cy + 10, cx + 22, cy + 3)
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(7)
        ctx.stroke()
        return
    rx, ry = (25, 30) if humor == "susto" else (22, 24)
    _elipse(ctx, cx, cy, rx, ry)
    g = cairo.LinearGradient(cx, cy - ry, cx, cy + ry)
    g.add_color_stop_rgba(0, 1, 1, 1, 1)
    g.add_color_stop_rgba(1, 0.86, 0.88, 0.95, 1)
    _preenche(ctx, g, 5)
    ir = 8 if humor == "susto" else 14
    ix, iy = cx + olhar[0] * 6, cy + 3 + olhar[1] * 6
    ctx.save()
    _elipse(ctx, cx, cy, rx - 2, ry - 2)
    ctx.clip()
    _circulo(ctx, ix, iy, ir)
    ctx.set_source(_grad_lin(ix, iy - ir, ix, iy + ir, P["iris"], tuple(v * 0.4 for v in P["iris"])))
    ctx.fill()
    _circulo(ctx, ix, iy, ir * 0.5)
    ctx.set_source_rgba(0.05, 0.03, 0.03, 1)
    ctx.fill()
    _circulo(ctx, ix - ir * 0.35, iy - ir * 0.4, ir * 0.3)
    ctx.set_source_rgba(1, 1, 1, 0.95)
    ctx.fill()
    ctx.restore()
    # pálpebra superior (olhar de adulto, menos arregalado)
    if humor != "susto":
        ctx.save()
        _elipse(ctx, cx, cy, rx, ry)
        ctx.clip()
        ctx.rectangle(cx - rx, cy - ry, 2 * rx, ry * 0.55)
        ctx.set_source_rgba(*_cor(P["pele_sombra"]))
        ctx.fill()
        ctx.restore()
        ctx.new_path()
        ctx.move_to(cx - rx - 2, cy - ry * 0.4)
        ctx.curve_to(cx - rx * 0.4, cy - ry * 0.55, cx + rx * 0.4, cy - ry * 0.55, cx + rx + 2, cy - ry * 0.4)
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(6)
        ctx.stroke()


def _boca(ctx, x, y, humor, fala):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if fala > 0.08 or humor == "susto":
        h = 12 + 30 * min(1.0, fala) if fala > 0.08 else 24
        w = 36 if humor != "susto" else 20

        def contorno_boca():
            ctx.new_path()
            ctx.move_to(x - w, y - 4)
            ctx.curve_to(x - w * 0.6, y - 9, x + w * 0.6, y - 9, x + w, y - 4)
            ctx.curve_to(x + w * 0.9, y + h, x - w * 0.9, y + h, x - w, y - 4)
            ctx.close_path()
        contorno_boca()
        ctx.set_source_rgba(0.40, 0.10, 0.12, 1)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        _elipse(ctx, x, y + h * 0.85, w * 0.6, h * 0.45)
        ctx.set_source_rgba(0.92, 0.45, 0.48, 1)
        ctx.fill()
        ctx.rectangle(x - w, y - 12, w * 2, 11)
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill()
        ctx.restore()
        contorno_boca()
        ctx.set_source_rgba(*_cor(CONTORNO))
        ctx.set_line_width(5)
        ctx.stroke()
        return
    ctx.new_path()
    if humor == "triste":
        ctx.move_to(x - 28, y + 10)
        ctx.curve_to(x - 10, y - 6, x + 10, y - 6, x + 28, y + 10)
    elif humor == "sem_graca":
        ctx.move_to(x - 28, y + 3)
        ctx.curve_to(x - 10, y + 10, x + 6, y - 6, x + 28, y)
    else:
        ctx.move_to(x - 34, y - 4)
        ctx.curve_to(x - 14, y + 20, x + 14, y + 20, x + 34, y - 4)
    ctx.set_source_rgba(*_cor(CONTORNO))
    ctx.set_line_width(7)
    ctx.stroke()


def desenha(ctx, x, y, s=1.0, humor="normal", fala=0.0, t=0.0, braco_e=0.2, braco_d=0.2, dobra_e=0.1,
            dobra_d=0.1, aceno=False, olhar=(0, 0), pulo=0.0, paleta=None, barba=True, bigode=True):
    P = dict(PALETA, **(paleta or {}))
    ctx.save()
    # sombra no chão
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s * 0.18)
    g = cairo.RadialGradient(0, 0, 10, 0, 0, 220)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.35 / (1 + pulo / 150))
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    ctx.arc(0, 0, 220, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    ctx.translate(x, y - pulo)
    ctx.scale(s, s)

    # --- pernas (calça)
    for lado in (-1, 1):
        _tubo(ctx, [(lado * 55, QUADRIL), (lado * 62, -60)], 96, P["calca"], P["calca_sombra"])
        ctx.new_path()
        ctx.move_to(lado * 62 - 34, -200)
        ctx.line_to(lado * 62 - 30, -80)
        ctx.set_source_rgba(1, 0.85, 0.5, 0.5)
        ctx.set_line_width(3)
        ctx.set_dash([8, 6])
        ctx.stroke()
        ctx.set_dash([])
    # --- sapatos (sociais pretos, apontando pra fora)
    for lado in (-1, 1):
        ctx.save()
        ctx.translate(lado * 68, 0)
        ctx.scale(lado, 1)
        ctx.new_path()
        ctx.move_to(-46, -8)
        ctx.curve_to(-50, -54, -18, -74, 10, -72)
        ctx.curve_to(50, -66, 82, -40, 84, -12)
        ctx.line_to(84, 0)
        ctx.line_to(-46, 0)
        ctx.close_path()
        _preenche(ctx, _grad_lin(0, -74, 0, 0, P["sapato"], P["sapato_sombra"]), 6)
        ctx.rectangle(-48, -12, 134, 14)
        ctx.set_source_rgba(0.25, 0.25, 0.27, 1)
        ctx.fill()
        _elipse(ctx, 18, -54, 26, 8, -0.12)
        ctx.set_source_rgba(1, 1, 1, 0.45)
        ctx.fill()
        ctx.restore()
    # --- tronco (camiseta)
    oy = OMBRO_Y
    ctx.new_path()
    ctx.move_to(-OMBRO_X - 8, oy + 15)
    ctx.curve_to(-70, oy - 25, 70, oy - 25, OMBRO_X + 8, oy + 15)
    ctx.curve_to(OMBRO_X + 10, oy + 150, 125, QUADRIL - 120, 120, QUADRIL - 10)
    ctx.curve_to(40, QUADRIL + 6, -40, QUADRIL + 6, -120, QUADRIL - 10)
    ctx.curve_to(-125, QUADRIL - 120, -OMBRO_X - 10, oy + 150, -OMBRO_X - 8, oy + 15)
    ctx.close_path()
    _preenche(ctx, _grad_lin(-140, oy - 20, 150, QUADRIL, P["camiseta"], P["camiseta_sombra"]), 7)
    ctx.set_source_rgba(0, 0, 0, 0.16)
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for (a, b, c, d) in [(-90, -700, -45, -680), (70, -760, 100, -720), (-15, -610, 30, -600),
                         (-60, -820, -20, -800)]:
        ctx.move_to(a, b)
        ctx.line_to(c, d)
        ctx.stroke()
    ctx.move_to(-118, QUADRIL - 26)
    ctx.curve_to(-40, QUADRIL - 12, 40, QUADRIL - 12, 118, QUADRIL - 26)
    ctx.set_source_rgba(0, 0, 0, 0.2)
    ctx.stroke()

    # --- braços
    _braco(ctx, -1, braco_e, dobra_e, P)
    _braco(ctx, 1, braco_d, dobra_d, P, onda=1.0 if aceno else 0.0, t=t)

    # --- pescoço + gola
    _tubo(ctx, [(0, oy - 5), (0, CAB_Y + CAB_RY - 40)], 84, P["pele"], P["pele_sombra"], brilho=False)
    ctx.new_path()
    ctx.move_to(-52, oy - 12)
    ctx.curve_to(-30, oy + 30, 30, oy + 30, 52, oy - 12)
    ctx.set_source_rgba(*_cor(P["camiseta_sombra"]))
    ctx.set_line_width(14)
    ctx.stroke()

    # --- cabeça
    hx, hy, rx, ry = 0, CAB_Y, CAB_RX, CAB_RY
    for lado in (-1, 1):
        _elipse(ctx, lado * (rx - 2), hy + 8, 22, 30)
        _preenche(ctx, _grad_rad(lado * rx, hy + 8, 28, P["pele"], P["pele_sombra"]))
        _elipse(ctx, lado * (rx - 2), hy + 8, 10, 16)
        ctx.set_source_rgba(*_cor(P["pele_sombra"], 0.7))
        ctx.fill()
    # rosto: arredondado com mandíbula de adulto
    def rosto():
        ctx.new_path()
        ctx.move_to(-rx, hy - 20)
        ctx.curve_to(-rx, hy - ry - 10, rx, hy - ry - 10, rx, hy - 20)
        ctx.curve_to(rx, hy + 60, rx * 0.55, hy + ry, 0, hy + ry + 4)
        ctx.curve_to(-rx * 0.55, hy + ry, -rx, hy + 60, -rx, hy - 20)
        ctx.close_path()
    rosto()
    _preenche(ctx, _grad_rad(hx, hy, ry, P["pele"], P["pele_sombra"]), 7)
    # barba por fazer
    if barba:
        ctx.save()
        rosto()
        ctx.clip()
        g = cairo.LinearGradient(0, hy + 20, 0, hy + 70)
        g.add_color_stop_rgba(0, *_cor(P["cabelo"], 0))
        g.add_color_stop_rgba(1, *_cor(P["cabelo"], 0.28))
        ctx.set_source(g)
        ctx.rectangle(-rx, hy + 20, 2 * rx, ry + 20)
        ctx.fill()
        ctx.restore()
    # costeletas
    for lado in (-1, 1):
        ctx.new_path()
        ctx.move_to(lado * (rx - 2), hy - 96)
        ctx.curve_to(lado * (rx + 4), hy - 30, lado * rx, hy, lado * (rx - 8), hy + 14)
        ctx.line_to(lado * (rx - 22), hy - 60)
        ctx.close_path()
        _preenche(ctx, P["cabelo"], 4)
    # olhos
    piscando = _pisca(t)
    ey = hy - 12
    if humor == "piscadinha":
        _olho(ctx, -42, ey, "normal", False, olhar, P)
        _olho(ctx, 42, ey, "feliz", False, olhar, P)
    else:
        for lado in (-1, 1):
            _olho(ctx, lado * 42, ey, humor, piscando, olhar, P)
    # sobrancelhas grossas
    for lado in (-1, 1):
        sob = {"susto": -14, "triste": 4, "bravo": 6}.get(humor, 0)
        incl = {"triste": -10, "bravo": 12}.get(humor, 0)
        ctx.new_path()
        ctx.move_to(lado * 18, ey - 36 + sob + incl)
        ctx.curve_to(lado * 34, ey - 46 + sob, lado * 52, ey - 46 + sob, lado * 68, ey - 38 + sob - incl * 0.3)
        ctx.set_source_rgba(*_cor(P["cabelo"]))
        ctx.set_line_width(13)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    # nariz
    ctx.new_path()
    ctx.move_to(hx + 2, ey + 6)
    ctx.curve_to(hx + 6, ey + 30, hx + 18, ey + 42, hx + 4, ey + 50)
    ctx.set_source_rgba(*_cor(P["pele_sombra"]))
    ctx.set_line_width(6)
    ctx.stroke()
    _boca(ctx, hx, hy + 84, "feliz" if humor in ("normal", "piscadinha") else humor, fala)

    # --- bigode
    if bigode:
        my = hy + 50
        ctx.new_path()
        ctx.move_to(0, my - 6)
        ctx.curve_to(-18, my - 16, -44, my - 14, -58, my + 4)
        ctx.curve_to(-62, my + 14, -54, my + 22, -44, my + 14)
        ctx.curve_to(-30, my + 6, -12, my + 8, 0, my + 4)
        ctx.curve_to(12, my + 8, 30, my + 6, 44, my + 14)
        ctx.curve_to(54, my + 22, 62, my + 14, 58, my + 4)
        ctx.curve_to(44, my - 14, 18, my - 16, 0, my - 6)
        ctx.close_path()
        _preenche(ctx, _grad_lin(0, my - 16, 0, my + 20, tuple(min(1, v * 1.5) for v in P["cabelo"]),
                                 tuple(v * 0.6 for v in P["cabelo"])), 5)
        ctx.new_path()
        ctx.move_to(-40, my - 6)
        ctx.curve_to(-26, my - 10, -14, my - 9, -6, my - 4)
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.set_line_width(3)
        ctx.stroke()

    # --- boné virado pra trás
    cy0 = hy - 98
    r = rx
    # aba saindo por trás da cabeça (lado esquerdo, meio caída)
    ctx.new_path()
    ctx.move_to(-r * 0.4, cy0 - 30)
    ctx.curve_to(-r - 40, cy0 - 40, -r - 95, cy0 - 5, -r - 92, cy0 + 22)
    ctx.curve_to(-r - 70, cy0 + 30, -r - 20, cy0 + 10, -r * 0.4, cy0 + 4)
    ctx.close_path()
    _preenche(ctx, _grad_lin(-r - 90, cy0 - 30, -r, cy0 + 25, P["bone"], P["bone_sombra"]), 7)
    # franjinha de cabelo aparecendo na testa
    ctx.new_path()
    ctx.move_to(-r + 6, cy0 + 4)
    ctx.curve_to(-60, cy0 + 26, 60, cy0 + 26, r - 6, cy0 + 4)
    ctx.line_to(r - 6, cy0 - 6)
    ctx.line_to(-r + 6, cy0 - 6)
    ctx.close_path()
    _preenche(ctx, P["cabelo"], 5)
    # copa
    ctx.new_path()
    ctx.move_to(-r - 8, cy0)
    ctx.curve_to(-r - 6, hy - 243, r + 6, hy - 243, r + 8, cy0)
    ctx.curve_to(r * 0.5, cy0 + 10, -r * 0.5, cy0 + 10, -r - 8, cy0)
    ctx.close_path()
    _preenche(ctx, _grad_rad(hx - 8, hy - 136, 150, P["bone"], P["bone_sombra"], -0.3, -0.5), 7)
    ctx.set_source_rgba(*_cor(P["bone_sombra"]))
    ctx.set_line_width(4)
    topo = hy - 190
    for cx in (-55, 55):
        ctx.new_path()
        ctx.move_to(cx * 0.08, topo + 4)
        ctx.curve_to(cx * 0.8, topo + 40, cx * 1.1, topo + 70, cx * 1.15, cy0 + 6)
        ctx.stroke()
    _elipse(ctx, 0, topo + 2, 13, 7)
    _preenche(ctx, P["bone_sombra"], 4)
    # abertura de trás (snapback) agora na frente: arco mostrando o cabelo + tira de ajuste
    ctx.new_path()
    ctx.move_to(-42, cy0 + 9)
    ctx.curve_to(-40, cy0 - 50, 40, cy0 - 50, 42, cy0 + 9)
    ctx.close_path()
    _preenche(ctx, _grad_lin(0, cy0 - 45, 0, cy0 + 10, tuple(v * 0.7 for v in P["cabelo"]), P["cabelo"]), 6)
    ctx.rectangle(-52, cy0 - 14, 104, 16)
    _preenche(ctx, _grad_lin(0, cy0 - 14, 0, cy0 + 2, P["bone"], P["bone_sombra"]), 4)
    for k in range(5):
        _circulo(ctx, -32 + k * 16, cy0 - 6, 3.2)
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.fill()
    _elipse(ctx, -60, hy - 150, 30, 12, -0.5)
    ctx.set_source_rgba(1, 1, 1, 0.3)
    ctx.fill()
    ctx.restore()
