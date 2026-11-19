"""Roteiro de "A Cidade que Apaga às 6" em forma de linha do tempo.

Cada cena é uma lista de eventos, tocados em sequência:
  ("fala", quem, texto, id)      -> duração = duração do áudio gerado
  ("pausa", segundos, id, sfx)   -> ação sem fala (sfx opcional no início)
  ("sfx", nome)                  -> efeito sonoro no instante atual (duração zero)
"""

CENAS = [
    ("acordar", [
        ("pausa", 0.7, "sono", None),
        ("pausa", 1.1, "acorda", "alarme"),
        ("fala", "teo", "Ué... cadê as minhas paredes?", "ue"),
        ("pausa", 0.5, "fim", None),
    ]),
    ("titulo", [
        ("sfx", "rabisco"),
        ("fala", "narrador", "A cidade que apaga às seis.", "t"),
        ("pausa", 0.6, "fim", None),
    ]),
    ("cidade", [
        ("fala", "narrador", "Em Rabiscópolis, tudo é desenhado. Casas, árvores, pão... e até o bigode do prefeito.", "n1"),
        ("fala", "narrador", "E toda noite, todo mundo precisa desenhar a própria vida de novo.", "n2"),
    ]),
    ("borracha", [
        ("fala", "narrador", "Porque às seis da manhã, o sol passa pela cidade como uma borracha.", "n3"),
        ("fala", "narrador", "E o que ninguém desenhou... some.", "n4"),
        ("pausa", 0.9, "careca", "plim"),
        ("fala", "careca", "De novo não!", "grito"),
        ("pausa", 0.3, "fim", None),
    ]),
    ("explica", [
        ("fala", "teo", "Mas eu nunca desenhei nada na vida!", "t1"),
        ("fala", "teo", "Eu achava que a casa se desenhava sozinha!", "t2"),
    ]),
    ("vo", [
        ("pausa", 0.8, "chega", "passos"),
        ("fala", "vo", "Téo... faz onze anos que eu desenho a sua casa. Toda noite.", "v1"),
        ("fala", "vo", "Ontem, o meu lápis acabou.", "v2"),
        ("pausa", 1.0, "culpa", None),
        ("fala", "vo", "Hoje, quem desenha é você.", "v3"),
        ("pausa", 0.9, "lapis", "brilho"),
    ]),
    ("noite", [
        ("fala", "narrador", "Téo tinha uma noite pra desenhar a casa inteira.", "n5"),
        ("fala", "narrador", "Problema: ele desenha muito mal.", "n6"),
        ("pausa", 0.4, "fim", None),
    ]),
    ("porta", [
        ("pausa", 1.5, "desenha", "rabisco"),
        ("pausa", 0.9, "abre", "porta"),
        ("fala", "teo", "...Tá.", "ta"),
        ("pausa", 0.5, "fim", None),
    ]),
    ("cachorro", [
        ("pausa", 1.5, "desenha", "rabisco"),
        ("pausa", 0.4, "nasce", "pop"),
        ("fala", "rabisco", "Au?", "au"),
        ("pausa", 0.3, "x", None),
        ("fala", "teo", "Vou te chamar de Rabisco.", "nome"),
        ("pausa", 0.3, "fim", None),
    ]),
    ("privada", [
        ("pausa", 1.3, "desenha", "rabisco"),
        ("pausa", 0.6, "pernas", "boing"),
        ("pausa", 0.5, "foge", "corrida"),
        ("fala", "teo", "Ei! Volta aqui!", "grito"),
        ("pausa", 0.4, "fim", None),
    ]),
    ("nanquim", [
        ("fala", "nanquim", "Ha ha ha! Essa casa parece desenhada com o pé!", "riso"),
        ("pausa", 0.9, "pe", "plink"),
        ("fala", "teo", "Eu tava... testando uma técnica nova.", "tecnica"),
        ("pausa", 0.3, "fim", None),
    ]),
    ("relogio", [
        ("sfx", "tique"),
        ("fala", "narrador", "Cinco e cinquenta e oito. Só faltava o telhado.", "n7"),
        ("pausa", 0.7, "crack", "crack"),
        ("fala", "teo", "Não, não, não, não!", "nao"),
    ]),
    ("luz", [
        ("sfx", "zumbido"),
        ("fala", "narrador", "Faltava um minuto. Faltava um telhado. E o lápis tinha quebrado.", "n8"),
        ("pausa", 0.4, "fim", None),
    ]),
    ("vo_salva", [
        ("pausa", 0.7, "chega", "passos"),
        ("fala", "vo", "Esse aqui ainda tem uma linha. Só uma.", "v4"),
        ("pausa", 0.8, "maos", None),
    ]),
    ("telhado", [
        ("pausa", 2.8, "desenha", "rabisco_lento"),
        ("pausa", 1.6, "luz", "whoosh"),
        ("pausa", 0.9, "branco", None),
    ]),
    ("sobreviveu", [
        ("pausa", 1.2, "revela", "brilho"),
        ("fala", "rabisco", "Au!", "au"),
        ("pausa", 0.8, "plim", "plim"),
        ("fala", "teo", "Descansa em paz, privada.", "rip"),
        ("pausa", 0.4, "fim", None),
    ]),
    ("cueca", [
        ("pausa", 0.6, "entra", None),
        ("fala", "nanquim", "Esqueci de desenhar as minhas calças.", "calcas"),
        ("pausa", 1.0, "risada", "boing"),
    ]),
    ("final", [
        ("fala", "teo", "Vó... amanhã eu desenho a sua casa.", "t1"),
        ("pausa", 0.3, "x", None),
        ("fala", "vo", "Com o pé?", "v5"),
        ("fala", "teo", "Com a mão, vó!", "t2"),
        ("pausa", 0.8, "fim", None),
    ]),
    ("mao", [
        ("pausa", 1.4, "sobe", "whoosh"),
        ("fala", "narrador", "Mas... quem apaga a cidade?", "n9"),
        ("pausa", 3.2, "fim", "misterio"),
    ]),
]

# Legendas mais curtas/estilizadas quando o texto falado não serve na tela.
LEGENDA = {
    ("titulo", "t"): "",
}
