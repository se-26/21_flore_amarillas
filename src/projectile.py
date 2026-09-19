"""Proyectiles: flores del jugador y disparos enemigos."""
import pygame

from . import settings as S


class Projectile:
    def __init__(self, frames, x, y, vx, vy, owner="player", damage=1, life=2.2):
        self.frames = frames
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.owner = owner
        self.damage = damage
        self.life = life
        self.dead = False
        self.t = 0.0
        self.trail = 0.0

    @property
    def rect(self):
        w, h = self.frames[0].get_size()
        return pygame.Rect(int(self.x - w / 2), int(self.y - h / 2), w, h)

    def update(self, dt, level, particles):
        self.t += dt
        self.life -= dt
        if self.life <= 0:
            self.dead = True
        if self.owner == "player":
            self.vy += 120 * dt          # ligera caida
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trail -= dt
        if self.trail <= 0:
            self.trail = 0.04
            particles.sparkle(self.x, self.y, 1,
                              S.GOLD if self.owner == "player" else (196, 160, 255))
        if level.collides_solid(self.rect):
            self.explode(particles)

    def explode(self, particles):
        if self.dead:
            return
        self.dead = True
        color = S.YELLOW if self.owner == "player" else (176, 140, 255)
        particles.burst(self.x, self.y, color, 10, 70, 0.5, 1, 40)

    def draw(self, surf, camera):
        img = self.frames[int(self.t * 16) % len(self.frames)]
        surf.blit(img, camera.to_screen(self.x - img.get_width() / 2,
                                        self.y - img.get_height() / 2))
