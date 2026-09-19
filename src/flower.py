"""Coleccionables y objetos interactivos del modo plataformas."""
import math

import pygame

from . import settings as S


class Flower:
    """Flor amarilla recolectable: flota, brilla y suelta particulas."""

    def __init__(self, frames, x, y):
        self.frames = frames
        self.x, self.y = float(x), float(y)
        self.t = (x * 0.03) % 6.28
        self.taken = False
        self.rect = pygame.Rect(int(x), int(y), 12, 14)

    def update(self, dt, particles):
        self.t += dt * 2.2
        self.rect.y = int(self.y + math.sin(self.t) * 2)
        if particles and int(self.t * 3) % 11 == 0:
            particles.sparkle(self.rect.centerx, self.rect.centery, 1)

    def draw(self, surf, camera):
        if self.taken:
            return
        img = self.frames[int(self.t * 2) % len(self.frames)]
        glow = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 232, 140, 40), (11, 11), 8)
        surf.blit(glow, camera.to_screen(self.rect.centerx - 11, self.rect.centery - 11))
        surf.blit(img, camera.to_screen(self.rect.x, self.rect.y))


class Sunflower:
    """Girasol especial: desbloquea el poder o recarga munición."""

    def __init__(self, frames, x, y, ammo_only=False):
        self.frames = frames
        self.x, self.y = float(x), float(y)
        self.ammo_only = ammo_only
        self.used = False
        self.t = 0.0
        self.rect = pygame.Rect(int(x) - 4, int(y) - 12, 22, 28)

    def update(self, dt, particles):
        self.t += dt * 2.0
        if particles and int(self.t * 4) % 7 == 0 and not self.used:
            particles.sparkle(self.rect.centerx, self.rect.centery - 6, 1)

    def draw(self, surf, camera):
        img = self.frames[int(self.t) % len(self.frames)]
        if not self.used:
            glow = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 226, 120, 52), (22, 22), 16)
            pygame.draw.circle(glow, (255, 240, 170, 40), (22, 22), 10)
            surf.blit(glow, camera.to_screen(self.rect.centerx - 22,
                                             self.rect.centery - 24))
        else:
            img = img.copy()
            img.set_alpha(150)
        surf.blit(img, camera.to_screen(self.rect.x, self.rect.y - 4))


class Checkpoint:
    def __init__(self, frames, x, y):
        self.frames = frames
        self.x, self.y = float(x), float(y)
        self.active = False
        self.t = 0.0
        self.rect = pygame.Rect(int(x), int(y) - 16, 18, 32)

    def update(self, dt, particles):
        self.t += dt * 4
        if self.active and particles and int(self.t) % 9 == 0:
            particles.sparkle(self.rect.centerx, self.rect.top + 6, 1)

    def draw(self, surf, camera):
        key = "on" if self.active else "off"
        img = self.frames[key][int(self.t) % 4]
        surf.blit(img, camera.to_screen(self.rect.x, self.rect.y))


class Door:
    def __init__(self, frames, x, y):
        self.frames = frames
        self.t = 0.0
        self.rect = pygame.Rect(int(x), int(y) - 24, 28, 40)
        self.open = False

    def update(self, dt, particles):
        self.t += dt * 5
        if self.open and particles and int(self.t) % 5 == 0:
            particles.sparkle(self.rect.centerx, self.rect.centery, 1)

    def draw(self, surf, camera):
        img = self.frames[int(self.t) % len(self.frames)]
        if not self.open:
            img = img.copy()
            img.set_alpha(170)
        surf.blit(img, camera.to_screen(self.rect.x, self.rect.y))
