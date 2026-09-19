"""Arte pixel art procedural del modo plataformas.

Todo se dibuja por codigo: heroes con poses reales, enemigos con silueta
propia, tiles con textura, props y fondos por capas para el parallax.
No se usan figuras geometricas "planas" como resultado final: cada sprite
lleva sombreado, contorno y detalles.
"""
import math
import random

import pygame

from . import settings as S
from .sprites import grid, outline, shade

# ---------------------------------------------------------------- paletas
HERO_PALETTES = {
    "flora": {           # personaje femenino
        "skin": (247, 206, 170), "skin_d": (214, 166, 134),
        "hair": (126, 70, 48), "hair_d": (86, 46, 34), "hair_l": (168, 104, 68),
        "cloth": (255, 206, 82), "cloth_d": (214, 148, 46),
        "pants": (94, 132, 196), "pants_d": (60, 92, 150),
        "shoe": (96, 62, 48), "shoe_d": (62, 40, 32),
        "accent": (255, 240, 160),
    },
    "sol": {             # personaje masculino
        "skin": (232, 184, 142), "skin_d": (196, 148, 112),
        "hair": (62, 48, 44), "hair_d": (38, 30, 30), "hair_l": (96, 74, 62),
        "cloth": (118, 196, 148), "cloth_d": (72, 142, 108),
        "pants": (92, 84, 128), "pants_d": (62, 54, 94),
        "shoe": (86, 62, 52), "shoe_d": (56, 40, 34),
        "accent": (255, 226, 120),
    },
    "dama": {            # destinataria
        "skin": (243, 198, 166), "skin_d": (208, 160, 130),
        "hair": (46, 38, 40), "hair_d": (28, 24, 28), "hair_l": (86, 68, 66),
        "cloth": (248, 158, 180), "cloth_d": (204, 106, 136),
        "pants": (214, 128, 154), "pants_d": (168, 92, 118),
        "shoe": (92, 62, 62), "shoe_d": (58, 40, 42),
        "accent": (255, 236, 180),
    },
    "caballero": {       # destinatario
        "skin": (226, 178, 138), "skin_d": (188, 142, 108),
        "hair": (138, 94, 56), "hair_d": (96, 62, 38), "hair_l": (178, 130, 82),
        "cloth": (146, 168, 234), "cloth_d": (98, 118, 186),
        "pants": (84, 92, 118), "pants_d": (56, 62, 86),
        "shoe": (78, 58, 48), "shoe_d": (50, 36, 30),
        "accent": (255, 236, 180),
    },
    "npc_jardinero": {
        "skin": (222, 176, 136), "skin_d": (184, 140, 106),
        "hair": (188, 186, 180), "hair_d": (140, 138, 134), "hair_l": (218, 216, 210),
        "cloth": (146, 174, 108), "cloth_d": (100, 128, 72),
        "pants": (122, 96, 72), "pants_d": (86, 66, 50),
        "shoe": (74, 56, 44), "shoe_d": (50, 36, 30),
        "accent": (255, 226, 120),
    },
    "npc_misterioso": {
        "skin": (206, 178, 190), "skin_d": (168, 142, 158),
        "hair": (96, 70, 140), "hair_d": (64, 44, 104), "hair_l": (140, 110, 190),
        "cloth": (88, 72, 132), "cloth_d": (58, 46, 96),
        "pants": (66, 54, 100), "pants_d": (44, 36, 72),
        "shoe": (52, 42, 68), "shoe_d": (34, 28, 48),
        "accent": (196, 168, 255),
    },
    "npc_gracioso": {
        "skin": (238, 192, 150), "skin_d": (200, 154, 118),
        "hair": (226, 132, 66), "hair_d": (176, 92, 44), "hair_l": (250, 176, 96),
        "cloth": (238, 122, 108), "cloth_d": (186, 82, 76),
        "pants": (108, 118, 142), "pants_d": (74, 82, 104),
        "shoe": (72, 54, 48), "shoe_d": (48, 34, 30),
        "accent": (255, 214, 120),
    },
}

HERO_W, HERO_H = 20, 26


# ------------------------------------------------------------ helpers
def _r(s, x, y, w, h, c):
    if w > 0 and h > 0:
        pygame.draw.rect(s, c, (int(x), int(y), int(w), int(h)))


def _leg(s, pal, x, top, h, foot_dx=0):
    _r(s, x, top, 3, h, pal["pants"])
    _r(s, x, top, 1, h, pal["pants_d"])
    _r(s, x - 1 + foot_dx, top + h, 4, 2, pal["shoe"])
    _r(s, x - 1 + foot_dx, top + h + 1, 4, 1, pal["shoe_d"])


def _arm(s, pal, x, top, h, hand=True):
    _r(s, x, top, 2, h, pal["cloth_d"])
    if hand:
        _r(s, x, top + h, 2, 2, pal["skin"])


