"""Generacion procedural de todo el pixel art del juego.

Todos los sprites se dibujan por codigo sobre superficies de Pygame,
usando rejillas de caracteres (pixel a pixel) o dibujo procedural.
Asi el juego comparte una unica identidad visual y no necesita
descargar ningun recurso externo.
"""
import random
import pygame

from . import settings as S


# ---------------------------------------------------------------- utilidades
def grid(rows, pal):
    """Convierte una rejilla de caracteres en una superficie pixel art."""
    w, h = len(rows[0]), len(rows)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            color = pal.get(ch)
            if color is not None:
                surf.set_at((x, y), color)
    return surf


def outline(surf, color=S.DARK):
    """Devuelve el sprite con un contorno de 1px (estilo pixel art)."""
    w, h = surf.get_size()
    out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surf)
    silhouette = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        out.blit(silhouette, (dx, dy))
    out.blit(surf, (1, 1))
    return out


def shade(color, amount):
    """Aclara (amount>0) u oscurece (amount<0) un color."""
    return tuple(max(0, min(255, c + amount)) for c in color[:3])


# ------------------------------------------------------------- personajes
BODY_DOWN = [
    "............",
    "...oooooo...",
    "..ohhhhhho..",
    ".ohhhhhhhho.",
    ".ohssssssho.",
    ".ohsessesho.",
    ".ohssssssho.",
    "..osssssso..",
    ".occcccccco.",
    ".osccccccso.",
    ".osccccccso.",
    ".osccccccso.",
    "..occcccco..",
    "..oppppppo..",
]
BODY_UP = [
    "............",
    "...oooooo...",
    "..ohhhhhho..",
    ".ohhhhhhhho.",
    ".ohhhhhhhho.",
    ".ohhhhhhhho.",
    ".ohhhhhhhho.",
    "..ohhhhhho..",
    ".occcccccco.",
    ".osccccccso.",
    ".osccccccso.",
    ".osccccccso.",
    "..occcccco..",
    "..oppppppo..",
]
BODY_SIDE = [
    "............",
    "...oooooo...",
    "..ohhhhhho..",
    ".ohhhhhhhho.",
    ".ohhhsssso..",
    ".ohhhseso...",
    ".ohhhsssso..",
    "..ohsssso...",
    ".occccccco..",
    ".oscccccso..",
    ".oscccccso..",
    ".oscccccso..",
    "..occccco...",
    "..oppppo....",
]

LEGS_FRONT = {
    "apart":    ("..opp..ppo..", "..obb..bbo.."),
    "together": ("...oppppo...", "...obbbbo..."),
    "wide":     (".opp....ppo.", ".obb....bbo."),
}
LEGS_SIDE = {
    "apart":    ("..opp.ppo...", "..obb.bbo..."),
    "together": ("..oppppo....", "..obbbbo...."),
    "wide":     (".opp..ppo...", ".obb..bbo..."),
}


def make_character(pal):
    """Devuelve {'down': [4 frames], 'up': [...], 'left': [...], 'right': [...]}."""
    def build(body, legs_table, step):
        rows = list(body) + list(legs_table[step])
        return grid(rows, pal)

    cycle = ["apart", "together", "apart", "wide"]
    frames = {}
    for name, body, table in (
        ("down", BODY_DOWN, LEGS_FRONT),
        ("up", BODY_UP, LEGS_FRONT),
        ("right", BODY_SIDE, LEGS_SIDE),
    ):
        frames[name] = [build(body, table, step) for step in cycle]
    frames["left"] = [pygame.transform.flip(f, True, False) for f in frames["right"]]
    return frames


def char_palette(skin, hair, cloth, pants, boots, eye=S.DARK):
    return {"o": S.DARK, "s": skin, "h": hair, "c": cloth,
            "p": pants, "b": boots, "e": eye}


SKIN_A = (246, 206, 168)
SKIN_B = (226, 178, 136)
SKIN_C = (186, 134, 100)

