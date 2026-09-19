"""Entrada unificada: teclado y controles tactiles.

El gameplay solo consulta acciones ("left", "jump", ...) y nunca al teclado
directamente, de modo que la misma logica sirve en PC y en movil.
"""
import pygame

from . import settings as S
from . import ui

ACTIONS = ("left", "right", "up", "down", "jump", "attack", "interact", "pause")

KEYMAP = {
    "left": (pygame.K_a, pygame.K_LEFT),
    "right": (pygame.K_d, pygame.K_RIGHT),
    "up": (pygame.K_w, pygame.K_UP),
    "down": (pygame.K_s, pygame.K_DOWN),
    "jump": (pygame.K_SPACE, pygame.K_w, pygame.K_UP, pygame.K_z),
    "attack": (pygame.K_x, pygame.K_j),
    "interact": (pygame.K_e, pygame.K_RETURN),
    "pause": (pygame.K_ESCAPE,),
}


class KeyboardInput:
    def __init__(self):
        self.state = {a: False for a in ACTIONS}

    def update(self):
        keys = pygame.key.get_pressed()
        for action, codes in KEYMAP.items():
            self.state[action] = any(keys[c] for c in codes)
        return self.state


class TouchButton:
    def __init__(self, action, rect, label, kind="round"):
        self.action = action
        self.rect = pygame.Rect(rect)
        self.label = label
        self.kind = kind
        self.pressed = False

    def draw(self, surf):
        alpha = 150 if not self.pressed else 220
        pad = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        r = pad.get_rect()
        base = (250, 244, 220, alpha)
        edge = (60, 48, 60, min(255, alpha + 40))
        pygame.draw.rect(pad, edge, r, border_radius=4)
        pygame.draw.rect(pad, base, r.inflate(-4, -4), border_radius=3)
        pygame.draw.rect(pad, (255, 214, 74, alpha), r.inflate(-4, -4), 1, border_radius=3)
        surf.blit(pad, self.rect.topleft)
        cx, cy = self.rect.center
        col = (48, 40, 52)
        if self.label == "<":
            pygame.draw.polygon(surf, col, [(cx + 4, cy - 6), (cx + 4, cy + 6), (cx - 5, cy)])
        elif self.label == ">":
            pygame.draw.polygon(surf, col, [(cx - 4, cy - 6), (cx - 4, cy + 6), (cx + 5, cy)])
        elif self.label == "^":
            pygame.draw.polygon(surf, col, [(cx - 6, cy + 4), (cx + 6, cy + 4), (cx, cy - 6)])
        elif self.label == "v":
            pygame.draw.polygon(surf, col, [(cx - 6, cy - 4), (cx + 6, cy - 4), (cx, cy + 6)])
        else:
            ui.text(surf, self.label, (cx, cy - 6), 11, col, shadow=None, center=True)


class TouchInput:
    """Botones tactiles dibujados en pixel art, con transparencia."""

    def __init__(self):
        h = S.GAME_H
        self.buttons = [
            TouchButton("left", (8, h - 46, 34, 34), "<"),
            TouchButton("right", (48, h - 46, 34, 34), ">"),
            TouchButton("down", (28, h - 84, 34, 34), "v"),
            TouchButton("jump", (S.GAME_W - 50, h - 46, 40, 36), "SALTO"),
            TouchButton("attack", (S.GAME_W - 96, h - 46, 40, 36), "FLOR"),
            TouchButton("interact", (S.GAME_W - 74, h - 88, 40, 32), "E"),
        ]
        self.fingers = {}
        self.enabled = False

    def _hit(self, pos):
        for b in self.buttons:
            if b.rect.collidepoint(pos):
                return b
        return None

    def handle(self, event, to_internal):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self.enabled = True
            pos = (event.x * S.GAME_W, event.y * S.GAME_H)
            if event.type == pygame.FINGERUP:
                self.fingers.pop(event.finger_id, None)
            else:
                self.fingers[event.finger_id] = pos
        elif event.type == pygame.MOUSEBUTTONDOWN and self.enabled:
            self.fingers["mouse"] = to_internal(event.pos)
        elif event.type == pygame.MOUSEMOTION and "mouse" in self.fingers:
            self.fingers["mouse"] = to_internal(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.fingers.pop("mouse", None)

    def update(self):
        state = {a: False for a in ACTIONS}
        for b in self.buttons:
            b.pressed = False
        for pos in self.fingers.values():
            b = self._hit(pos)
            if b:
                b.pressed = True
                state[b.action] = True
        return state

    def draw(self, surf):
        if not self.enabled:
            return
        for b in self.buttons:
            b.draw(surf)


class InputManager:
    def __init__(self):
        self.keyboard = KeyboardInput()
        self.touch = TouchInput()
        self.state = {a: False for a in ACTIONS}
        self.prev = dict(self.state)
        self.touch_mode = False

    def handle_event(self, event, to_internal):
        self.touch.handle(event, to_internal)
        if self.touch.enabled:
            self.touch_mode = True

    def update(self):
        self.prev = dict(self.state)
        keys = self.keyboard.update()
        touch = self.touch.update()
        self.state = {a: keys[a] or touch[a] for a in ACTIONS}
        return self.state

    def down(self, action):
        return self.state.get(action, False)

    def pressed(self, action):
        return self.state.get(action, False) and not self.prev.get(action, False)

    def released(self, action):
        return not self.state.get(action, False) and self.prev.get(action, False)

    def draw(self, surf):
        self.touch.draw(surf)