def _arm_h(s, pal, x, y, w, flip=False):
    """Brazo horizontal (ataque / lanzamiento)."""
    _r(s, x, y, w, 2, pal["cloth_d"])
    hx = x + w if not flip else x - 2
    _r(s, hx, y, 2, 2, pal["skin"])


def _head(s, pal, x, y, female, eyes="open", mouth="smile"):
    # cara
    _r(s, x, y, 8, 8, pal["skin"])
    _r(s, x + 6, y + 1, 2, 7, pal["skin_d"])
    # cabello
    _r(s, x - 1, y - 2, 10, 4, pal["hair"])
    _r(s, x - 1, y - 2, 10, 1, pal["hair_l"])
    _r(s, x - 1, y + 1, 2, 4, pal["hair"])
    _r(s, x + 7, y + 1, 2, 4, pal["hair"])
    if female:
        _r(s, x - 2, y, 2, 12, pal["hair"])
        _r(s, x + 8, y, 2, 12, pal["hair"])
        _r(s, x - 2, y + 10, 2, 2, pal["hair_d"])
        _r(s, x + 8, y + 10, 2, 2, pal["hair_d"])
        # florecita en el pelo
        _r(s, x + 7, y - 3, 3, 3, S.YELLOW)
        _r(s, x + 8, y - 2, 1, 1, S.ORANGE)
    else:
        _r(s, x + 1, y + 1, 6, 1, pal["hair_d"])
    # ojos
    if eyes == "closed":
        _r(s, x + 1, y + 4, 2, 1, S.DARK)
        _r(s, x + 5, y + 4, 2, 1, S.DARK)
    elif eyes == "x":
        _r(s, x + 1, y + 3, 2, 2, S.DARK)
        _r(s, x + 5, y + 3, 2, 2, S.DARK)
    else:
        _r(s, x + 1, y + 3, 2, 2, S.DARK)
        _r(s, x + 5, y + 3, 2, 2, S.DARK)
        _r(s, x + 2, y + 3, 1, 1, S.WHITE)
        _r(s, x + 6, y + 3, 1, 1, S.WHITE)
    # rubor y boca
    _r(s, x, y + 5, 1, 1, (244, 156, 156))
    _r(s, x + 7, y + 5, 1, 1, (228, 140, 140))
    if mouth == "smile":
        _r(s, x + 3, y + 6, 2, 1, (168, 92, 84))
    elif mouth == "open":
        _r(s, x + 3, y + 5, 2, 2, (150, 74, 70))


def _torso(s, pal, x, y, female):
    _r(s, x, y, 8, 7, pal["cloth"])
    _r(s, x + 6, y, 2, 7, pal["cloth_d"])
    _r(s, x, y, 8, 1, shade(pal["cloth"], 26))
    if female:
        _r(s, x - 1, y + 5, 10, 2, pal["cloth"])
        _r(s, x - 1, y + 6, 10, 1, pal["cloth_d"])
    _r(s, x + 3, y + 2, 2, 2, pal["accent"])


def hero_frame(pal, female, legs="stand", arms="down", body_dy=0, lean=0,
               eyes="open", mouth="smile", crouch=False):
    s = pygame.Surface((HERO_W, HERO_H), pygame.SRCALPHA)
    bx = 6 + lean
    if crouch:
        _head(s, pal, bx, 8, female, eyes, mouth)
        _torso(s, pal, 6, 16, female)
        _leg(s, pal, 7, 22, 2)
        _leg(s, pal, 11, 22, 2)
        _arm(s, pal, 4, 17, 4)
        _arm(s, pal, 14, 17, 4)
        return outline(s)

    ty = 11 + body_dy
    hy = 3 + body_dy

    # piernas
    if legs == "stand":
        _leg(s, pal, 7, ty + 7, 5)
        _leg(s, pal, 11, ty + 7, 5)
    elif legs == "walkA":
        _leg(s, pal, 6, ty + 7, 5, -1)
        _leg(s, pal, 12, ty + 7, 4, 1)
    elif legs == "walkB":
        _leg(s, pal, 8, ty + 7, 5)
        _leg(s, pal, 11, ty + 7, 5)
    elif legs == "walkC":
        _leg(s, pal, 12, ty + 7, 5, 1)
        _leg(s, pal, 6, ty + 7, 4, -1)
    elif legs == "tuck":
        _leg(s, pal, 7, ty + 6, 4, -1)
        _leg(s, pal, 11, ty + 7, 3, 1)
    elif legs == "spread":
        _leg(s, pal, 5, ty + 7, 4, -1)
        _leg(s, pal, 13, ty + 7, 4, 1)
    elif legs == "bend":
        _leg(s, pal, 6, ty + 8, 3, -1)
        _leg(s, pal, 12, ty + 8, 3, 1)
    else:
        _leg(s, pal, 7, ty + 7, 5)
        _leg(s, pal, 11, ty + 7, 5)

    _torso(s, pal, 6, ty, female)
    _head(s, pal, bx, hy, female, eyes, mouth)

    # brazos
    if arms == "down":
        _arm(s, pal, 4, ty + 1, 5)
        _arm(s, pal, 14, ty + 1, 5)
    elif arms == "swingA":
        _arm(s, pal, 3, ty + 2, 4)
        _arm(s, pal, 15, ty, 4)
    elif arms == "swingB":
        _arm(s, pal, 4, ty, 4)
        _arm(s, pal, 14, ty + 2, 4)
    elif arms == "up":
        _arm_h(s, pal, 15, ty - 2, 3)
        _arm_h(s, pal, 2, ty - 1, 3, True)
    elif arms == "out":
        _arm_h(s, pal, 15, ty + 1, 4)
        _arm_h(s, pal, 1, ty + 1, 4, True)
    elif arms == "attack0":
        _arm(s, pal, 4, ty + 1, 5)
        _arm_h(s, pal, 14, ty - 1, 3)
    elif arms == "attack1":
        _arm(s, pal, 4, ty + 2, 4)
        _arm_h(s, pal, 14, ty + 3, 5)
    elif arms == "throw0":
        _arm(s, pal, 4, ty + 1, 5)
        _arm_h(s, pal, 13, ty - 2, 3)
    elif arms == "throw1":
        _arm(s, pal, 4, ty + 2, 4)
        _arm_h(s, pal, 14, ty + 1, 5)
    elif arms == "cheer":
        _arm(s, pal, 3, ty - 4, 5, False)
        _r(s, 3, ty - 5, 2, 2, pal["skin"])
        _arm(s, pal, 15, ty - 4, 5, False)
        _r(s, 15, ty - 5, 2, 2, pal["skin"])
    return outline(s)


