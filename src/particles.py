"""Sistema de particulas y textos flotantes."""
import math
import random

import pygame

from . import settings as S
from . import ui


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color",
                 "size", "gravity", "drag", "sway", "phase", "fade")

    def __init__(self, x, y, vx, vy, life, color, size=1,
                 gravity=0.0, drag=1.0, sway=0.0, fade=True):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.drag = drag
        self.sway = sway
        self.phase = random.random() * 6.28
        self.fade = fade

    def update(self, dt):
        self.life -= dt
        self.vy += self.gravity * dt
        self.vx *= self.drag
        self.vy *= self.drag
        self.phase += dt * 3
        self.x += (self.vx + math.sin(self.phase) * self.sway) * dt
        self.y += self.vy * dt


class FloatingText:
    def __init__(self, x, y, text, color, size):
        self.x, self.y = x, y
        self.text = text
        self.life = 1.1
        self.color = color
        self.size = size

    def update(self, dt):
        self.life -= dt
        self.y -= dt * 18

    def draw(self, surf, camera):
        if self.life <= 0:
            return
        alpha = max(0, min(255, int(self.life * 320)))
        hw = ui.get_font(self.size).size(self.text)[0] // 2
        sx, sy = camera.to_screen(self.x - hw, self.y)
        ui.text(surf, self.text, (sx + hw, sy), self.size, self.color,
                shadow=S.DARK, center=True, alpha=alpha)


class ParticleSystem:
    """Gestiona particulas de mundo (con camara) y textos flotantes."""

    def __init__(self, font, size=11):
        self.parts = []
        self.texts = []
        self.font = font
        self.size = size

    def clear(self):
        self.parts.clear()
        self.texts.clear()

    # ------------------------------------------------------- emisores
    def burst(self, x, y, color, n=8, speed=40, life=0.6, size=1, gravity=60):
        for _ in range(n):
            ang = random.random() * 6.283
            sp = random.uniform(speed * 0.3, speed)
            self.parts.append(Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp - 20,
                                       life * random.uniform(0.6, 1.2), color,
                                       size, gravity, 0.98))

    def sparkle(self, x, y, n=6, color=S.GOLD):
        for _ in range(n):
            self.parts.append(Particle(
                x + random.uniform(-6, 6), y + random.uniform(-6, 6),
                random.uniform(-8, 8), random.uniform(-26, -8),
                random.uniform(0.4, 0.9), color, 1, 10, 0.99))

    def dust(self, x, y):
        self.parts.append(Particle(x + random.uniform(-2, 2), y,
                                   random.uniform(-8, 8), random.uniform(-6, -2),
                                   0.35, (226, 214, 180), 1, 20, 0.96))

    def petal(self, x, y, color=S.YELLOW, vy=None):
        self.parts.append(Particle(x, y, random.uniform(-6, 6),
                                   vy if vy is not None else random.uniform(12, 26),
                                   random.uniform(3.5, 6.5), color,
                                   random.choice((1, 2)), 0, 1.0, sway=14, fade=False))

    def firefly(self, x, y):
        self.parts.append(Particle(x, y, random.uniform(-8, 8), random.uniform(-8, 8),
                                   random.uniform(2.0, 4.0), S.GOLD, 1, 0, 1.0, sway=10))

    def text(self, x, y, msg, color=S.GOLD):
        self.texts.append(FloatingText(x, y, msg, color, self.size))

    # -------------------------------------------------------- ciclo
    def update(self, dt):
        for p in self.parts:
            p.update(dt)
        self.parts = [p for p in self.parts if p.life > 0]
        for t in self.texts:
            t.update(dt)
        self.texts = [t for t in self.texts if t.life > 0]

    def draw(self, surf, camera):
        for p in self.parts:
            sx, sy = camera.to_screen(p.x, p.y)
            if -8 < sx < S.GAME_W + 8 and -8 < sy < S.GAME_H + 8:
                ratio = p.life / p.max_life
                color = p.color
                if p.fade and ratio < 0.35:
                    color = tuple(int(c * (0.4 + ratio)) for c in p.color[:3])
                pygame.draw.rect(surf, color, (sx, sy, p.size, p.size))
        for t in self.texts:
            t.draw(surf, camera)


class ScreenParticles(ParticleSystem):
    """Particulas en coordenadas de pantalla (menus, cinematicas)."""

    def draw(self, surf, camera=None):
        for p in self.parts:
            pygame.draw.rect(surf, p.color, (int(p.x), int(p.y), p.size, p.size))
