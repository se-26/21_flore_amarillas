"""Menus: principal, seleccion de personaje y destinatario, ajustes y pausa."""
import math
import random

import pygame

from . import settings as S
from . import ui

CONTROLS = [
    ("A / D  o  <  >", "Moverse"),
    ("ESPACIO / W", "Saltar (x2: salta mas alto)"),
    ("S / abajo", "Agacharse"),
    ("X", "Atacar / lanzar flor"),
    ("E", "Interactuar y hablar"),
    ("SHIFT", "Correr"),
    ("ESC", "Pausa"),
]


class PetalBackdrop:
    """Fondo animado de petalos amarillos, compartido por los menus."""

    def __init__(self, n=60):
        self.p = [[random.uniform(0, S.GAME_W), random.uniform(-S.GAME_H, S.GAME_H),
                   random.uniform(9, 24), random.random() * 6] for _ in range(n)]
        self.t = 0.0

    def update(self, dt):
        self.t += dt
        for q in self.p:
            q[1] += q[2] * dt
            q[0] += math.sin(q[3] + self.t) * 9 * dt
            if q[1] > S.GAME_H:
                q[1] = -6
                q[0] = random.uniform(0, S.GAME_W)

    def draw(self, surf, c1=(120, 190, 236), c2=(252, 232, 178)):
        for y in range(S.GAME_H):
            k = y / S.GAME_H
            surf.fill((int(c1[0] + (c2[0] - c1[0]) * k),
                       int(c1[1] + (c2[1] - c1[1]) * k),
                       int(c1[2] + (c2[2] - c1[2]) * k)), (0, y, S.GAME_W, 1))
        pygame.draw.ellipse(surf, (108, 178, 96), (-70, 156, 320, 150))
        pygame.draw.ellipse(surf, (132, 200, 108), (170, 168, 360, 150))
        pygame.draw.rect(surf, (96, 166, 88), (0, 202, S.GAME_W, 18))
        for q in self.p:
            pygame.draw.rect(surf, S.GOLD, (int(q[0]), int(q[1]), 2, 2))