PLAYER_PAL = char_palette(SKIN_B, (92, 58, 44), (255, 214, 74), (86, 116, 178), (78, 56, 44))
NPC_PALETTES = {
    "tomas":  char_palette(SKIN_C, (58, 48, 46), (206, 106, 96), (74, 64, 88), (60, 48, 44)),
    "lucia":  char_palette(SKIN_A, (198, 136, 70), (248, 188, 198), (152, 108, 168), (86, 64, 56)),
    "rosa":   char_palette(SKIN_A, (214, 214, 220), (168, 202, 226), (96, 98, 122), (70, 62, 62)),
    "dalia":  char_palette(SKIN_B, (140, 88, 60), (158, 212, 104), (96, 122, 96), (72, 58, 48)),
    "mateo":  char_palette(SKIN_C, (44, 40, 52), (118, 158, 206), (72, 78, 96), (58, 50, 46)),
    "iris":   char_palette(SKIN_A, (120, 76, 140), (222, 142, 158), (104, 88, 132), (66, 56, 60)),
    "sol":    char_palette(SKIN_B, (74, 52, 46), (255, 244, 214), (240, 148, 66), (96, 72, 56)),
}


# ------------------------------------------------------------------ flores
def make_flower(petal, petal_d, center, stem=S.GREEN_D):
    pal = {"p": petal, "q": petal_d, "c": center, "g": stem,
           "l": S.GREEN, "o": S.GREEN_DD}
    rows = [
        "...ppp...",
        "..pppppq.",
        ".ppcccppq",
        ".ppcccppq",
        "..pqqqqq.",
        "...ppq...",
        "....g....",
        "..l.g....",
        "..ll g...",
        "....g....",
        "....g....",
    ]
    rows = [r.replace(" ", ".") for r in rows]
    return grid(rows, pal)


def flower_sway_frames(base):
    """Tres fotogramas de balanceo: desplaza la corola 1px a cada lado."""
    w, h = base.get_size()
    frames = []
    for dx in (0, 1, 0, -1):
        f = pygame.Surface((w + 2, h), pygame.SRCALPHA)
        top = base.subsurface(pygame.Rect(0, 0, w, 6)).copy()
        bottom = base.subsurface(pygame.Rect(0, 6, w, h - 6)).copy()
        f.blit(bottom, (1, 6))
        f.blit(top, (1 + dx, 0))
        frames.append(f)
    return frames


def make_golden_flower():
    base = make_flower(S.GOLD, S.YELLOW_D, S.ORANGE, S.GREEN_D)
    big = pygame.transform.scale(base, (base.get_width() + 4, base.get_height() + 4))
    return big


# ----------------------------------------------------------------- arboles
def make_tree(rnd, dark=False):
    w, h = 32, 40
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    leaf = S.GREEN_D if not dark else S.GREEN_NIGHT
    leaf_l = S.GREEN if not dark else S.GREEN_D
    leaf_ll = S.GREEN_L if not dark else S.GREEN
    # tronco
    pygame.draw.rect(surf, S.BROWN_D, (13, 24, 6, 15))
    pygame.draw.rect(surf, S.BROWN, (14, 24, 3, 15))
    pygame.draw.rect(surf, S.DARK, (12, 37, 8, 2))
    # copa por circulos agrupados
    blobs = [(16, 16, 13), (9, 20, 8), (23, 20, 8), (16, 10, 9), (10, 12, 7), (22, 12, 7)]
    for cx, cy, r in blobs:
        pygame.draw.circle(surf, S.DARK, (cx, cy), r + 1)
    for cx, cy, r in blobs:
        pygame.draw.circle(surf, leaf, (cx, cy), r)
    for cx, cy, r in blobs[:4]:
        pygame.draw.circle(surf, leaf_l, (cx - 1, cy - 2), max(2, r - 3))
    for _ in range(18):
        x = rnd.randint(5, 26)
        y = rnd.randint(4, 24)
        if surf.get_at((x, y))[3] > 0 and surf.get_at((x, y))[:3] != S.DARK:
            surf.set_at((x, y), leaf_ll)
    return surf


