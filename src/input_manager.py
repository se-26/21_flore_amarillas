"""Entrada unificada: teclado (PC) e input tactil (web/movil).

El gameplay solo consulta acciones ("left", "jump", ...) y nunca al teclado
directamente. En movil los botones virtuales semi-transparentes se dibujan en
las esquinas inferiores (pantalla horizontal) y solo se muestran y responden
mientras el jugador se mueve por el mundo: si hay un dialogo o caja de texto
activo, los botones se ocultan para no tapar la lectura.
"""
import os

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
    """Boton virtual semi-transparente estilo pixel art."""

    def __init__(self, action, rect, label):
        self.action = action
        self.rect = pygame.Rect(rect)
        self.label = label
        self.pressed = False

    def draw(self, surf):
        alpha = 120 if not self.pressed else 210
        pad = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        r = pad.get_rect()
        base = (250, 244, 220, alpha)
        edge = (60, 48, 60, min(255, alpha + 40))
        pygame.draw.rect(pad, edge, r, border_radius=6)
        pygame.draw.rect(pad, base, r.inflate(-4, -4), border_radius=5)
        pygame.draw.rect(pad, (255, 214, 74, alpha), r.inflate(-4, -4),
                         1, border_radius=5)
        surf.blit(pad, self.rect.topleft)
        cx, cy = self.rect.center
        col = (48, 40, 52)
        if self.label == "<":
            pygame.draw.polygon(surf, col, [(cx + 5, cy - 7), (cx + 5, cy + 7), (cx - 6, cy)])
        elif self.label == ">":
            pygame.draw.polygon(surf, col, [(cx - 5, cy - 7), (cx - 5, cy + 7), (cx + 6, cy)])
        elif self.label == "^":
            pygame.draw.polygon(surf, col, [(cx - 7, cy + 5), (cx + 7, cy + 5), (cx, cy - 6)])
        elif self.label == "v":
            pygame.draw.polygon(surf, col, [(cx - 7, cy - 5), (cx + 7, cy - 5), (cx, cy + 6)])
        else:
            ui.text(surf, self.label, (cx, cy - 7), 10, col, shadow=None, center=True)


class TouchInput:
    """Botones tactiles de las esquinas inferiores (pantalla horizontal).

    Solo se dibujan y quedan activos con set_visible(True), que el juego
    activa cada frame mientras el jugador recorre el mundo sin dialogos.
    """

    def __init__(self, enabled):
        self.enabled = enabled or os.environ.get("TOUCH_TEST") == "1"
        h = S.GAME_H
        self.buttons = [
            TouchButton("left", (8, h - 46, 34, 34), "<"),
            TouchButton("right", (48, h - 46, 34, 34), ">"),
            TouchButton("jump", (10, h - 88, 34, 34), "^"),
            TouchButton("attack", (S.GAME_W - 96, h - 46, 40, 36), "FLOR"),
            TouchButton("down", (S.GAME_W - 52, h - 88, 36, 32), "v"),
            TouchButton("interact", (S.GAME_W - 136, h - 88, 38, 32), "E"),
        ]
        self.fingers = {}
        self.visible = False

    def set_visible(self, flag):
        if not self.enabled:
            return
        self.visible = bool(flag)
        if not self.visible:
            self.fingers.clear()
            for b in self.buttons:
                b.pressed = False

    def _hit(self, pos):
        for b in self.buttons:
            if b.rect.collidepoint(pos):
                return b
        return None

    def handle(self, event, to_internal):
        if not self.enabled:
            return
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            try:
                w, h = pygame.display.get_surface().get_size()
                pos = to_internal((event.x * w, event.y * h)) if to_internal \
                    else (event.x * S.GAME_W, event.y * S.GAME_H)
            except Exception:
                pos = (event.x * S.GAME_W, event.y * S.GAME_H)
            if event.type == pygame.FINGERUP:
                self.fingers.pop(event.finger_id, None)
            else:
                self.fingers[event.finger_id] = pos
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION,
                            pygame.MOUSEBUTTONUP):
            if not self.enabled:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    return
                self.fingers["mouse"] = to_internal(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.fingers.pop("mouse", None)
            elif "mouse" in self.fingers:
                self.fingers["mouse"] = to_internal(event.pos)

    def update(self):
        state = {a: False for a in ACTIONS}
        if not (self.enabled and self.visible):
            return state
        for b in self.buttons:
            b.pressed = False
        for pos in self.fingers.values():
            b = self._hit(pos)
            if b:
                b.pressed = True
                state[b.action] = True
        return state

    def draw(self, surf):
        if self.enabled and self.visible:
            for b in self.buttons:
                b.draw(surf)


class InputManager:
    def __init__(self):
        self.keyboard = KeyboardInput()
        self.touch = TouchInput(S.IS_MOBILE)
        self.state = {a: False for a in ACTIONS}
        self.prev = dict(self.state)
        self.touch_active = False

    def handle_event(self, event, to_internal):
        self.touch.handle(event, to_internal)

    def update(self):
        self.prev = dict(self.state)
        keys = self.keyboard.update()
        self.touch.set_visible(self.touch_active)
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