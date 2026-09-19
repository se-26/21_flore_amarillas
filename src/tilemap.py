"""Mapa de tiles del modo plataformas: solidos, plataformas y pinchos."""
import random

import pygame

from . import settings as S
from . import art

SOLID = "#"
PLATFORM = "="
SPIKE = "^"
EMPTY = "."


class TileMap:
    def __init__(self, grid, theme):
        self.grid = grid
        self.theme = theme
        self.rows = len(grid)
        self.cols = max(len(r) for r in grid) if grid else 0
        self.base = None

    # ------------------------------------------------------------ consulta
    def at(self, col, row):
        if 0 <= row < self.rows and 0 <= col < len(self.grid[row]):
            return self.grid[row][col]
        return EMPTY

    def is_solid(self, col, row):
        return self.at(col, row) == SOLID

    def is_platform(self, col, row):
        return self.at(col, row) == PLATFORM

    def is_spike(self, col, row):
        return self.at(col, row) == SPIKE

    def tile_rect(self, col, row):
        return pygame.Rect(col * S.TILE, row * S.TILE, S.TILE, S.TILE)

    def solid_rects_around(self, rect, margin=1):
        c0 = rect.left // S.TILE - margin
        c1 = rect.right // S.TILE + margin
        r0 = rect.top // S.TILE - margin
        r1 = rect.bottom // S.TILE + margin
        out = []
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if self.is_solid(c, r):
                    out.append(self.tile_rect(c, r))
        return out

    def platform_rects_around(self, rect, margin=1):
        c0 = rect.left // S.TILE - margin
        c1 = rect.right // S.TILE + margin
        r0 = rect.top // S.TILE - margin
        r1 = rect.bottom // S.TILE + margin
        out = []
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if self.is_platform(c, r):
                    out.append(pygame.Rect(c * S.TILE, r * S.TILE, S.TILE, 6))
        return out

    def spike_rects_around(self, rect, margin=1):
        c0 = rect.left // S.TILE - margin
        c1 = rect.right // S.TILE + margin
        r0 = rect.top // S.TILE - margin
        r1 = rect.bottom // S.TILE + margin
        out = []
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if self.is_spike(c, r):
                    out.append(pygame.Rect(c * S.TILE, r * S.TILE + 6, S.TILE, 10))
        return out

    def solid_below(self, x, y):
        return self.is_solid(int(x) // S.TILE, int(y) // S.TILE)

    # -------------------------------------------------------- renderizado
    def bake(self, platform_art):
        rnd = random.Random(self.cols * 7 + self.rows)
        tiles = platform_art.tiles[self.theme]
        self.base = pygame.Surface((self.cols * S.TILE, self.rows * S.TILE),
                                   pygame.SRCALPHA)
        for r in range(self.rows):
            for c in range(len(self.grid[r])):
                ch = self.grid[r][c]
                pos = (c * S.TILE, r * S.TILE)
                if ch == SOLID:
                    top = not self.is_solid(c, r - 1)
                    img = rnd.choice(tiles["top"] if top else tiles["body"])
                    self.base.blit(img, pos)
                elif ch == PLATFORM:
                    self.base.blit(tiles["plat"], pos)
                elif ch == SPIKE:
                    self.base.blit(tiles["spike"], pos)
        return self

    def draw(self, surf, camera):
        surf.blit(self.base, (-int(camera.ox), -int(camera.oy)))

    @property
    def pixel_size(self):
        return self.cols * S.TILE, self.rows * S.TILE
