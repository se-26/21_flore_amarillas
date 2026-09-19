"""NPCs del modo plataformas: idle animado y dialogo al pulsar E."""
import pygame

from . import settings as S


class NPC:
    def __init__(self, frames, x, y, name, lines):
        self.frames = frames
        self.name = name
        self.lines = lines
        self.t = 0.0
        self.talked = False
        img = frames["idle"][0]
        # el NPC se coloca en la fila sobre el suelo (y = row * TILE);
        # apoyamos los pies exactamente en la cima del tile de abajo
        self.rect = pygame.Rect(int(x), int(y) - img.get_height() + S.TILE,
                                img.get_width(), img.get_height())
        self.facing = 1

    def update(self, dt, player=None):
        self.t += dt
        if player:
            self.facing = 1 if player.rect.centerx > self.rect.centerx else -1

    def draw(self, surf, camera):
        img = self.frames["idle"][int(self.t * 3) % len(self.frames["idle"])]
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        x = self.rect.centerx - img.get_width() // 2
        y = self.rect.bottom - img.get_height()
        surf.blit(img, camera.to_screen(x, y))