def hero_frames(key, female):
    """Devuelve el diccionario completo de animaciones del heroe."""
    pal = HERO_PALETTES[key]
    f = lambda **kw: hero_frame(pal, female, **kw)
    frames = {
        "idle": [f(legs="stand", arms="down"),
                 f(legs="stand", arms="down", body_dy=1),
                 f(legs="stand", arms="down"),
                 f(legs="stand", arms="down", body_dy=1, eyes="closed")],
        "walk": [f(legs="walkA", arms="swingA"),
                 f(legs="walkB", arms="down", body_dy=-1),
                 f(legs="walkC", arms="swingB"),
                 f(legs="walkB", arms="down", body_dy=-1)],
        "run": [f(legs="walkA", arms="swingA", lean=1, body_dy=-1),
                f(legs="walkB", arms="swingB", lean=1),
                f(legs="walkC", arms="swingA", lean=1, body_dy=-1),
                f(legs="walkB", arms="swingB", lean=1)],
        "jump": [f(legs="tuck", arms="up", body_dy=-1)],
        "fall": [f(legs="spread", arms="out"), f(legs="spread", arms="out", body_dy=1)],
        "land": [f(legs="bend", arms="out", body_dy=2)],
        "crouch": [f(crouch=True), f(crouch=True, eyes="closed")],
        "attack": [f(legs="stand", arms="attack0", mouth="open"),
                   f(legs="bend", arms="attack1", mouth="open", body_dy=1)],
        "throw": [f(legs="stand", arms="throw0", mouth="open"),
                  f(legs="walkB", arms="throw1", mouth="open")],
        "hurt": [f(legs="spread", arms="out", eyes="x", mouth="open", lean=-1)],
        "dead": [f(legs="bend", arms="out", eyes="x", mouth="open", body_dy=3)],
        "celebrate": [f(legs="stand", arms="cheer", mouth="open"),
                      f(legs="bend", arms="cheer", mouth="open", body_dy=-2)],
    }
    return frames


# ------------------------------------------------------------- enemigos
def _eye(s, x, y, c=S.WHITE, p=S.DARK):
    _r(s, x, y, 3, 3, c)
    _r(s, x + 1, y + 1, 2, 2, p)


def enemy_petalillo(frame):
    s = pygame.Surface((18, 16), pygame.SRCALPHA)
    bob = frame % 2
    body = (255, 206, 92)
    for i, ang in enumerate(range(0, 360, 60)):
        a = math.radians(ang + frame * 8)
        px = 9 + math.cos(a) * 6
        py = 7 + bob + math.sin(a) * 5
        _r(s, px - 2, py - 2, 4, 4, S.YELLOW if i % 2 else body)
    pygame.draw.circle(s, (250, 178, 60), (9, 7 + bob), 5)
    pygame.draw.circle(s, (224, 142, 44), (9, 8 + bob), 4)
    _eye(s, 5, 5 + bob)
    _eye(s, 10, 5 + bob)
    _r(s, 8, 10 + bob, 2, 1, (140, 72, 40))
    _r(s, 5, 13 - bob, 2, 3, (188, 118, 58))
    _r(s, 11, 13 + bob, 2, 3, (188, 118, 58))
    return outline(s)