def make_pine(rnd):
    w, h = 26, 44
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, S.BROWN_D, (11, 34, 5, 9))
    for i, (cy, half) in enumerate(((12, 11), (20, 12), (28, 13))):
        pygame.draw.polygon(surf, S.DARK,
                            [(13, cy - 13), (13 - half - 1, cy + 4), (13 + half + 1, cy + 4)])
        pygame.draw.polygon(surf, S.GREEN_DD,
                            [(13, cy - 12), (13 - half, cy + 3), (13 + half, cy + 3)])
        pygame.draw.polygon(surf, S.GREEN_D,
                            [(13, cy - 10), (13 - half + 4, cy + 2), (13 + 2, cy + 2)])
    return surf


def make_bush(rnd, dark=False):
    surf = pygame.Surface((22, 16), pygame.SRCALPHA)
    leaf = S.GREEN_D if not dark else S.GREEN_NIGHT
    for cx, cy, r in ((7, 9, 6), (14, 9, 6), (11, 6, 6)):
        pygame.draw.circle(surf, S.DARK, (cx, cy), r + 1)
    for cx, cy, r in ((7, 9, 6), (14, 9, 6), (11, 6, 6)):
        pygame.draw.circle(surf, leaf, (cx, cy), r)
    for _ in range(8):
        x, y = rnd.randint(3, 18), rnd.randint(2, 11)
        if surf.get_at((x, y))[3] > 0:
            surf.set_at((x, y), S.GREEN)
    return surf


def make_rock(rnd):
    surf = pygame.Surface((20, 16), pygame.SRCALPHA)
    pts = [(2, 14), (4, 7), (8, 3), (13, 3), (17, 8), (18, 14)]
    pygame.draw.polygon(surf, S.DARK, pts)
    pygame.draw.polygon(surf, S.STONE_D, [(p[0], p[1] + 1) for p in pts])
    pygame.draw.polygon(surf, S.STONE, [(5, 12), (7, 6), (12, 5), (14, 9), (12, 12)])
    pygame.draw.polygon(surf, S.STONE_L, [(7, 9), (9, 6), (11, 7), (10, 10)])
    return surf


# --------------------------------------------------------------- edificios
def make_house(rnd, wall, roof):
    w, h = 64, 60
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body = pygame.Rect(6, 24, 52, 34)
    pygame.draw.rect(surf, S.DARK, body.inflate(2, 2))
    pygame.draw.rect(surf, wall, body)
    for y in range(body.top, body.bottom, 4):
        pygame.draw.line(surf, shade(wall, -12), (body.left, y), (body.right - 1, y))
    # tejado
    for i in range(14):
        pygame.draw.rect(surf, roof if i % 2 else shade(roof, -18),
                         (2 + i, 24 - i - 1, w - 4 - i * 2, 2))
    pygame.draw.polygon(surf, S.DARK, [(1, 24), (32, 8), (63, 24)], 1)
    # puerta
    door = pygame.Rect(26, 40, 12, 18)
    pygame.draw.rect(surf, S.BROWN_D, door)
    pygame.draw.rect(surf, S.BROWN, door.inflate(-2, -2))
    pygame.draw.rect(surf, S.DARK, door, 1)
    surf.set_at((35, 50), S.YELLOW)
    # ventanas
    for wx in (12, 44):
        win = pygame.Rect(wx, 32, 10, 10)
        pygame.draw.rect(surf, S.DARK, win.inflate(2, 2))
        pygame.draw.rect(surf, S.SKY, win)
        pygame.draw.rect(surf, S.CREAM, (wx, 32, 10, 3))
        pygame.draw.line(surf, S.DARK, (wx + 5, 32), (wx + 5, 41))
        pygame.draw.line(surf, S.DARK, (wx, 36), (wx + 9, 36))
    # chimenea
    pygame.draw.rect(surf, S.DARK, (46, 6, 8, 12))
    pygame.draw.rect(surf, S.BROWN, (47, 7, 6, 11))
    return surf


