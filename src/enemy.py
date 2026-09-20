"""Enemigos del modo plataformas: comportamiento, daño y muerte."""
import math
import random

import pygame

from . import settings as S

CONFIG = {
    "petalillo":   {"hp": 1, "speed": 26, "w": 14, "h": 13, "gravity": True,
                    "touch": 1, "score": 1},
    "saltarin":    {"hp": 2, "speed": 34, "w": 14, "h": 15, "gravity": True,
                    "touch": 1, "score": 2},
    "perseguidor": {"hp": 2, "speed": 62, "w": 16, "h": 14, "gravity": True,
                    "touch": 1, "score": 3},
    "volador":     {"hp": 1, "speed": 34, "w": 16, "h": 12, "gravity": False,
                    "touch": 1, "score": 2},
    "lanzador":    {"hp": 3, "speed": 16, "w": 16, "h": 18, "gravity": False,
                    "touch": 1, "score": 4},
    "guardian":    {"hp": 12, "speed": 40, "w": 32, "h": 40, "gravity": True,
                    "touch": 1, "score": 20},
}


class Enemy:
    def __init__(self, kind, frames, x, y, game, boss=False, range_y=24):
        self.kind = kind
        self.cfg = CONFIG[kind]
        self.frames = frames
        self.game = game
        self.boss = boss
        w, h = self.cfg["w"], self.cfg["h"]
        self.rect = pygame.Rect(int(x), int(y), w, h)
        self.fx, self.fy = float(x), float(y)
        self.vx = -self.cfg["speed"]
        self.vy = 0.0
        self.hp = self.cfg["hp"]
        self.max_hp = self.hp
        self.dead = False
        self.dying = 0.0
        self.flash = 0.0
        self.t = random.random() * 3
        self.home_y = float(y)
        self.range_y = range_y
        self.timer = random.uniform(0.5, 1.6)
        self.active = kind != "perseguidor"
        self.facing = -1
        self.phase = 0

    # ------------------------------------------------------------ ayuda
    def sync(self):
        self.rect.x = int(round(self.fx))
        self.rect.y = int(round(self.fy))

    def hurt(self, amount=1, from_x=None):
        if self.dying or self.dead:
            return
        self.hp -= amount
        self.flash = 0.18
        self.game.audio.play("enemy_hit")
        self.game.particles.burst(self.rect.centerx, self.rect.centery,
                                  S.YELLOW, 8, 60)
        if from_x is not None:
            self.vx = 60 if from_x < self.rect.centerx else -60
        if self.hp <= 0:
            self.kill()

    def kill(self):
        self.dying = 0.45
        self.game.audio.play("enemy_death")
        self.game.particles.burst(self.rect.centerx, self.rect.centery,
                                  S.GOLD, 22, 110, 0.8, 2, 90)
        self.game.particles.sparkle(self.rect.centerx, self.rect.centery, 10)
        if self.boss:
            self.game.camera.shake(5, 0.6)

    # -------------------------------------------------------------- ciclo
    def update(self, dt, level, player):
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        if self.dying > 0:
            self.dying -= dt
            self.fy += 40 * dt
            self.sync()
            if self.dying <= 0:
                self.dead = True
            return

        getattr(self, "_ai_" + self.kind)(dt, level, player)
        if self.cfg["gravity"]:
            self.vy = min(S.MAX_FALL, self.vy + S.GRAVITY * dt)
        self._move(dt, level)

    def _move(self, dt, level):
        self.fx += self.vx * dt
        self.sync()
        for r in level.solid_rects(self.rect):
            if self.rect.colliderect(r):
                if self.vx > 0:
                    self.rect.right = r.left
                else:
                    self.rect.left = r.right
                self.fx = self.rect.x
                self.vx = -self.vx
        self.fy += self.vy * dt
        self.sync()
        self.on_ground = False
        if self.cfg["gravity"]:
            for r in level.solid_rects(self.rect) + level.oneway_rects(self.rect):
                if self.rect.colliderect(r):
                    if self.vy > 0:
                        self.rect.bottom = r.top
                        self.on_ground = True
                    else:
                        self.rect.top = r.bottom
                    self.vy = 0
                    self.fy = self.rect.y
        if self.vx:
            self.facing = 1 if self.vx > 0 else -1

    # -------------------------------------------------------------- IA
    def _ai_petalillo(self, dt, level, player):
        if self.on_ground_ahead(level) is False:
            self.vx = -self.vx
        if self.vx == 0:
            self.vx = self.cfg["speed"]

    def on_ground_ahead(self, level):
        if not self.cfg["gravity"] or not getattr(self, "on_ground", False):
            return True
        x = self.rect.right + 2 if self.vx > 0 else self.rect.left - 2
        return level.solid_at(x, self.rect.bottom + 4) or \
            level.oneway_at(x, self.rect.bottom + 4)

    def _ai_saltarin(self, dt, level, player):
        self.timer -= dt
        if getattr(self, "on_ground", False):
            self.vx *= 0.85
            if self.timer <= 0:
                self.timer = random.uniform(1.0, 1.8)
                d = 1 if player.rect.centerx > self.rect.centerx else -1
                if abs(player.rect.centerx - self.rect.centerx) > 200:
                    d = -1 if self.facing < 0 else 1
                self.vx = d * self.cfg["speed"]
                self.vy = -215

    def _ai_perseguidor(self, dt, level, player):
        dist = abs(player.rect.centerx - self.rect.centerx)
        if dist < 220 and abs(player.rect.centery - self.rect.centery) < 170:
            self.active = True
        if self.active:
            d = 1 if player.rect.centerx > self.rect.centerx else -1
            self.vx = d * self.cfg["speed"]
            if getattr(self, "on_ground", False) and self.on_ground_ahead(level) is False:
                self.vy = -200
        else:
            self.vx = 0

    def _ai_volador(self, dt, level, player):
        self.fy = self.home_y + math.sin(self.t * 1.8) * self.range_y
        d = 1 if player.rect.centerx > self.rect.centerx else -1
        self.vx = d * self.cfg["speed"] * 0.6
        self.sync()

    def _ai_lanzador(self, dt, level, player):
        self.fy = self.home_y + math.sin(self.t * 1.2) * 8
        self.vx = 0
        self.sync()
        self.timer -= dt
        if self.timer <= 0 and abs(player.rect.centerx - self.rect.centerx) < 190:
            self.timer = 2.1
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            n = max(1.0, math.hypot(dx, dy))
            self.game.spawn_enemy_shot(self.rect.centerx, self.rect.centery,
                                       dx / n * 95, dy / n * 95)

    def _ai_guardian(self, dt, level, player):
        self.timer -= dt
        on_ground = getattr(self, "on_ground", False)
        dist = player.rect.centerx - self.rect.centerx
        if on_ground:
            self.vx *= 0.9
            if self.timer <= 0:
                self.timer = random.uniform(1.4, 2.2)
                self.phase = (self.phase + 1) % 3
                if self.phase == 0:
                    self.vy = -230
                    self.vx = (1 if dist > 0 else -1) * 60
                elif self.phase == 1:
                    for ang in (-35, 0, 35):
                        a = math.radians(ang)
                        d = 1 if dist > 0 else -1
                        self.game.spawn_enemy_shot(
                            self.rect.centerx, self.rect.centery,
                            math.cos(a) * 110 * d, math.sin(a) * 110 - 20)
                    self.game.audio.play("projectile")
                else:
                    self.vx = (1 if dist > 0 else -1) * self.cfg["speed"]

    # ---------------------------------------------------------- dibujado
    def image(self):
        img = self.frames[int(self.t * 6) % len(self.frames)]
        if self.facing > 0:
            img = pygame.transform.flip(img, True, False)
        if self.flash > 0:
            img = img.copy()
            img.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGB_ADD)
            img.fill((160, 160, 160, 0), special_flags=pygame.BLEND_RGB_ADD)
        return img

    def draw(self, surf, camera):
        img = self.image()
        if self.dying > 0:
            k = max(0.1, self.dying / 0.45)
            w = max(2, int(img.get_width() * k))
            h = max(2, int(img.get_height() * k))
            img = pygame.transform.scale(img, (w, h))
        x = self.rect.centerx - img.get_width() // 2
        y = self.rect.bottom - img.get_height()
        surf.blit(img, camera.to_screen(x, y))
        if self.boss and not self.dying:
            from . import ui
            bar = pygame.Rect(0, 0, 40, 4)
            bar.midbottom = camera.to_screen(self.rect.centerx, self.rect.top - 4)
            ui.bar(surf, bar, self.hp / self.max_hp, S.HEART_RED)