def enemy_saltarin(frame):
    s = pygame.Surface((18, 18), pygame.SRCALPHA)
    squash = 0 if frame == 0 else 2
    top = 3 + squash
    pygame.draw.ellipse(s, (198, 104, 150), (1, top, 16, 10))
    pygame.draw.ellipse(s, (240, 152, 190), (2, top + 1, 14, 6))
    _r(s, 3, top + 8, 12, 5 - squash, (120, 196, 148))
    _r(s, 3, top + 8, 12, 2, (160, 226, 176))
    _eye(s, 5, top + 4)
    _eye(s, 10, top + 4)
    _r(s, 4, 15, 3, 3 - squash, (86, 150, 110))
    _r(s, 11, 15, 3, 3 - squash, (86, 150, 110))
    return outline(s)


def enemy_perseguidor(frame):
    s = pygame.Surface((20, 18), pygame.SRCALPHA)
    wob = frame % 2
    pygame.draw.ellipse(s, (58, 46, 82), (2, 4 + wob, 16, 12))
    pygame.draw.ellipse(s, (88, 70, 122), (4, 5 + wob, 12, 8))
    for i in range(4):
        _r(s, 3 + i * 4, 2 + wob, 3, 4, (58, 46, 82))
    _eye(s, 6, 8 + wob, (255, 222, 120), (120, 60, 30))
    _eye(s, 11, 8 + wob, (255, 222, 120), (120, 60, 30))
    _r(s, 6, 14 + wob, 8, 2, (34, 26, 48))
    for i in range(3):
        _r(s, 4 + i * 5, 16, 2, 2, (44, 34, 64))
    return outline(s)


def enemy_volador(frame):
    s = pygame.Surface((22, 16), pygame.SRCALPHA)
    up = frame % 2
    wy = 3 if up else 7
    pygame.draw.polygon(s, (186, 226, 246), [(2, wy), (9, 8), (2, wy + 6)])
    pygame.draw.polygon(s, (186, 226, 246), [(20, wy), (13, 8), (20, wy + 6)])
    pygame.draw.polygon(s, (134, 190, 226), [(4, wy + 2), (9, 8), (4, wy + 5)])
    pygame.draw.ellipse(s, (226, 176, 92), (7, 5, 8, 10))
    pygame.draw.ellipse(s, (250, 210, 130), (8, 6, 5, 6))
    _eye(s, 8, 7)
    _r(s, 12, 8, 2, 2, S.DARK)
    return outline(s)


def enemy_lanzador(frame):
    s = pygame.Surface((20, 22), pygame.SRCALPHA)
    bob = frame % 2
    pygame.draw.ellipse(s, (120, 96, 176), (2, 4 + bob, 16, 14))
    pygame.draw.ellipse(s, (156, 132, 212), (4, 5 + bob, 11, 9))
    _r(s, 3, 2 + bob, 14, 3, (76, 58, 124))
    _r(s, 7, 0 + bob, 6, 3, (76, 58, 124))
    _eye(s, 5, 9 + bob, (255, 240, 180), (90, 40, 120))
    _eye(s, 11, 9 + bob, (255, 240, 180), (90, 40, 120))
    _r(s, 2, 12 + bob, 2, 3, (226, 186, 255))
    _r(s, 16, 12 + bob, 2, 3, (226, 186, 255))
    _r(s, 7, 18 + bob, 6, 3, (76, 58, 124))
    return outline(s)


def enemy_guardian(frame):
    s = pygame.Surface((40, 46), pygame.SRCALPHA)
    bob = frame % 2
    # tallo y cuerpo
    _r(s, 16, 20 + bob, 8, 22, (72, 140, 84))
    _r(s, 16, 20 + bob, 3, 22, (52, 108, 66))
    for i in range(3):
        _r(s, 10 - i, 28 + i * 5 + bob, 8, 3, (92, 166, 96))
        _r(s, 22 + i, 28 + i * 5 + bob, 8, 3, (92, 166, 96))
    # corona de petalos
    for ang in range(0, 360, 30):
        a = math.radians(ang + frame * 6)
        px = 20 + math.cos(a) * 13
        py = 16 + bob + math.sin(a) * 12
        _r(s, px - 3, py - 3, 6, 6, S.YELLOW if ang % 60 else S.GOLD)
    pygame.draw.circle(s, (206, 132, 56), (20, 16 + bob), 9)
    pygame.draw.circle(s, (164, 96, 44), (20, 17 + bob), 7)
    _eye(s, 14, 13 + bob, (255, 246, 200), (120, 50, 40))
    _eye(s, 22, 13 + bob, (255, 246, 200), (120, 50, 40))
    _r(s, 17, 20 + bob, 6, 2, (110, 46, 40))
    # brazos de vid
    _r(s, 4, 30 + bob, 12, 3, (72, 140, 84))
    _r(s, 24, 30 - bob, 12, 3, (72, 140, 84))
    return outline(s)