def make_fountain():
    surf = pygame.Surface((44, 36), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, S.DARK, (0, 10, 44, 26))
    pygame.draw.ellipse(surf, S.STONE, (1, 11, 42, 24))
    pygame.draw.ellipse(surf, S.STONE_D, (4, 14, 36, 18))
    pygame.draw.ellipse(surf, S.WATER, (6, 16, 32, 14))
    pygame.draw.ellipse(surf, S.WATER_L, (10, 18, 12, 5))
    pygame.draw.rect(surf, S.STONE_D, (20, 2, 4, 16))
    pygame.draw.rect(surf, S.STONE_L, (21, 2, 1, 16))
    pygame.draw.ellipse(surf, S.STONE, (14, 0, 16, 6))
    return surf


def make_bench():
    surf = pygame.Surface((26, 16), pygame.SRCALPHA)
    pygame.draw.rect(surf, S.DARK, (0, 3, 26, 4))
    pygame.draw.rect(surf, S.BROWN, (1, 4, 24, 2))
    pygame.draw.rect(surf, S.DARK, (0, 8, 26, 4))
    pygame.draw.rect(surf, S.BROWN_L, (1, 9, 24, 2))
    for x in (2, 21):
        pygame.draw.rect(surf, S.STONE_D, (x, 10, 3, 5))
    return surf


def make_lamp():
    surf = pygame.Surface((12, 34), pygame.SRCALPHA)
    pygame.draw.rect(surf, S.DARK, (5, 8, 3, 25))
    pygame.draw.rect(surf, S.STONE_D, (5, 8, 1, 25))
    pygame.draw.rect(surf, S.DARK, (2, 2, 8, 8))
    pygame.draw.rect(surf, S.YELLOW, (3, 3, 6, 6))
    pygame.draw.rect(surf, S.GOLD, (4, 4, 3, 3))
    pygame.draw.rect(surf, S.DARK, (3, 0, 6, 2))
    return surf


def make_sign():
    surf = pygame.Surface((18, 20), pygame.SRCALPHA)
    pygame.draw.rect(surf, S.BROWN_D, (7, 10, 4, 10))
    pygame.draw.rect(surf, S.DARK, (0, 2, 18, 10))
    pygame.draw.rect(surf, S.BROWN_L, (1, 3, 16, 8))
    for i in range(3):
        pygame.draw.line(surf, S.BROWN_D, (3, 5 + i * 2), (14, 5 + i * 2))
    return surf


def make_stall():
    surf = pygame.Surface((46, 40), pygame.SRCALPHA)
    pygame.draw.rect(surf, S.BROWN_D, (2, 22, 42, 16))
    pygame.draw.rect(surf, S.BROWN, (3, 23, 40, 14))
    for i in range(6):
        c = S.RED if i % 2 == 0 else S.CREAM
        pygame.draw.rect(surf, c, (2 + i * 7, 8, 7, 10))
    pygame.draw.rect(surf, S.DARK, (2, 6, 42, 3))
    pygame.draw.rect(surf, S.BROWN_D, (2, 18, 42, 3))
    for x in (4, 24, 38):
        pygame.draw.rect(surf, S.YELLOW, (x, 24, 5, 4))
    return surf


# -------------------------------------------------------------- criaturas
def make_butterfly(color):
    pal = {"o": S.DARK, "w": color, "l": shade(color, 40), "b": S.BROWN_D}
    open_f = [
        ".ow.wo.",
        "owwbwwo",
        "owlblwo",
        ".owbwo.",
        "..obo..",
    ]
    closed_f = [
        "..owo..",
        "..owo..",
        ".owbwo.",
        "..obo..",
        "..obo..",
    ]
    return [grid(open_f, pal), grid(closed_f, pal)]


def make_bird():
    pal = {"o": S.DARK, "b": (86, 92, 120), "w": S.WHITE, "y": S.YELLOW}
    a = ["..oo...", ".obbo..", "obwbbo.", ".obbbo.", "..ooo.."]
    b = [".......", "..oo...", "obbbbo.", ".obwbo.", "..ooo.."]
    return [grid(a, pal), grid(b, pal)]


def make_fish():
    pal = {"o": S.DARK, "f": S.ORANGE, "l": S.GOLD}
    a = [
        "..ooo..o",
        ".olffooo",
        "offffffo",
        ".olffooo",
        "..ooo..o",
    ]
    b = [
        "..ooo.oo",
        ".olffoo.",
        "offffffo",
        ".olffoo.",
        "..ooo.oo",
    ]
    return [grid(a, pal), grid(b, pal)]


