"""Camara 2D de plataformas: seguimiento suave, limites, shake y parallax."""
import math
import random

from . import settings as S


class Camera:
    def __init__(self, world_w=S.GAME_W, world_h=S.GAME_H):
        self.x = 0.0
        self.y = 0.0
        self.world_w = world_w
        self.world_h = world_h
        self.shake_time = 0.0
        self.shake_power = 0.0
        self.offset = (0, 0)

    def set_world(self, w, h):
        self.world_w, self.world_h = w, h

    def _target(self, rect, look_dy=0.0):
        tx = rect.centerx - S.GAME_W / 2
        ty = rect.centery - S.GAME_H / 2 + look_dy
        tx = max(0, min(tx, max(0, self.world_w - S.GAME_W)))
        ty = max(0, min(ty, max(0, self.world_h - S.GAME_H)))
        return tx, ty

    def snap(self, rect):
        self.x, self.y = self._target(rect)

    def update(self, dt, rect, look_dy=0.0):
        tx, ty = self._target(rect, look_dy)
        k = min(1.0, dt * 7.0)
        self.x += (tx - self.x) * k
        self.y += (ty - self.y) * k
        if self.shake_time > 0:
            self.shake_time -= dt
            p = self.shake_power * (self.shake_time / 0.35 if self.shake_time < 0.35 else 1)
            self.offset = (random.uniform(-p, p), random.uniform(-p, p))
        else:
            self.offset = (0, 0)

    def shake(self, power=3.0, time=0.28):
        self.shake_power = max(self.shake_power, power)
        self.shake_time = max(self.shake_time, time)

    @property
    def ox(self):
        return self.x + self.offset[0]

    @property
    def oy(self):
        return self.y + self.offset[1]

    def to_screen(self, x, y):
        return int(x - self.ox), int(y - self.oy)

    def apply(self, rect):
        return rect.move(-int(self.ox), -int(self.oy))