ENEMY_BUILDERS = {
    "petalillo": (enemy_petalillo, 3),
    "saltarin": (enemy_saltarin, 2),
    "perseguidor": (enemy_perseguidor, 2),
    "volador": (enemy_volador, 2),
    "lanzador": (enemy_lanzador, 2),
    "guardian": (enemy_guardian, 3),
}


# -------------------------------------------------------------- objetos
def flower_frames():
    frames = []
    for i in range(4):
        s = pygame.Surface((12, 14), pygame.SRCALPHA)
        dy = (0, -1, 0, 1)[i]
        _r(s, 5, 8 + dy, 2, 6, S.GREEN_D)
        _r(s, 2, 10 + dy, 3, 2, S.GREEN)
        for ang in range(0, 360, 60):
            a = math.radians(ang + i * 12)
            px = 6 + math.cos(a) * 3.4
            py = 5 + dy + math.sin(a) * 3.4
            _r(s, px - 2, py - 2, 4, 4, S.YELLOW)
        pygame.draw.circle(s, S.ORANGE, (6, 5 + dy), 2)
        _r(s, 5, 3 + dy, 1, 1, S.GOLD)
        frames.append(outline(s))
    return frames


def sunflower_frames():
    frames = []
    for i in range(4):
        s = pygame.Surface((22, 28), pygame.SRCALPHA)
        dy = (0, -1, -2, -1)[i]
        _r(s, 10, 14 + dy, 3, 14, S.GREEN_D)
        _r(s, 10, 14 + dy, 1, 14, S.GREEN_DD)
        _r(s, 4, 18 + dy, 6, 3, S.GREEN)
        _r(s, 13, 22 + dy, 6, 3, S.GREEN)
        for ang in range(0, 360, 24):
            a = math.radians(ang + i * 8)
            px = 11 + math.cos(a) * 8
            py = 10 + dy + math.sin(a) * 8
            _r(s, px - 2, py - 2, 5, 5, S.GOLD if ang % 48 else S.YELLOW)
        pygame.draw.circle(s, (188, 118, 48), (11, 10 + dy), 5)
        pygame.draw.circle(s, (146, 88, 38), (11, 11 + dy), 4)
        for p in ((9, 9), (12, 9), (10, 12)):
            _r(s, p[0], p[1] + dy, 1, 1, (232, 186, 96))
        frames.append(outline(s))
    return frames


def projectile_frames():
    frames = []
    for i in range(4):
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        for ang in range(0, 360, 72):
            a = math.radians(ang + i * 22)
            px = 5 + math.cos(a) * 3
            py = 5 + math.sin(a) * 3
            _r(s, px - 1, py - 1, 3, 3, S.GOLD)
        pygame.draw.circle(s, S.ORANGE, (5, 5), 2)
        frames.append(outline(s, (120, 84, 20)))
    return frames


def enemy_shot_frames():
    frames = []
    for i in range(3):
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(s, (180, 140, 255), (5, 5), 4 - (i % 2))
        pygame.draw.circle(s, (240, 220, 255), (4, 4), 2)
        frames.append(outline(s, (72, 48, 120)))
    return frames


def heart_icon(full=True):
    pal = {"o": (120, 38, 52), "r": S.HEART_RED, "l": (255, 168, 176),
           "e": (86, 78, 96), "d": (60, 54, 70)}
    rows_full = [
        ".oo.oo.",
        "olrorlo",
        "orrrrro",
        "orrrrro",
        ".orrro.",
        "..oro..",
        "...o...",
    ]
    rows_empty = [r.replace("r", "e").replace("l", "e") for r in rows_full]
    return grid(rows_full if full else rows_empty, pal)


def door_frames():
    frames = []
    for i in range(4):
        s = pygame.Surface((28, 40), pygame.SRCALPHA)
        glow = 18 + i * 6
        pygame.draw.ellipse(s, (255, 240, 170, 60), (0, 4, 28, 34))
        _r(s, 4, 6, 20, 34, (128, 90, 58))
        _r(s, 6, 8, 16, 30, (196, 152, 96))
        _r(s, 6, 8, 16, 2, (226, 196, 140))
        for ang in range(0, 360, 45):
            a = math.radians(ang + i * 10)
            px = 14 + math.cos(a) * (6 + i * 0.5)
            py = 22 + math.sin(a) * (8 + i * 0.5)
            _r(s, px - 1, py - 1, 3, 3, S.GOLD)
        pygame.draw.circle(s, (255, 236, 150), (14, 22), 4 + i % 2)
        _r(s, 2, 2, 24, 5, (98, 68, 46))
        _r(s, 2, 2, 24, 2, (150, 110, 74))
        frames.append(outline(s))
    return frames