class ListMenu:
    """Menu vertical reutilizable con soporte de teclado y toque."""

    def __init__(self, game, options):
        self.game = game
        self.options = options
        self.index = 0
        self.rects = []

    def move(self, d):
        self.index = (self.index + d) % len(self.options)
        self.game.audio.play("menu_select")

    def handle(self, event, to_internal=None):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move(1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.on_side(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.on_side(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_x):
                self.confirm()
            elif event.key == pygame.K_ESCAPE:
                self.cancel()
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if event.type == pygame.FINGERDOWN:
                w, h = pygame.display.get_surface().get_size()
                pos = to_internal((event.x * w, event.y * h)) if to_internal \
                    else (event.x * S.GAME_W, event.y * S.GAME_H)
            else:
                pos = to_internal(event.pos) if to_internal else event.pos
            for i, r in enumerate(self.rects):
                if r.collidepoint(pos):
                    self.index = i
                    self.confirm()
                    break

    def on_side(self, d):
        pass

    def cancel(self):
        pass

    def confirm(self):
        self.game.audio.play("menu_confirm")

    def draw_options(self, surf, top, gap=22, size=15, width=180):
        self.rects = []
        for i, opt in enumerate(self.options):
            y = top + i * gap
            box = pygame.Rect(0, 0, width, gap - 2)
            box.center = (S.GAME_W // 2, y + 7)
            self.rects.append(box)
            if i == self.index:
                ui.panel(surf, box, fill=(44, 36, 58), alpha=215)
            ui.title(surf, opt, (S.GAME_W // 2, y), size,
                     S.GOLD if i == self.index else S.CREAM)


class MainMenu(ListMenu):
    def __init__(self, game):
        super().__init__(game, ["JUGAR", "CONTINUAR", "CONFIGURACION", "SALIR"])
        self.bg = PetalBackdrop()

    def update(self, dt):
        self.bg.update(dt)

    def confirm(self):
        self.game.audio.play("menu_confirm")
        opt = self.options[self.index]
        if opt == "JUGAR":
            self.game.state = "char_select"
        elif opt == "CONTINUAR":
            if not self.game.continue_game():
                self.game.notify("No hay progreso guardado todavia")
        elif opt == "CONFIGURACION":
            self.game.open_settings("menu")
        else:
            self.game.running = False

    def draw(self, surf):
        self.bg.draw(surf)
        art = self.game.art
        surf.blit(art.sunflower[0], (34, 22))
        surf.blit(art.sunflower[2], (S.GAME_W - 56, 22))
        ui.title(surf, "21 DE SEPTIEMBRE", (S.GAME_W // 2, 18), 26, S.CREAM)
        ui.title(surf, "FLORES PARA TI", (S.GAME_W // 2, 48), 18, S.YELLOW)
        self.draw_options(surf, 86)


class CharacterSelect(ListMenu):
    def __init__(self, game):
        super().__init__(game, ["flora", "sol"])
        self.bg = PetalBackdrop(40)
        self.t = 0.0

    def update(self, dt):
        self.bg.update(dt)
        self.t += dt

    def on_side(self, d):
        self.index = (self.index + d) % 2
        self.game.audio.play("menu_select")

    def move(self, d):
        self.on_side(d)

    def cancel(self):
        self.game.state = "menu"

    def confirm(self):
        self.game.audio.play("menu_confirm")
        self.game.progress.hero = self.options[self.index]
        self.game.state = "target_select"

    def draw(self, surf):
        self.bg.draw(surf, (150, 190, 240), (250, 226, 180))
        ui.title(surf, "ELIGE A TU PERSONAJE", (S.GAME_W // 2, 18), 20, S.CREAM)
        names = {"flora": "SELENA", "sol": "LUKE"}
        self.rects = []
        for i, key in enumerate(self.options):
            cx = S.GAME_W // 2 + (-70 if i == 0 else 70)
            box = pygame.Rect(0, 0, 96, 108)
            box.center = (cx, 118)
            self.rects.append(box)
            ui.panel(surf, box, fill=(44, 38, 58),
                     alpha=230 if i == self.index else 170,
                     accent=S.YELLOW if i == self.index else S.STONE_D)
            frames = self.game.art.heroes[key]
            pose = "celebrate" if i == self.index else "idle"
            img = frames[pose][int(self.t * 4) % len(frames[pose])]
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            surf.blit(img, img.get_rect(center=(cx, 108)))
            ui.title(surf, names[key], (cx, box.bottom - 22), 14,
                     S.GOLD if i == self.index else S.CREAM)
        ui.text(surf, "Ambos tienen exactamente las mismas habilidades.",
                (S.GAME_W // 2, S.GAME_H - 30), 11, S.INK, shadow=None, center=True)
        ui.text(surf, "< >  elegir     ENTER  confirmar",
                (S.GAME_W // 2, S.GAME_H - 16), 11, S.INK, shadow=None, center=True)


class TargetSelect(CharacterSelect):
    def __init__(self, game):
        ListMenu.__init__(self, game, ["dama", "caballero"])
        self.bg = PetalBackdrop(40)
        self.t = 0.0

    def cancel(self):
        self.game.state = "char_select"

    def confirm(self):
        self.game.audio.play("menu_confirm")
        self.game.progress.target = self.options[self.index]
        self.game.start_new_game()

    def draw(self, surf):
        self.bg.draw(surf, (236, 170, 190), (252, 232, 190))
        ui.title(surf, "¿A QUIEN LE ENTREGARAS LAS FLORES?",
                 (S.GAME_W // 2, 16), 16, S.CREAM)
        names = {"dama": "LUCIA", "caballero": "JEFF"}
        self.rects = []
        for i, key in enumerate(self.options):
            cx = S.GAME_W // 2 + (-70 if i == 0 else 70)
            box = pygame.Rect(0, 0, 96, 108)
            box.center = (cx, 118)
            self.rects.append(box)
            ui.panel(surf, box, fill=(52, 38, 54),
                     alpha=230 if i == self.index else 170,
                     accent=S.YELLOW if i == self.index else S.STONE_D)
            frames = self.game.art.targets[key]
            pose = "celebrate" if i == self.index else "idle"
            img = frames[pose][int(self.t * 4) % len(frames[pose])]
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            surf.blit(img, img.get_rect(center=(cx, 108)))
            ui.title(surf, names[key], (cx, box.bottom - 22), 13,
                     S.GOLD if i == self.index else S.CREAM)
        ui.text(surf, "Cualquier combinacion es valida. Solo cambia quien te espera.",
                (S.GAME_W // 2, S.GAME_H - 30), 11, S.INK, shadow=None, center=True)
        ui.text(surf, "< >  elegir     ENTER  confirmar     ESC  volver",
                (S.GAME_W // 2, S.GAME_H - 16), 11, S.INK, shadow=None, center=True)


class SettingsMenu(ListMenu):
    def __init__(self, game):
        super().__init__(game, ["MUSICA", "EFECTOS", "VOLUMEN MUSICA",
                                "VOLUMEN EFECTOS", "VOLVER"])
        self.origin = "menu"

    def cancel(self):
        self.game.close_settings()

    def on_side(self, d):
        a = self.game.audio
        opt = self.options[self.index]
        if opt == "MUSICA":
            a.set_music_on(not a.music_on)
        elif opt == "EFECTOS":
            a.set_sfx_on(not a.sfx_on)
        elif opt == "VOLUMEN MUSICA":
            a.set_music_volume(a.music_volume + 0.1 * d)
        elif opt == "VOLUMEN EFECTOS":
            a.set_sfx_volume(a.sfx_volume + 0.1 * d)
        self.game.audio.play("menu_select")
        self.game.save_game()

    def confirm(self):
        if self.options[self.index] == "VOLVER":
            self.game.audio.play("menu_confirm")
            self.game.close_settings()
        else:
            self.on_side(1)

    def draw(self, surf, background=None):
        overlay = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        overlay.fill((14, 12, 22, 190))
        surf.blit(overlay, (0, 0))
        box = pygame.Rect(0, 0, 268, 160)
        box.center = (S.GAME_W // 2, S.GAME_H // 2)
        ui.panel(surf, box)
        ui.title(surf, "CONFIGURACION", (box.centerx, box.y + 8), 17, S.GOLD)
        a = self.game.audio
        values = [
            "SI" if a.music_on else "NO",
            "SI" if a.sfx_on else "NO",
            f"{int(a.music_volume * 100)}%",
            f"{int(a.sfx_volume * 100)}%",
            "",
        ]
        self.rects = []
        for i, opt in enumerate(self.options):
            y = box.y + 38 + i * 21
            row = pygame.Rect(box.x + 10, y - 3, box.w - 20, 19)
            self.rects.append(row)
            if i == self.index:
                ui.panel(surf, row, fill=(60, 50, 76), alpha=200, shadow=False)
            ui.text(surf, opt, (box.x + 24, y), 12,
                    S.GOLD if i == self.index else S.CREAM)
            if values[i]:
                ui.text(surf, f"<  {values[i]}  >" if i == self.index else values[i],
                        (box.right - 24, y), 12,
                        S.YELLOW if i == self.index else S.CREAM_D, right=True)
        ui.text(surf, "Los ajustes se guardan automaticamente",
                (box.centerx, box.bottom - 16), 10, S.STONE_L, center=True)


class PauseMenu(ListMenu):
    def __init__(self, game):
        super().__init__(game, ["CONTINUAR", "REINICIAR NIVEL",
                                "VOLUMEN MUSICA", "VOLUMEN EFECTOS",
                                "CONFIGURACION", "CONTROLES", "SALIR AL MENU"])

    def on_side(self, d):
        a = self.game.audio
        opt = self.options[self.index]
        if opt == "VOLUMEN MUSICA":
            a.set_music_volume(a.music_volume + 0.1 * d)
        elif opt == "VOLUMEN EFECTOS":
            a.set_sfx_volume(a.sfx_volume + 0.1 * d)
        else:
            return
        self.game.audio.play("menu_select")
        self.game.save_game()

    def cancel(self):
        self.game.state = "play"

    def confirm(self):
        self.game.audio.play("menu_confirm")
        opt = self.options[self.index]
        if opt == "CONTINUAR":
            self.game.state = "play"
        elif opt == "REINICIAR NIVEL":
            self.game.start_level(self.game.progress.level_index)
        elif opt in ("VOLUMEN MUSICA", "VOLUMEN EFECTOS"):
            self.on_side(1)
        elif opt == "CONFIGURACION":
            self.game.open_settings("pause")
        elif opt == "CONTROLES":
            self.game.prev_state = "pause"
            self.game.state = "controls"
        else:
            self.game.save_game()
            self.game.go_to_menu()

    def draw(self, surf):
        overlay = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        overlay.fill((14, 12, 22, 170))
        surf.blit(overlay, (0, 0))
        box = pygame.Rect(0, 0, 280, 196)
        box.center = (S.GAME_W // 2, S.GAME_H // 2)
        ui.panel(surf, box)
        ui.title(surf, "PAUSA", (box.centerx, box.y + 8), 20, S.GOLD)
        a = self.game.audio
        values = {"VOLUMEN MUSICA": f"{int(a.music_volume * 100)}%",
                  "VOLUMEN EFECTOS": f"{int(a.sfx_volume * 100)}%"}
        self.rects = []
        for i, opt in enumerate(self.options):
            y = box.y + 38 + i * 19
            row = pygame.Rect(box.x + 10, y - 3, box.w - 20, 18)
            self.rects.append(row)
            if i == self.index:
                ui.panel(surf, row, fill=(60, 50, 76), alpha=200, shadow=False)
            if opt in values:
                ui.text(surf, opt, (box.x + 18, y), 12,
                        S.GOLD if i == self.index else S.CREAM)
                ui.text(surf, f"<  {values[opt]}  >" if i == self.index else values[opt],
                        (box.right - 18, y), 12,
                        S.YELLOW if i == self.index else S.CREAM_D, right=True)
            else:
                ui.text(surf, opt, (box.centerx, y), 12,
                        S.GOLD if i == self.index else S.CREAM, center=True)


class ControlsScreen:
    def __init__(self, game):
        self.game = game

    def handle(self, event, to_internal=None):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            self.game.state = self.game.prev_state or "menu"

    def draw(self, surf):
        overlay = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        overlay.fill((14, 12, 22, 190))
        surf.blit(overlay, (0, 0))
        box = pygame.Rect(0, 0, 280, 166)
        box.center = (S.GAME_W // 2, S.GAME_H // 2)
        ui.panel(surf, box)
        ui.title(surf, "CONTROLES", (box.centerx, box.y + 8), 17, S.GOLD)
        y = box.y + 34
        for key, desc in CONTROLS:
            ui.text(surf, key, (box.x + 18, y), 12, S.YELLOW)
            ui.text(surf, desc, (box.x + 140, y), 12, S.CREAM)
            y += 16


class DeathScreen(ListMenu):
    def __init__(self, game):
        super().__init__(game, ["REINICIAR NIVEL", "SALIR AL MENU"])
        self.t = 0.0

    def reset(self):
        self.index = 0
        self.t = 0.0

    def update(self, dt):
        self.t += dt

    def confirm(self):
        self.game.audio.play("menu_confirm")
        if self.index == 0:
            self.game.restart_level()
        else:
            self.game.save_game()
            self.game.go_to_menu()

    def draw(self, surf):
        overlay = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        overlay.fill((20, 10, 24, min(210, int(self.t * 500))))
        surf.blit(overlay, (0, 0))
        ui.title(surf, "OH NO...", (S.GAME_W // 2, 48), 24, S.HEART_RED)
        ui.title(surf, "Las flores todavia te necesitan.",
                 (S.GAME_W // 2, 84), 14, S.CREAM)
        self.draw_options(surf, 128, 22, 14, 190)


class LevelCompleteScreen(ListMenu):
    def __init__(self, game):
        super().__init__(game, ["CONTINUAR"])
        self.t = 0.0
        self.data = None

    def start(self, data, flowers):
        self.t = 0.0
        self.data = data
        self.flowers = flowers
        self.index = 0

    def update(self, dt):
        self.t += dt

    def confirm(self):
        self.game.audio.play("menu_confirm")
        self.game.next_level()

    def draw(self, surf):
        overlay = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        overlay.fill((14, 12, 22, 180))
        surf.blit(overlay, (0, 0))
        box = pygame.Rect(0, 0, 280, 120)
        box.center = (S.GAME_W // 2, S.GAME_H // 2 - 6)
        ui.panel(surf, box)
        ui.title(surf, "¡NIVEL COMPLETADO!", (box.centerx, box.y + 10), 18, S.GOLD)
        if self.data:
            ui.text(surf, f"NIVEL {self.data.number} - {self.data.name}",
                    (box.centerx, box.y + 38), 12, S.CREAM, center=True)
        ui.text(surf, f"Flores recogidas: {self.flowers}",
                (box.centerx, box.y + 56), 12, S.YELLOW, center=True)
        ui.text(surf, f"Flores totales: {self.game.progress.total_flowers}",
                (box.centerx, box.y + 72), 12, S.CREAM, center=True)
        self.draw_options(surf, box.bottom + 8, 20, 14, 150)
