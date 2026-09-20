"""Escenas especiales: poder del girasol, entrega del ramo y pantalla final."""
import math
import random

import pygame

from . import settings as S
from . import ui
from .menu import ListMenu, PetalBackdrop


class PowerUnlockScene:
    """Animacion al descubrir el poder del girasol."""

    def __init__(self, game, sunflower):
        self.game = game
        self.sun = sunflower
        self.t = 0.0
        self.phase = 0
        game.audio.play("sunflower_power")

    def update(self, dt):
        self.t += dt
        cx, cy = self.sun.rect.centerx, self.sun.rect.centery - 6
        if self.t < 1.4:
            if random.random() < dt * 40:
                a = random.uniform(0, 6.28)
                r = 26
                cx2 = cx + math.cos(a) * r
                cy2 = cy + math.sin(a) * r
                self.game.particles.sparkle(cx2, cy2, 2)
            self.game.camera.shake(1.2, 0.1)
        elif self.phase == 0:
            self.phase = 1
            self.game.particles.burst(cx, cy, S.GOLD, 40, 130, 1.0, 2, 30)
            self.game.progress.unlock_power()
            self.game.camera.shake(4, 0.4)
        if self.t > 3.6:
            self.game.end_power_scene()

    def draw(self, surf, camera):
        glow = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        k = min(1.0, self.t / 1.4)
        glow.fill((255, 226, 130, int(60 + 90 * k)))
        surf.blit(glow, (0, 0))
        if self.t > 1.4:
            ui.title(surf, "¡PODER DEL GIRASOL", (S.GAME_W // 2, 60), 20, S.CREAM)
            ui.title(surf, "DESBLOQUEADO!", (S.GAME_W // 2, 84), 20, S.CREAM)
            ui.title(surf, "Pulsa X para lanzar flores",
                     (S.GAME_W // 2, 116), 13, S.GOLD)


class FinalScene:
    """Entrega del ramo en el jardin final."""

    TEXTS = [
        ("Feliz 21 de septiembre", 0.6),
        ("Este ramo es para ti.", 2.0),
        ("Gracias por acompañarme en el camino.", 3.4),
    ]

    def __init__(self, game, target_x, target_y):
        self.game = game
        self.t = 0.0
        self.phase = 0
        self.tx, self.ty = target_x, target_y
        self.petals = []
        self.bouquet_t = 0.0
        self.target_t = 0.0
        self.zoom0 = 1.0
        self.zoom_out_t = 0.0

    def update(self, dt):
        self.t += dt
        self.target_t += dt
        p = self.game.player
        if self.phase == 0:
            p.celebrating = False
            dx = self.tx - 26 - p.rect.centerx
            if abs(dx) > 3:
                p.vx = 60 if dx > 0 else -60
                p.facing = 1 if dx > 0 else -1
            else:
                p.vx = 0
                self.phase = 1
                self.t = 0.0
                self.game.audio.play("final_bouquet")
                self.game.audio.play_final_song()
        elif self.phase == 1:
            p.vx = 0
            p.celebrating = True
            self.bouquet_t += dt
            target_zoom = 1.0 + 0.16 * min(1.0, self.bouquet_t / 1.6)
            self.game.zoom += (target_zoom - self.game.zoom) * min(1.0, dt * 2.5)
            if self.bouquet_t > 1.6:
                self.phase = 2
                self.t = 0.0
                self.zoom0 = self.game.zoom
                self.zoom_out_t = 0.0
        else:
            p.vx = 0
            if self.zoom_out_t < 0.55:
                self.zoom_out_t += dt
                k = min(1.0, self.zoom_out_t / 0.55)
                self.game.zoom = 1.0 + (self.zoom0 - 1.0) * (1.0 - k)
                if k >= 1.0:
                    self.game.zoom = 1.0
            if random.random() < dt * 70:
                cam = self.game.camera
                self.petals.append([cam.x + random.uniform(0, S.GAME_W), cam.y - 6,
                                    random.uniform(16, 40), random.random() * 6])
            if self.t > 6.5:
                self.game.zoom = 1.0
                self.game.state = "ending"
        for q in self.petals:
            q[1] += q[2] * dt
            q[0] += math.sin(q[3] + self.t) * 12 * dt

    def draw_overlay(self, surf, camera):
        warm = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        strength = 40 if self.phase == 0 else min(110, 40 + int(self.t * 45))
        warm.fill((255, 190, 100, strength))
        surf.blit(warm, (0, 0))
        for q in self.petals:
            x, y = camera.to_screen(q[0], q[1])
            pygame.draw.rect(surf, S.GOLD, (x, y, 2, 2))
        if self.phase >= 1:
            img = self.game.art.bouquet
            k = min(1.0, self.bouquet_t / 1.2)
            w = max(4, int(img.get_width() * k))
            h = max(4, int(img.get_height() * k))
            sc = pygame.transform.scale(img, (w, h))
            x, y = camera.to_screen(self.tx - 26, self.ty - 30)
            surf.blit(sc, (x, y - h // 2))
        if self.phase >= 2:
            for i, (msg, delay) in enumerate(self.TEXTS):
                if self.t > delay:
                    ui.title(surf, msg, (S.GAME_W // 2, 28 + i * 26),
                             20 if i == 0 else 14, S.CREAM)

    def draw_target(self, surf, camera):
        frames = self.game.art.targets[self.game.progress.target]
        pose = "celebrate" if self.phase >= 1 else "idle"
        seq = frames[pose]
        img = seq[int(self.target_t * 4) % len(seq)]
        img = pygame.transform.flip(img, True, False)
        surf.blit(img, camera.to_screen(self.tx - img.get_width() // 2,
                                        self.ty - img.get_height()))


class EndingScreen(ListMenu):
    def __init__(self, game):
        super().__init__(game, ["JUGAR DE NUEVO", "SALIR"])
        self.bg = PetalBackdrop(70)
        self.t = 0.0

    def update(self, dt):
        self.t += dt
        self.bg.update(dt)

    def confirm(self):
        self.game.audio.play("menu_confirm")
        if self.index == 0:
            self.game.state = "char_select"
        else:
            self.game.running = False

    def draw(self, surf):
        self.bg.draw(surf, (252, 186, 120), (255, 238, 190))
        surf.blit(self.game.art.bouquet,
                  (S.GAME_W // 2 - 17, 26 + int(math.sin(self.t) * 2)))
        ui.title(surf, "FIN", (S.GAME_W // 2, 74), 26, S.CREAM)
        ui.title(surf, "juego creado por selena", (S.GAME_W // 2, 104), 14, S.CREAM)
        p = self.game.progress
        ui.text(surf, f"Flores totales: {p.total_flowers}    Caidas: {p.deaths}",
                (S.GAME_W // 2, 126), 11, (110, 72, 40), shadow=None, center=True)
        self.draw_options(surf, 148, 22, 14, 180)