def checkpoint_frames():
    frames = []
    for i in range(4):
        for on in (False, True):
            pass
    out = {"off": [], "on": []}
    for i in range(4):
        for state in ("off", "on"):
            s = pygame.Surface((18, 32), pygame.SRCALPHA)
            _r(s, 3, 4, 3, 28, (120, 96, 72))
            _r(s, 3, 4, 1, 28, (86, 68, 52))
            wave = math.sin(i * 1.5) * 1.5 if state == "on" else 0
            color = S.YELLOW if state == "on" else (150, 146, 152)
            color_d = S.YELLOW_D if state == "on" else (112, 108, 118)
            pygame.draw.polygon(s, color, [(6, 5), (16, 8 + wave), (6, 14)])
            pygame.draw.polygon(s, color_d, [(6, 10), (16, 8 + wave), (6, 14)])
            if state == "on":
                pygame.draw.circle(s, S.GOLD, (5, 3), 2)
            out[state].append(outline(s))
    return out


def ammo_icon():
    s = pygame.Surface((9, 9), pygame.SRCALPHA)
    for ang in range(0, 360, 72):
        a = math.radians(ang)
        _r(s, 4 + math.cos(a) * 3 - 1, 4 + math.sin(a) * 3 - 1, 3, 3, S.YELLOW)
    pygame.draw.circle(s, S.ORANGE, (4, 4), 1)
    return outline(s)


def bouquet():
    s = pygame.Surface((34, 40), pygame.SRCALPHA)
    pygame.draw.polygon(s, (128, 88, 56), [(12, 22), (22, 22), (20, 39), (14, 39)])
    pygame.draw.polygon(s, (170, 124, 82), [(14, 24), (17, 24), (16, 37), (15, 37)])
    fl = flower_frames()[0]
    for (x, y) in ((2, 6), (11, 0), (20, 5), (6, 14), (17, 14)):
        s.blit(fl, (x, y))
    return s


# ---------------------------------------------------------------- tiles
THEMES = {
    "campo": {"top": (126, 200, 96), "top_l": (168, 226, 124), "body": (150, 106, 68),
              "body_d": (110, 76, 50), "plat": S.WOOD, "plat_d": S.WOOD_D,
              "sky": ((120, 190, 236), (214, 240, 244)), "accent": S.YELLOW},
    "bosque": {"top": (94, 168, 92), "top_l": (128, 200, 110), "body": (108, 78, 56),
               "body_d": (74, 54, 40), "plat": (128, 96, 62), "plat_d": (86, 62, 44),
               "sky": ((74, 138, 160), (168, 206, 186)), "accent": (196, 236, 150)},
    "inverso": {"top": (150, 122, 196), "top_l": (188, 162, 226), "body": (92, 72, 128),
                "body_d": (62, 48, 92), "plat": (120, 98, 168), "plat_d": (80, 64, 120),
                "sky": ((92, 74, 140), (196, 158, 204)), "accent": (238, 186, 255)},
    "cielo": {"top": (156, 220, 236), "top_l": (200, 240, 248), "body": (128, 168, 208),
              "body_d": (92, 126, 168), "plat": S.CRYSTAL, "plat_d": S.CRYSTAL_D,
              "sky": ((104, 176, 236), (230, 246, 252)), "accent": (255, 250, 210)},
    "sueno": {"top": (172, 140, 230), "top_l": (208, 182, 250), "body": (86, 64, 136),
              "body_d": (58, 42, 98), "plat": (142, 112, 210), "plat_d": (96, 74, 156),
              "sky": ((40, 30, 78), (118, 78, 150)), "accent": (186, 240, 255)},
    "jardin": {"top": (140, 208, 108), "top_l": (180, 232, 132), "body": (156, 112, 72),
               "body_d": (114, 80, 54), "plat": (196, 158, 96), "plat_d": (142, 108, 68),
               "sky": ((250, 176, 112), (255, 232, 176)), "accent": S.GOLD},
}


def tile_ground_top(theme, rnd):
    t = THEMES[theme]
    s = pygame.Surface((S.TILE, S.TILE))
    s.fill(t["body"])
    for _ in range(14):
        x, y = rnd.randrange(16), rnd.randrange(5, 16)
        s.set_at((x, y), t["body_d"])
    _r(s, 0, 0, 16, 5, t["top"])
    _r(s, 0, 0, 16, 2, t["top_l"])
    for x in range(0, 16, 3):
        _r(s, x, 5, 2, rnd.randint(1, 3), t["top"])
    _r(s, 0, 15, 16, 1, t["body_d"])
    return s


def tile_ground_body(theme, rnd):
    t = THEMES[theme]
    s = pygame.Surface((S.TILE, S.TILE))
    s.fill(t["body"])
    for _ in range(18):
        x, y = rnd.randrange(16), rnd.randrange(16)
        s.set_at((x, y), t["body_d"])
    for _ in range(4):
        x, y = rnd.randrange(2, 13), rnd.randrange(2, 13)
        _r(s, x, y, 2, 2, shade(t["body"], 18))
    return s


