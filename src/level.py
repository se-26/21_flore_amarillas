"""Nivel en ejecucion: tiles, entidades, plataformas especiales y parallax."""
import math

import pygame

from . import settings as S
from . import levels as leveldefs
from .enemy import Enemy
from .flower import Checkpoint, Door, Flower, Sunflower
from .npc import NPC
from .tilemap import TileMap


class MovingPlatform:
    def __init__(self, x, y, w, dx, dy, dist, speed):
        self.rect = pygame.Rect(int(x), int(y), w * S.TILE, 6)
        self.ox, self.oy = float(x), float(y)
        self.dx, self.dy = dx, dy
        self.dist = dist
        self.speed = speed
        self.dir = 1
        self.travel = 0.0
        self.vx = self.vy = 0.0
        self.solid = True

    def update(self, dt):
        self.travel += self.speed * self.dir * dt
        if self.travel > self.dist:
            self.travel = self.dist
            self.dir = -1
        elif self.travel < 0:
            self.travel = 0
            self.dir = 1
        nx = self.ox + self.dx * self.travel
        ny = self.oy + self.dy * self.travel
        self.vx = (nx - self.rect.x) / max(dt, 1e-5)
        self.vy = (ny - self.rect.y) / max(dt, 1e-5)
        self.rect.x, self.rect.y = int(nx), int(ny)

    def draw(self, surf, camera, art, theme):
        tile = art.tiles[theme]["plat"]
        for i in range(self.rect.w // S.TILE):
            surf.blit(tile, camera.to_screen(self.rect.x + i * S.TILE, self.rect.y))


class VanishPlatform:
    CYCLE = 15.0
    PRESENTE = 10.0
    PERIODO_VISIBLE = 5.0

    def __init__(self, x, y, w, phase):
        self.rect = pygame.Rect(int(x), int(y), w * S.TILE, 6)
        self.phase = phase
        self.t = phase % self.CYCLE
        self.solid = self.t < self.PRESENTE
        self.alpha = 255

    def update(self, dt):
        self.t = (self.t + dt) % self.CYCLE
        on = self.t < self.PRESENTE
        self.solid = on
        if on:
            fade = min(1.0, (self.PRESENTE - self.t) / 0.5)
            self.alpha = int(120 + 135 * fade)
        else:
            self.alpha = 60

    def draw(self, surf, camera, art, theme):
        tile = art.tiles[theme]["plat"].copy()
        tile.set_alpha(self.alpha)
        for i in range(self.rect.w // S.TILE):
            surf.blit(tile, camera.to_screen(self.rect.x + i * S.TILE, self.rect.y))


class Level:
    def __init__(self, index, game):
        self.game = game
        self.data = leveldefs.build(index)
        self.index = index
        self.theme = self.data.theme
        self.tiles = TileMap(self.data.grid, self.theme).bake(game.art)
        self.flowers = []
        self.sunflowers = []
        self.enemies = []
        self.npcs = []
        self.checkpoints = []
        self.movers = []
        self.vanishers = []
        self.door = None
        self.boss = None
        self.decor = list(self.data.decor)
        self.t = 0.0
        self._spawn_entities()
        self.spawn_point = self.data.spawn
        self.layers = game.art.backgrounds[self.theme]

    # ----------------------------------------------------------- entidades
    def _spawn_entities(self):
        art = self.game.art
        for e in self.data.entities:
            k = e["kind"]
            if k == "flower":
                self.flowers.append(Flower(art.flower, e["x"], e["y"]))
            elif k == "sunflower":
                self.sunflowers.append(Sunflower(art.sunflower, e["x"], e["y"],
                                                 e.get("ammo_only", False)))
            elif k == "enemy":
                en = Enemy(e["enemy"], art.enemies[e["enemy"]], e["x"], e["y"],
                           self.game, boss=e.get("boss", False),
                           range_y=e.get("range_y", 24))
                self.enemies.append(en)
                if en.boss:
                    self.boss = en
            elif k == "npc":
                self.npcs.append(NPC(art.npcs[e["npc"]], e["x"], e["y"],
                                     e["name"], e["lines"]))
            elif k == "checkpoint":
                self.checkpoints.append(Checkpoint(art.checkpoint, e["x"], e["y"]))
            elif k == "door":
                self.door = Door(art.door, e["x"], e["y"])
            elif k == "mover":
                self.movers.append(MovingPlatform(e["x"], e["y"], e["w"], e["dx"],
                                                  e["dy"], e["dist"], e["speed"]))
            elif k == "vanish":
                self.vanishers.append(VanishPlatform(e["x"], e["y"], e["w"],
                                                     e.get("phase", 0.0)))

    # ---------------------------------------------------------- colisiones
    @property
    def pixel_size(self):
        return self.tiles.pixel_size

    def solid_rects(self, rect):
        return self.tiles.solid_rects_around(rect)

    def oneway_rects(self, rect):
        out = self.tiles.platform_rects_around(rect)
        for v in self.vanishers:
            if v.solid and abs(v.rect.centerx - rect.centerx) < 120:
                out.append(v.rect)
        for m in self.movers:
            if abs(m.rect.centerx - rect.centerx) < 160:
                out.append(m.rect)
        return out

    def spike_rects(self, rect):
        return self.tiles.spike_rects_around(rect)

    def collides_solid(self, rect):
        return any(rect.colliderect(r) for r in self.solid_rects(rect))

    def solid_at(self, x, y):
        return self.tiles.is_solid(int(x) // S.TILE, int(y) // S.TILE)

    def oneway_at(self, x, y):
        return self.tiles.is_platform(int(x) // S.TILE, int(y) // S.TILE)

    # -------------------------------------------------------------- ciclo
    def update(self, dt, player, particles):
        self.t += dt
        for m in self.movers:
            m.update(dt)
        for v in self.vanishers:
            v.update(dt)
        for f in self.flowers:
            if not f.taken:
                f.update(dt, particles)
        for s in self.sunflowers:
            s.update(dt, particles)
        for c in self.checkpoints:
            c.update(dt, particles)
        if self.door:
            self.door.update(dt, particles)
        for n in self.npcs:
            n.update(dt, player)
        cam = self.game.camera
        for en in self.enemies:
            near = abs(en.rect.centerx - cam.x - S.GAME_W / 2) < S.GAME_W * 1.2
            if near or en.dying > 0:
                en.update(dt, self, player)
        self.enemies = [e for e in self.enemies if not e.dead]

    # ---------------------------------------------------------- dibujado
    def draw_background(self, surf, camera):
        for layer in self.layers:
            s = layer["surf"]
            f = layer["factor"]
            if f == 0.0:
                surf.blit(s, (0, 0))
                continue
            off = -(camera.ox * f) % s.get_width()
            x = off - s.get_width()
            while x < S.GAME_W:
                surf.blit(s, (int(x), layer["y"]))
                x += s.get_width()

    def draw_decor(self, surf, camera):
        props = self.game.art.props[self.theme]
        for d in self.decor:
            sx = d["x"] - camera.ox
            if sx < -60 or sx > S.GAME_W + 60:
                continue
            kind = d["kind"]
            img = props[kind][d.get("v", 0) % len(props[kind])]
            surf.blit(img, (int(sx), int(d["y"] - camera.oy - img.get_height() + 16)))

    def draw_world(self, surf, camera):
        self.tiles.draw(surf, camera)
        for m in self.movers:
            m.draw(surf, camera, self.game.art, self.theme)
        for v in self.vanishers:
            v.draw(surf, camera, self.game.art, self.theme)
        for s in self.sunflowers:
            s.draw(surf, camera)
        for c in self.checkpoints:
            c.draw(surf, camera)
        if self.door:
            self.door.draw(surf, camera)
        for f in self.flowers:
            f.draw(surf, camera)
        for n in self.npcs:
            n.draw(surf, camera)
        for e in self.enemies:
            e.draw(surf, camera)