def make_letter():
    pal = {"o": S.DARK, "c": S.CREAM, "d": S.CREAM_D, "r": S.RED}
    rows = [
        "oooooooooooo",
        "occccccccccо".replace("о", "o"),
        "odcccccccdco",
        "occdcccdccco",
        "occcdcdcccco",
        "occccrccccco",
        "occccccccdco",
        "oooooooooooo",
    ]
    return grid(rows, pal)


def make_basket():
    surf = pygame.Surface((30, 16), pygame.SRCALPHA)
    pygame.draw.arc(surf, S.BROWN_D, (2, -6, 26, 18), 3.34, 6.08, 2)
    pygame.draw.rect(surf, S.DARK, (0, 4, 30, 12))
    pygame.draw.rect(surf, S.BROWN, (1, 5, 28, 10))
    for x in range(3, 28, 4):
        pygame.draw.line(surf, S.BROWN_D, (x, 5), (x, 14))
    pygame.draw.line(surf, S.BROWN_L, (1, 8), (28, 8))
    return surf


def make_bouquet():
    surf = pygame.Surface((40, 44), pygame.SRCALPHA)
    pygame.draw.polygon(surf, S.BROWN_D, [(14, 24), (26, 24), (23, 43), (17, 43)])
    pygame.draw.polygon(surf, S.BROWN_L, [(16, 26), (20, 26), (19, 41), (17, 41)])
    small = make_flower(S.YELLOW, S.YELLOW_D, S.ORANGE)
    gold = make_flower(S.GOLD, S.YELLOW_D, S.ORANGE_D)
    spots = [(4, 8), (14, 2), (24, 7), (9, 16), (21, 16), (0, 2), (28, 0)]
    for i, (x, y) in enumerate(spots):
        surf.blit(gold if i == 1 else small, (x, y))
    return surf


def make_heart():
    pal = {"o": S.DARK, "r": (236, 96, 112), "l": (255, 168, 176)}
    rows = [
        ".oo.oo.",
        "olrorlo",
        "orrrrro",
        ".orrrro".replace("o", "r", 1),
        "..orro.",
        "...o...",
    ]
    return grid(rows, pal)


# ------------------------------------------------------------------ tiles
def tile_grass(rnd, variant=0, dark=False):
    t = pygame.Surface((S.TILE, S.TILE))
    base = S.GREEN if not dark else S.GREEN_D
    t.fill(base)
    for _ in range(10 + variant * 4):
        x, y = rnd.randrange(S.TILE), rnd.randrange(S.TILE)
        t.set_at((x, y), shade(base, -14))
    for _ in range(6):
        x, y = rnd.randrange(S.TILE), rnd.randrange(S.TILE)
        t.set_at((x, y), shade(base, 18))
    if variant == 2:
        x, y = rnd.randrange(2, 12), rnd.randrange(2, 12)
        pygame.draw.line(t, S.GREEN_L, (x, y + 2), (x + 1, y))
        pygame.draw.line(t, S.GREEN_L, (x + 3, y + 2), (x + 2, y))
    return t


def tile_flowerbed(rnd, dark=False):
    t = tile_grass(rnd, 1, dark)
    for _ in range(3):
        x, y = rnd.randrange(2, 13), rnd.randrange(2, 13)
        pygame.draw.rect(t, S.YELLOW, (x, y, 2, 2))
        t.set_at((x, y), S.GOLD)
    return t


def tile_path(rnd):
    t = pygame.Surface((S.TILE, S.TILE))
    t.fill((208, 184, 142))
    for _ in range(26):
        x, y = rnd.randrange(S.TILE), rnd.randrange(S.TILE)
        t.set_at((x, y), (190, 164, 124))
    for _ in range(8):
        x, y = rnd.randrange(S.TILE), rnd.randrange(S.TILE)
        t.set_at((x, y), (224, 204, 168))
    return t