def tile_platform(theme, rnd):
    t = THEMES[theme]
    s = pygame.Surface((S.TILE, S.TILE), pygame.SRCALPHA)
    _r(s, 0, 0, 16, 6, t["plat"])
    _r(s, 0, 0, 16, 2, shade(t["plat"], 30))
    _r(s, 0, 5, 16, 2, t["plat_d"])
    for x in range(1, 16, 5):
        _r(s, x, 2, 1, 3, t["plat_d"])
    return s


def tile_spike(theme):
    t = THEMES[theme]
    s = pygame.Surface((S.TILE, S.TILE), pygame.SRCALPHA)
    for i in range(4):
        x = i * 4
        pygame.draw.polygon(s, (218, 220, 230), [(x, 16), (x + 2, 5), (x + 4, 16)])
        pygame.draw.polygon(s, (150, 152, 170), [(x + 2, 5), (x + 4, 16), (x + 3, 16)])
    _r(s, 0, 14, 16, 2, t["body_d"])
    return s


def prop_tree(theme, rnd):
    t = THEMES[theme]
    s = pygame.Surface((46, 64), pygame.SRCALPHA)
    _r(s, 19, 34, 8, 30, t["body"])
    _r(s, 19, 34, 3, 30, t["body_d"])
    for cx, cy, r in ((23, 24, 17), (12, 30, 11), (34, 30, 11), (23, 14, 12)):
        pygame.draw.circle(s, shade(t["top"], -40), (cx, cy), r + 1)
        pygame.draw.circle(s, t["top"], (cx, cy), r)
        pygame.draw.circle(s, t["top_l"], (cx - 2, cy - 3), max(2, r - 5))
    for _ in range(22):
        x, y = rnd.randrange(4, 42), rnd.randrange(2, 42)
        if s.get_at((x, y))[3] > 0:
            s.set_at((x, y), t["accent"] if rnd.random() < 0.3 else t["top_l"])
    return s


def prop_bush(theme, rnd):
    t = THEMES[theme]
    s = pygame.Surface((26, 18), pygame.SRCALPHA)
    for cx, cy, r in ((8, 11, 7), (17, 11, 7), (13, 7, 7)):
        pygame.draw.circle(s, shade(t["top"], -40), (cx, cy), r + 1)
        pygame.draw.circle(s, t["top"], (cx, cy), r)
    for _ in range(6):
        x, y = rnd.randrange(3, 22), rnd.randrange(2, 13)
        if s.get_at((x, y))[3] > 0:
            s.set_at((x, y), t["top_l"])
    return s


def prop_deco_flower(rnd):
    s = pygame.Surface((9, 11), pygame.SRCALPHA)
    color = rnd.choice([S.YELLOW, S.CREAM, S.PINK, S.GOLD])
    _r(s, 4, 5, 1, 6, S.GREEN_D)
    _r(s, 1, 7, 3, 1, S.GREEN)
    for ang in range(0, 360, 72):
        a = math.radians(ang)
        _r(s, 4 + math.cos(a) * 2.6 - 1, 4 + math.sin(a) * 2.6 - 1, 3, 3, color)
    _r(s, 4, 4, 1, 1, S.ORANGE)
    return s


def prop_rock(theme, rnd):
    t = THEMES[theme]
    s = pygame.Surface((22, 16), pygame.SRCALPHA)
    pts = [(2, 15), (4, 7), (9, 3), (15, 4), (20, 9), (20, 15)]
    pygame.draw.polygon(s, shade(t["body_d"], -20), pts)
    pygame.draw.polygon(s, t["body"], [(p[0], p[1] + 1) for p in pts])
    pygame.draw.polygon(s, shade(t["body"], 28), [(7, 11), (9, 6), (13, 6), (14, 10)])
    return s


def prop_crystal(theme):
    s = pygame.Surface((16, 24), pygame.SRCALPHA)
    pygame.draw.polygon(s, S.CRYSTAL, [(8, 0), (14, 12), (8, 23), (2, 12)])
    pygame.draw.polygon(s, S.CRYSTAL_D, [(8, 0), (14, 12), (8, 23)])
    pygame.draw.polygon(s, (226, 248, 255), [(8, 3), (11, 12), (8, 18), (6, 12)])
    return outline(s)


# ------------------------------------------------------------- fondos
def _gradient(w, h, c1, c2):
    s = pygame.Surface((w, h))
    for y in range(h):
        k = y / max(1, h - 1)
        s.fill((int(c1[0] + (c2[0] - c1[0]) * k),
                int(c1[1] + (c2[1] - c1[1]) * k),
                int(c1[2] + (c2[2] - c1[2]) * k)), (0, y, w, 1))
    return s


