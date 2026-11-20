"""Gera mascote/ficha_mascote.png"""
import cairo, desenho as D, mascote as M
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, D.W, D.H); c = cairo.Context(s)
D.papel(c)
D.texto(c, "O MASCOTE", 540, 160, 110, fill=M.PALETA["bone"], stroke=(0.1, 0.1, 0.1), sw=20)
M.desenha(c, 540, 1230, 1.0, humor="normal", t=1.0, braco_d=2.5, dobra_d=0.5, braco_e=0.2)
poses = [("feliz", dict(humor="feliz", braco_e=2.4, braco_d=2.4, dobra_e=0.4, dobra_d=0.4)),
         ("piscadinha", dict(humor="piscadinha", braco_d=1.5, dobra_d=0.1)),
         ("susto", dict(humor="susto", braco_e=2.7, braco_d=2.7, dobra_e=0.6, dobra_d=0.6)),
         ("falando", dict(humor="normal", fala=0.8, braco_d=1.0, dobra_d=0.9))]
for i, (nome, kw) in enumerate(poses):
    x = 150 + i * 260
    M.desenha(c, x, 1720, 0.4, t=1.0, **kw)
    D.texto(c, nome, x, 1800, 48, "Patrick Hand", fill=(0.1, 0.1, 0.1))
s.write_to_png("../mascote/ficha_mascote.png")
