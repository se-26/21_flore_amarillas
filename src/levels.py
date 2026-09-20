"""Definicion y construccion procedural de los seis niveles."""
import random

from . import settings as S
from .tilemap import EMPTY, PLATFORM, SOLID, SPIKE


class LevelData:
    def __init__(self, key, number, name, theme, objective, flowers_required,
                 music="exploration", boss=False):
        self.key = key
        self.number = number
        self.name = name
        self.theme = theme
        self.objective = objective
        self.flowers_required = flowers_required
        self.music = music
        self.boss = boss
        self.grid = []
        self.entities = []
        self.decor = []
        self.spawn = (2, 2)


class Builder:
    """Pequeño DSL para construir niveles por tiles."""

    def __init__(self, data, cols, rows, seed):
        self.d = data
        self.cols, self.rows = cols, rows
        self.rnd = random.Random(seed)
        self.g = [[EMPTY] * cols for _ in range(rows)]

    # ------------------------------------------------------------ terreno
    def set(self, c, r, ch):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.g[r][c] = ch

    def ground(self, c0, c1, row, depth=None):
        depth = depth if depth is not None else self.rows
        for c in range(c0, c1):
            for r in range(row, min(self.rows, row + depth)):
                self.set(c, r, SOLID)

    def block(self, c0, r0, w, h):
        for c in range(c0, c0 + w):
            for r in range(r0, r0 + h):
                self.set(c, r, SOLID)

    def plat(self, c, row, w):
        for i in range(w):
            self.set(c + i, row, PLATFORM)

    def spikes(self, c0, row, w):
        for i in range(w):
            self.set(c0 + i, row, SPIKE)

    # ----------------------------------------------------------- entidades
    def ent(self, kind, c, row, **kw):
        e = {"kind": kind, "x": c * S.TILE, "y": row * S.TILE}
        e.update(kw)
        self.d.entities.append(e)
        return e

    def flower(self, c, row):
        self.ent("flower", c, row)

    def sun(self, c, row, ammo_only=False):
        self.ent("sunflower", c, row, ammo_only=ammo_only)

    def enemy(self, kind, c, row, **kw):
        self.ent("enemy", c, row, enemy=kind, **kw)

    def npc(self, key, c, row, name, lines):
        self.ent("npc", c, row, npc=key, name=name, lines=lines)

    def check(self, c, row):
        self.ent("checkpoint", c, row)

    def door(self, c, row):
        self.ent("door", c, row)

    def mover(self, c, row, w, dx, dy, dist, speed=34):
        self.ent("mover", c, row, w=w, dx=dx, dy=dy, dist=dist, speed=speed)

    def vanish(self, c, row, w, phase=0.0):
        self.ent("vanish", c, row, w=w, phase=phase)

    def deco(self, kind, c, row, **kw):
        d = {"kind": kind, "x": c * S.TILE, "y": row * S.TILE}
        d.update(kw)
        self.d.decor.append(d)

    def scatter_deco(self, c0, c1, row, density=0.5):
        for c in range(c0, c1):
            if self.rnd.random() < density * 0.25:
                self.deco("flower", c, row, v=self.rnd.randrange(4))
            elif self.rnd.random() < density * 0.10:
                self.deco("bush", c, row, v=self.rnd.randrange(2))
            elif self.rnd.random() < density * 0.06:
                self.deco("tree", c, row, v=self.rnd.randrange(2))
            elif self.rnd.random() < density * 0.05:
                self.deco("rock", c, row, v=self.rnd.randrange(2))

    def finish(self, spawn_c, spawn_r):
        self.d.grid = ["".join(row) for row in self.g]
        self.d.spawn = (spawn_c * S.TILE, spawn_r * S.TILE)
        return self.d


