"""Sistema de dialogos con caja pixel art y efecto maquina de escribir."""
import pygame

from . import settings as S
from . import ui

CHARS_PER_SEC = 42.0


class DialogueSystem:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.name = ""
        self.pages = []
        self.index = 0
        self.revealed = 0.0
        self.on_end = None
        self.arrow_t = 0.0
        self.portrait = None

    def start(self, name, pages, on_end=None, portrait=None):
        self.active = True
        self.name = name
        self.pages = list(pages)
        self.index = 0
        self.revealed = 0.0
        self.on_end = on_end
        self.portrait = portrait
        self.game.audio.play("dialogue")

    @property
    def current(self):
        return self.pages[self.index] if self.index < len(self.pages) else ""

    def finished_page(self):
        return self.revealed >= len(self.current)

    def advance(self):
        if not self.active:
            return
        if not self.finished_page():
            self.revealed = len(self.current)
            return
        self.index += 1
        self.revealed = 0.0
        if self.index >= len(self.pages):
            self.active = False
            cb, self.on_end = self.on_end, None
            if cb:
                cb()
        else:
            self.game.audio.play("dialogue")

    def update(self, dt):
        if not self.active:
            return
        self.arrow_t += dt * 4
        if not self.finished_page():
            self.revealed += CHARS_PER_SEC * dt

    def draw(self, surf):
        if not self.active:
            return
        box = pygame.Rect(14, S.GAME_H - 74, S.GAME_W - 28, 62)
        ui.panel(surf, box, fill=(40, 34, 54), alpha=238)

        tx = box.x + 10
        if self.name:
            tag = pygame.Rect(box.x + 6, box.y - 10, ui.get_font(12).size(self.name)[0] + 16, 16)
            ui.panel(surf, tag, fill=(70, 52, 42), alpha=245, accent=S.YELLOW)
            ui.text(surf, self.name, (tag.centerx, tag.y + 2), 12, S.GOLD, center=True)

        shown = self.current[:int(self.revealed)]
        lines = ui.wrap(shown, 12, box.w - 28)
        for i, line in enumerate(lines[:3]):
            ui.text(surf, line, (tx, box.y + 13 + i * 15), 12, S.CREAM)

        if self.finished_page():
            import math
            off = int(math.sin(self.arrow_t) * 1.5)
            ax, ay = box.right - 14, box.bottom - 13 + off
            pygame.draw.polygon(surf, S.YELLOW,
                                [(ax, ay), (ax + 7, ay), (ax + 3, ay + 5)])
            pygame.draw.polygon(surf, S.DARK,
                                [(ax, ay), (ax + 7, ay), (ax + 3, ay + 5)], 1)
