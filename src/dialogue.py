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

    def _box(self):
        return pygame.Rect(14, S.GAME_H - 74, S.GAME_W - 28, 62)

    def button_rect(self):
        """Boton 'continuar' (flecha/FIN) en la esquina inferior derecha."""
        box = self._box()
        return pygame.Rect(box.right - 38, box.bottom - 27, 26, 22)

    def draw(self, surf):
        if not self.active:
            return
        box = self._box()
        ui.panel(surf, box, fill=(40, 34, 54), alpha=238)

        tx = box.x + 10
        if self.name:
            tag = pygame.Rect(box.x + 6, box.y - 10, ui.get_font(12).size(self.name)[0] + 16, 16)
            ui.panel(surf, tag, fill=(70, 52, 42), alpha=245, accent=S.YELLOW)
            ui.text(surf, self.name, (tag.centerx, tag.y + 2), 12, S.GOLD, center=True)

        # deja espacio libre para el boton ▶ de la esquina inferior derecha
        shown = self.current[:int(self.revealed)]
        lines = ui.wrap(shown, 12, box.w - 52)
        for i, line in enumerate(lines[:3]):
            ui.text(surf, line, (tx, box.y + 13 + i * 15), 12, S.CREAM)

        if self.finished_page():
            import math
            br = self.button_rect()
            last = self.index >= len(self.pages) - 1
            pulse = int(210 + 45 * math.sin(self.arrow_t))
            pad = pygame.Surface(br.size, pygame.SRCALPHA)
            rb = pad.get_rect()
            pygame.draw.rect(pad, (18, 14, 24, 110), rb.move(1, 2), border_radius=9)
            accent = S.ORANGE if last else S.YELLOW
            pygame.draw.rect(pad, (*accent, 255), rb, border_radius=9)
            pygame.draw.rect(pad, (56, 44, 66, pulse), rb.inflate(-2, -2), border_radius=8)
            surf.blit(pad, br.topleft)
            if last:
                ui.text(surf, "FIN", (br.centerx, br.centery - 5), 9, S.GOLD,
                        center=True, alpha=pulse)
            else:
                cx, cy = br.centerx, br.centery
                pygame.draw.polygon(surf, (255, 244, 214),
                                    [(cx - 4, cy - 6), (cx - 4, cy + 6), (cx + 5, cy)])
                pygame.draw.polygon(surf, S.YELLOW,
                                    [(cx - 4, cy - 6), (cx - 4, cy + 6), (cx + 5, cy)], 1)