# ------------------------------------------------------------------ NIVEL 1
def level_1():
    d = LevelData("campo", 1, "EL CAMPO DORADO", "campo",
                  ["Recolecta 10 flores amarillas.", "¡Llega hasta la puerta final!"], 10)
    b = Builder(d, 150, 20, 101)
    gy = 14
    b.ground(0, 26, gy)
    b.scatter_deco(1, 25, gy - 1, 0.9)
    for c in range(4, 24, 5):
        b.flower(c, gy - 2)
    b.enemy("petalillo", 18, gy - 1)
    b.npc("npc_jardinero", 8, gy - 1, "Jardinero", [
        "Buenas, ¡hoy es 21 de septiembre!",
        "Usa A y D para caminar y ESPACIO para saltar.",
        "Las flores mas brillantes suelen esconderse donde menos las esperas.",
    ])
    b.check(24, gy - 1)

    x = 28
    while x < 128:
        pattern = b.rnd.choice(["plano", "hueco", "escalon", "plataformas"])
        if pattern == "plano":
            w = b.rnd.randint(8, 14)
            b.ground(x, x + w, gy)
            b.scatter_deco(x, x + w, gy - 1, 0.8)
            if b.rnd.random() < 0.7:
                b.flower(x + w // 2, gy - 2)
            if b.rnd.random() < 0.6:
                b.enemy("petalillo", x + w - 3, gy - 1)
            x += w + b.rnd.randint(2, 3)
        elif pattern == "hueco":
            gap = b.rnd.randint(2, 3)
            x += gap
            w = b.rnd.randint(6, 10)
            b.ground(x, x + w, gy)
            b.scatter_deco(x, x + w, gy - 1, 0.7)
            b.flower(x + 2, gy - 2)
            x += w
        elif pattern == "escalon":
            b.ground(x, x + 5, gy)
            b.block(x + 5, gy - 2, 5, 2)
            b.ground(x + 5, x + 10, gy)
            b.flower(x + 7, gy - 4)
            b.scatter_deco(x, x + 5, gy - 1, 0.6)
            if b.rnd.random() < 0.5:
                b.enemy("petalillo", x + 8, gy - 3)
            x += 12
        else:
            b.ground(x, x + 12, gy)
            b.plat(x + 3, gy - 4, 4)
            b.plat(x + 8, gy - 6, 3)
            b.flower(x + 4, gy - 6)
            b.flower(x + 9, gy - 8)
            b.scatter_deco(x, x + 12, gy - 1, 0.6)
            x += 14
        if x > 60 and not any(e["kind"] == "sunflower" for e in d.entities):
            b.ground(x, x + 8, gy)
            b.sun(x + 4, gy - 2)
            b.npc("npc_gracioso", x + 1, gy - 1, "Jhony", [
                "Si ves una flor flotando... probablemente no deberias preguntarte por que.",
                "Ese girasol de ahi guarda una sorpresa. Acercate y pulsa E.",
            ])
            x += 10
        if x > 90 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 2:
            b.ground(x, x + 4, gy)
            b.check(x + 2, gy - 1)
            x += 5

    b.ground(128, 150, gy)
    b.scatter_deco(129, 148, gy - 1, 1.0)
    b.flower(132, gy - 2)
    b.flower(136, gy - 2)
    b.enemy("petalillo", 138, gy - 1)
    b.door(144, gy - 3)
    return b.finish(3, gy - 3)


# ------------------------------------------------------------------ NIVEL 2
def level_2():
    d = LevelData("bosque", 2, "EL BOSQUE SUSURRANTE", "bosque",
                  ["Recolecta 12 flores amarillas.", "Cuidado con los saltarines."], 12)
    b = Builder(d, 165, 22, 202)
    gy = 16
    b.ground(0, 20, gy)
    b.scatter_deco(1, 19, gy - 1, 1.0)
    b.npc("npc_misterioso", 6, gy - 1, "Yari", [
        "Ten cuidado... este bosque no siempre funciona como deberia.",
        "Algunas flores estan sobre las copas. Mira hacia arriba.",
    ])
    b.check(17, gy - 1)
    b.flower(10, gy - 2)
    b.flower(14, gy - 5)
    b.plat(12, gy - 4, 4)

    x = 24
    while x < 140:
        p = b.rnd.choice(["saltos", "torre", "puente", "claro"])
        if p == "saltos":
            for i in range(3):
                w = b.rnd.randint(4, 6)
                b.ground(x, x + w, gy - i % 2)
                b.scatter_deco(x, x + w, gy - 1 - i % 2, 0.8)
                if b.rnd.random() < 0.6:
                    b.flower(x + w // 2, gy - 2 - i % 2)
                x += w + b.rnd.randint(3, 4)
            b.enemy("saltarin", x - 6, gy - 2)
        elif p == "torre":
            b.ground(x, x + 10, gy)
            b.block(x + 3, gy - 3, 3, 3)
            b.plat(x + 7, gy - 5, 3)
            b.plat(x + 2, gy - 7, 3)
            b.flower(x + 3, gy - 9)
            b.flower(x + 8, gy - 7)
            b.enemy("saltarin", x + 7, gy - 1)
            b.scatter_deco(x, x + 10, gy - 1, 0.7)
            x += 13
        elif p == "puente":
            b.ground(x, x + 3, gy)
            for i in range(5):
                b.plat(x + 4 + i * 3, gy - 2 - (i % 2), 2)
            b.flower(x + 10, gy - 5)
            b.ground(x + 19, x + 24, gy)
            b.scatter_deco(x + 19, x + 24, gy - 1, 0.7)
            x += 26
        else:
            b.ground(x, x + 14, gy)
            b.scatter_deco(x, x + 14, gy - 1, 1.2)
            b.flower(x + 4, gy - 2)
            b.enemy("petalillo", x + 8, gy - 1)
            b.enemy("saltarin", x + 12, gy - 1)
            if b.rnd.random() < 0.5:
                b.plat(x + 5, gy - 6, 4)
                b.flower(x + 6, gy - 8)   # secreto alto
            x += 16
        if x > 70 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 2:
            b.check(x - 2, gy - 1)
        if x > 95 and not any(e["kind"] == "sunflower" for e in d.entities):
            b.sun(x - 4, gy - 2, ammo_only=True)

    b.ground(140, 165, gy)
    b.scatter_deco(141, 163, gy - 1, 1.2)
    b.check(143, gy - 1)
    b.flower(146, gy - 2)
    b.flower(150, gy - 4)
    b.plat(148, gy - 3, 4)
    b.enemy("saltarin", 154, gy - 1)
    b.door(159, gy - 3)
    return b.finish(3, gy - 3)


# ------------------------------------------------------------------ NIVEL 3
def level_3():
    d = LevelData("inverso", 3, "EL BOSQUE AL REVES", "inverso",
                  ["Recolecta 12 flores.",
                   "No siempre debes seguir el camino que ves."], 12)
    b = Builder(d, 170, 26, 303)
    gy = 20
    b.ground(0, 18, gy)
    b.npc("npc_misterioso", 6, gy - 1, "Dani", [
        "Bienvenida al bosque al reves.",
        "No siempre debes seguir el camino que ves.",
        "Las plataformas de arriba tambien llevan a alguna parte.",
    ])
    b.check(15, gy - 1)
    b.flower(10, gy - 2)
    b.scatter_deco(1, 17, gy - 1, 0.8)

    x = 22
    while x < 145:
        p = b.rnd.choice(["colgante", "flotante", "espejo", "raices"])
        if p == "colgante":
            b.block(x, 2, 12, 3)           # techo
            for i in range(4):
                b.plat(x + 1 + i * 3, 6 + (i % 2) * 3, 3)
            b.flower(x + 9, 8)
            b.ground(x, x + 12, gy)
            b.enemy("perseguidor", x + 6, gy - 1)
            b.scatter_deco(x, x + 12, gy - 1, 0.5)
            x += 15
        elif p == "flotante":
            for i in range(5):
                r = gy - 3 - (i % 3) * 3
                b.plat(x + i * 4, r, 3)
                if i % 2 == 0:
                    b.flower(x + i * 4 + 1, r - 2)
            x += 22
        elif p == "espejo":
            b.ground(x, x + 8, gy)
            b.block(x + 2, gy - 8, 6, 2)
            b.plat(x + 3, gy - 4, 4)
            b.spikes(x + 4, gy - 1, 3)
            b.enemy("perseguidor", x + 6, gy - 1)
            b.scatter_deco(x, x + 2, gy - 1, 0.6)
            x += 11
            b.ground(x, x + 4, gy)
            b.flower(x + 2, gy - 2)
            x += 5
        else:
            b.ground(x, x + 14, gy)
            for i in range(3):
                b.block(x + 2 + i * 4, gy - 3 - i, 2, 3 + i)
            b.scatter_deco(x, x + 14, gy - 1, 0.7)
            b.enemy("saltarin", x + 12, gy - 1)
            x += 16
            b.ground(x, x + 4, gy)
            b.flower(x + 2, gy - 2)
            x += 5
        if x > 60 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 2:
            b.check(x - 3, gy - 1)
        if x > 100 and not any(e["kind"] == "sunflower" for e in d.entities):
            b.ground(x, x + 4, gy)
            b.sun(x + 1, gy - 2, ammo_only=True)
            x += 6
        if x > 110 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 3:
            b.check(x - 2, gy - 1)

    b.ground(145, 170, gy)
    b.scatter_deco(146, 168, gy - 1, 0.9)
    b.flower(150, gy - 2)
    b.flower(156, gy - 5)
    b.plat(154, gy - 4, 4)
    b.enemy("perseguidor", 160, gy - 1)
    b.flower(162, gy - 2)
    b.flower(163, gy - 2)
    b.door(165, gy - 3)
    return b.finish(3, gy - 3)


# ------------------------------------------------------------------ NIVEL 4
def level_4():
    d = LevelData("cielo", 4, "LAS ISLAS DEL CIELO", "cielo",
                  ["Recolecta 12 flores entre las islas.",
                   "Usa las plataformas moviles."], 12)
    b = Builder(d, 150, 34, 404)
    gy = 30
    b.ground(0, 14, gy)
    b.check(11, gy - 1)
    b.flower(6, gy - 2)
    b.npc("npc_gracioso", 4, gy - 1, "Jhony", [
        "¡Aqui arriba el suelo es opcional!",
        "Si caes, no pasa nada: volveras al ultimo banderin.",
    ])
    b.scatter_deco(1, 13, gy - 1, 0.6)

    x = 18
    row = gy - 3
    while x < 128:
        p = b.rnd.choice(["isla", "movil", "escalera", "nido"])
        if p == "isla":
            w = b.rnd.randint(5, 8)
            row = max(6, min(gy - 1, row + b.rnd.choice([-3, -2, 0, 2])))
            b.block(x, row, w, 2)
            b.flower(x + w // 2, row - 2)
            if b.rnd.random() < 0.5:
                b.enemy("volador", x + w // 2, row - 5, range_y=26)
            b.scatter_deco(x, x + w, row - 1, 0.5)
            x += w + 3
        elif p == "movil":
            b.mover(x, row, 3, 1, 0, 4 * S.TILE, 36)
            b.flower(x + 5, row - 3)
            x += 9
        elif p == "escalera":
            for i in range(4):
                b.plat(x + i * 3, row - i * 2, 3)
                if i % 2:
                    b.flower(x + i * 3 + 1, row - i * 2 - 2)
            row = max(6, row - 8)
            x += 14
        else:
            b.block(x, row, 10, 2)
            b.plat(x + 3, row - 4, 4)
            b.flower(x + 4, row - 6)
            b.enemy("volador", x + 6, row - 8, range_y=34)
            b.enemy("petalillo", x + 8, row - 1)
            b.scatter_deco(x, x + 10, row - 1, 0.5)
            x += 13
        if x > 55 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 2:
            b.block(x, row, 4, 2)
            b.check(x + 1, row - 1)
            x += 6
        if x > 80 and not any(e["kind"] == "sunflower" for e in d.entities):
            b.block(x, row, 5, 2)
            b.sun(x + 2, row - 2, ammo_only=True)
            x += 7
        if x > 100 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 3:
            b.block(x, row, 4, 2)
            b.check(x + 1, row - 1)
            x += 6

    b.block(128, 18, 22, 3)
    b.scatter_deco(129, 148, 17, 0.7)
    b.flower(132, 16)
    b.flower(138, 16)
    b.enemy("volador", 136, 12, range_y=30)
    b.door(144, 15)
    return b.finish(3, gy - 3)


# ------------------------------------------------------------------ NIVEL 5
def level_5():
    d = LevelData("sueno", 5, "EL MUNDO DE LOS SUEÑOS", "sueno",
                  ["Recolecta 14 flores luminosas.",
                   "Algunas plataformas no estan siempre ahi."], 14)
    b = Builder(d, 175, 28, 505)
    gy = 22
    b.ground(0, 16, gy)
    b.check(13, gy - 1)
    b.flower(8, gy - 2)
    b.sun(9, gy - 2, ammo_only=True)
    b.npc("npc_misterioso", 5, gy - 1, "Dani", [
        "Estas soñando, y aun asi las flores pesan en tus manos.",
        "Lo que desaparece siempre vuelve. Solo hay que esperar el momento.",
    ])
    b.scatter_deco(1, 15, gy - 1, 0.5)

    x = 20
    while x < 150:
        p = b.rnd.choice(["parpadeo", "trampa", "lanzadores", "luces"])
        if p == "parpadeo":
            for i in range(5):
                if i % 2 == 0:
                    b.plat(x + i * 4, gy - 3 - (i % 2) * 2, 3)
                    b.flower(x + i * 4 + 1, gy - 5 - (i % 2) * 2)
                else:
                    b.mover(x + i * 4, gy - 3 - (i % 2) * 2, 3, 0, -1,
                            2 * S.TILE, 26)
            x += 22
        elif p == "trampa":
            b.ground(x, x + 12, gy)
            b.spikes(x + 4, gy - 1, 4)
            b.plat(x + 3, gy - 4, 6)
            b.flower(x + 6, gy - 6)
            b.enemy("perseguidor", x + 10, gy - 1)
            x += 15
        elif p == "lanzadores":
            b.ground(x, x + 14, gy)
            b.enemy("lanzador", x + 5, gy - 4)
            b.enemy("lanzador", x + 11, gy - 6)
            b.flower(x + 8, gy - 2)
            b.plat(x + 7, gy - 4, 4)
            b.scatter_deco(x, x + 14, gy - 1, 0.4)
            x += 17
        else:
            b.ground(x, x + 10, gy)
            b.plat(x + 2, gy - 3, 3)
            b.plat(x + 6, gy - 6, 3)
            b.flower(x + 3, gy - 5)
            b.flower(x + 7, gy - 8)
            b.enemy("volador", x + 5, gy - 10, range_y=30)
            x += 13
        if x > 60 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 2:
            b.ground(x, x + 4, gy)
            b.check(x + 2, gy - 1)
            x += 5
        if x > 90 and not any(e["kind"] == "sunflower" for e in d.entities):
            b.ground(x, x + 5, gy)
            b.sun(x + 2, gy - 2, ammo_only=True)
            x += 6
        if x > 120 and len([e for e in d.entities if e["kind"] == "checkpoint"]) < 3:
            b.ground(x, x + 4, gy)
            b.check(x + 2, gy - 1)
            x += 5

    b.ground(150, 175, gy)
    b.flower(154, gy - 2)
    b.flower(158, gy - 2)
    b.enemy("lanzador", 162, gy - 5)
    b.scatter_deco(151, 173, gy - 1, 0.6)
    b.door(170, gy - 3)
    return b.finish(3, gy - 3)


# ------------------------------------------------------------------ NIVEL 6
def level_6():
    d = LevelData("jardin", 6, "EL JARDIN FINAL", "jardin",
                  ["Derrota al guardian del jardin.",
                   "Reune 10 flores y entrega el ramo."], 10,
                  music="final_theme", boss=True)
    b = Builder(d, 130, 22, 606)
    gy = 16
    b.ground(0, 40, gy)
    b.scatter_deco(1, 39, gy - 1, 1.4)
    b.check(6, gy - 1)
    b.npc("npc_jardinero", 10, gy - 1, "Jardinero", [
        "Has llegado lejos. El jardin te estaba esperando.",
        "El guardian no es malo: solo cuida las flores mas bonitas.",
        "Usa X para lanzar flores. Tres impactos seguidos y se calmara.",
    ])
    for c in (8, 14, 20, 26, 32, 37):
        b.flower(c, gy - 2)
    b.plat(16, gy - 4, 4)
    b.plat(24, gy - 6, 4)
    b.flower(17, gy - 6)
    b.flower(25, gy - 8)
    b.enemy("petalillo", 30, gy - 1)

    b.ground(44, 86, gy)
    b.scatter_deco(45, 85, gy - 1, 1.0)
    b.check(47, gy - 1)
    b.sun(50, gy - 2, ammo_only=True)
    b.flower(56, gy - 2)
    b.flower(62, gy - 5)
    b.plat(60, gy - 4, 4)
    b.sun(72, gy - 2, ammo_only=True)
    b.enemy("guardian", 70, gy - 3, boss=True)

    b.ground(90, 130, gy)
    b.scatter_deco(91, 128, gy - 1, 1.6)
    b.check(92, gy - 1)
    b.flower(96, gy - 2)
    b.flower(102, gy - 2)
    b.plat(104, gy - 5, 5)
    b.flower(106, gy - 7)
    b.door(124, gy - 3)
    return b.finish(3, gy - 3)


BUILDERS = [level_1, level_2, level_3, level_4, level_5, level_6]


def build(index):
    """index 0..5"""
    return BUILDERS[max(0, min(len(BUILDERS) - 1, index))]()