def tile_sand(rnd):
    t = pygame.Surface((S.TILE, S.TILE))
    t.fill((238, 220, 168))
    for _ in range(18):
        x, y = rnd.randrange(S.TILE), rnd.randrange(S.TILE)
        t.set_at((x, y), (222, 202, 150))
    return t


def tile_stone(rnd):
    t = pygame.Surface((S.TILE, S.TILE))
    t.fill(S.STONE)
    for by in range(0, S.TILE, 8):
        off = 0 if by % 16 == 0 else 8
        for bx in range(-8, S.TILE, 16):
            pygame.draw.rect(t, S.STONE_D, (bx + off, by, 15, 7), 1)
    for _ in range(8):
        t.set_at((rnd.randrange(S.TILE), rnd.randrange(S.TILE)), S.STONE_L)
    return t


def tile_water(rnd, frame):
    t = pygame.Surface((S.TILE, S.TILE))
    t.fill(S.WATER)
    for y in range(S.TILE):
        if (y + frame) % 6 == 0:
            pygame.draw.line(t, S.WATER_D, (0, y), (S.TILE - 1, y))
    for i in range(3):
        x = (rnd.randrange(S.TILE) + frame * 3) % S.TILE
        y = (rnd.randrange(S.TILE) + frame) % S.TILE
        pygame.draw.line(t, S.WATER_L, (x, y), (min(S.TILE - 1, x + 3), y))
    return t


# ------------------------------------------------------------------ ASSETS
class Assets:
    """Contenedor unico con todos los graficos generados."""

    def __init__(self):
        rnd = random.Random(2109)
        self.player = make_character(PLAYER_PAL)
        self.npcs = {k: make_character(p) for k, p in NPC_PALETTES.items()}

        base_flower = make_flower(S.YELLOW, S.YELLOW_D, S.ORANGE)
        self.flower = flower_sway_frames(base_flower)
        self.flower_white = flower_sway_frames(make_flower(S.CREAM, S.CREAM_D, S.YELLOW))
        self.flower_pink = flower_sway_frames(make_flower(S.PINK, S.PINK_D, S.YELLOW))
        self.flower_icon = base_flower
        self.golden = flower_sway_frames(make_golden_flower())
        self.golden_icon = make_golden_flower()

        self.trees = [make_tree(rnd) for _ in range(3)]
        self.trees_dark = [make_tree(rnd, dark=True) for _ in range(3)]
        self.pines = [make_pine(rnd) for _ in range(2)]
        self.bushes = [make_bush(rnd) for _ in range(2)]
        self.bushes_dark = [make_bush(rnd, dark=True) for _ in range(2)]
        self.rocks = [make_rock(rnd) for _ in range(3)]

        self.houses = [
            make_house(rnd, S.CREAM, S.RED),
            make_house(rnd, (226, 206, 176), (150, 116, 180)),
            make_house(rnd, (214, 226, 232), S.ORANGE_D),
            make_house(rnd, (244, 226, 190), (92, 148, 132)),
        ]
        self.fountain = make_fountain()
        self.bench = make_bench()
        self.lamp = make_lamp()
        self.sign = make_sign()
        self.stall = make_stall()

        self.butterflies = {
            "yellow": make_butterfly(S.YELLOW),
            "pink": make_butterfly(S.PINK),
            "blue": make_butterfly(S.SKY),
            "white": make_butterfly(S.WHITE),
        }
        self.bird = make_bird()
        self.fish = make_fish()
        self.letter = make_letter()
        self.basket = make_basket()
        self.bouquet = make_bouquet()
        self.heart = make_heart()

        # Tiles
        self.tiles = {
            "grass0": tile_grass(rnd, 0),
            "grass1": tile_grass(rnd, 1),
            "grass2": tile_grass(rnd, 2),
            "grass_dark0": tile_grass(rnd, 0, True),
            "grass_dark1": tile_grass(rnd, 2, True),
            "flowerbed": tile_flowerbed(rnd),
            "path": tile_path(rnd),
            "sand": tile_sand(rnd),
            "stone": tile_stone(rnd),
        }
        self.water_frames = [tile_water(random.Random(7), f) for f in range(6)]