def _clouds(w, h, color, rnd, n=8):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(n):
        cx, cy = rnd.randrange(w), rnd.randrange(10, max(12, h - 20))
        for dx, dy, r in ((0, 0, 10), (-9, 3, 7), (9, 3, 7), (-4, -4, 7), (5, -3, 6)):
            pygame.draw.circle(s, color, (cx + dx, cy + dy), r)
        pygame.draw.circle(s, shade(color, -14), (cx, cy + 6), 9)
    return s


def _hills(w, h, color, rnd, base, count=6, amp=40):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    step = w // count
    for i in range(count + 1):
        cx = i * step + rnd.randint(-10, 10)
        r = rnd.randint(amp, amp + 26)
        pygame.draw.circle(s, color, (cx, base), r)
    _r(s, 0, base, w, h - base, color)
    return s


def _far_trees(w, h, color, rnd, base):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    x = 0
    while x < w:
        th = rnd.randint(26, 46)
        pygame.draw.circle(s, color, (x + 8, base - th), rnd.randint(10, 15))
        _r(s, x + 6, base - th, 4, th, shade(color, -18))
        x += rnd.randint(14, 24)
    _r(s, 0, base, w, h - base, shade(color, -10))
    return s


def background_layers(theme, seed=7):
    """Capas de fondo con su factor de parallax."""
    rnd = random.Random(seed)
    W, H = 768, S.GAME_H
    t = THEMES[theme]
    layers = []
    sky = _gradient(W, H, *t["sky"])
    if theme == "sueno":
        pygame.draw.circle(sky, (248, 238, 196), (540, 56), 40)
        pygame.draw.circle(sky, (224, 210, 172), (532, 50), 34)
        for _ in range(70):
            sky.set_at((rnd.randrange(W), rnd.randrange(H // 2)), S.WHITE)
    elif theme == "cielo":
        pygame.draw.circle(sky, (255, 246, 196), (600, 40), 26)
    elif theme == "jardin":
        pygame.draw.circle(sky, (255, 232, 168), (560, 60), 46)
        pygame.draw.circle(sky, (255, 246, 208), (560, 60), 34)
    elif theme == "inverso":
        pygame.draw.circle(sky, (238, 226, 255), (180, 46), 22)
    layers.append({"surf": sky, "factor": 0.0, "y": 0})

    if theme in ("campo", "bosque", "jardin", "cielo"):
        layers.append({"surf": _clouds(W, H, (255, 255, 255, 150), rnd, 9),
                       "factor": 0.12, "y": 0})
    if theme in ("sueno", "inverso"):
        layers.append({"surf": _clouds(W, H, (200, 176, 255, 90), rnd, 7),
                       "factor": 0.12, "y": 0})

    hill_color = shade(t["top"], -60) + ()
    layers.append({"surf": _hills(W, H, (*shade(t["top"], -70), 210), rnd, H - 46),
                   "factor": 0.25, "y": 0})
    layers.append({"surf": _far_trees(W, H, (*shade(t["top"], -35), 235), rnd, H - 26),
                   "factor": 0.45, "y": 0})
    return layers


# ------------------------------------------------------------- cache
class PlatformArt:
    """Cachea todo el arte del modo plataformas."""

    def __init__(self):
        rnd = random.Random(21)
        self.heroes = {
            "flora": hero_frames("flora", True),
            "sol": hero_frames("sol", False),
        }
        self.targets = {
            "dama": hero_frames("dama", True),
            "caballero": hero_frames("caballero", False),
        }
        self.npcs = {k: hero_frames(k, k == "npc_misterioso")
                     for k in ("npc_jardinero", "npc_misterioso", "npc_gracioso")}
        self.enemies = {k: [fn(i) for i in range(n)]
                        for k, (fn, n) in ENEMY_BUILDERS.items()}
        self.flower = flower_frames()
        self.sunflower = sunflower_frames()
        self.projectile = projectile_frames()
        self.enemy_shot = enemy_shot_frames()
        self.heart_full = heart_icon(True)
        self.heart_empty = heart_icon(False)
        self.ammo = ammo_icon()
        self.door = door_frames()
        self.checkpoint = checkpoint_frames()
        self.bouquet = bouquet()
        self.crystal = prop_crystal("cielo")

        self.tiles = {}
        self.props = {}
        self.backgrounds = {}
        for theme in THEMES:
            r = random.Random(hash(theme) % 999)
            self.tiles[theme] = {
                "top": [tile_ground_top(theme, r) for _ in range(3)],
                "body": [tile_ground_body(theme, r) for _ in range(3)],
                "plat": tile_platform(theme, r),
                "spike": tile_spike(theme),
            }
            self.props[theme] = {
                "tree": [prop_tree(theme, r) for _ in range(2)],
                "bush": [prop_bush(theme, r) for _ in range(2)],
                "rock": [prop_rock(theme, r) for _ in range(2)],
                "flower": [prop_deco_flower(r) for _ in range(4)],
            }
            self.backgrounds[theme] = background_layers(theme)
