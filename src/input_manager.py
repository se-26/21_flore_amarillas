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
from . import keys as K

ACTIONS = ("left", "right", "up", "down", "jump", "attack", "interact", "pause")

KEYMAP = {
    "left": (K.K_a, K.K_LEFT),
    "right": (K.K_d, K.K_RIGHT),
    "up": (K.K_w, K.K_UP),
    "down": (K.K_s, K.K_DOWN),
    "jump": (K.K_SPACE, K.K_w, K.K_UP, K.K_z),
    "attack": (K.K_x, K.K_j),
    "interact": (K.K_e, K.K_RETURN),
    "pause": (K.K_ESCAPE,),
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
    """Boton virtual semi-transparente estilo pixel art magico.

    Marco pixel art con esquinas redondeadas, sombra suave y acento amarillo;
    al presionarlo se ilumina, cambia el icono de color y "rebota" hacia
    abajo. Los iconos son simples (flechas, flor) y el texto es minimo.
    """

    def __init__(self, action, rect, label, caption=""):
        self.action = action
        self.rect = pygame.Rect(rect)
        self.label = label
        self.caption = caption
        self.pressed = False
        self.enabled = True
        self._pad_idle = None
        self._pad_pressed = None

    def _icon(self, surf, cx, cy, main, outline):
        """Dibuja el icono del boton centrado en (cx, cy)."""
        if self.label == "<":
            pygame.draw.polygon(surf, main, [(cx - 3, cy - 7), (cx - 3, cy + 7), (cx - 10, cy)])
            pygame.draw.polygon(surf, outline, [(cx - 3, cy - 7), (cx - 3, cy + 7), (cx - 10, cy)], 1)
        elif self.label == ">":
            pygame.draw.polygon(surf, main, [(cx + 3, cy - 7), (cx + 3, cy + 7), (cx + 10, cy)])
            pygame.draw.polygon(surf, outline, [(cx + 3, cy - 7), (cx + 3, cy + 7), (cx + 10, cy)], 1)
        elif self.label == "^":
            pygame.draw.polygon(surf, main, [(cx, cy - 9), (cx - 9, cy + 1), (cx + 9, cy + 1)])
            pygame.draw.polygon(surf, outline,
                                [(cx, cy - 9), (cx - 9, cy + 1), (cx + 9, cy + 1)], 1)
            pygame.draw.rect(surf, main, (cx - 2, cy + 1, 4, 5))
            pygame.draw.rect(surf, outline, (cx - 2, cy + 1, 4, 5), 1)
        elif self.label == "v":
            pygame.draw.polygon(surf, main, [(cx - 9, cy - 1), (cx + 9, cy - 1), (cx, cy + 8)])
            pygame.draw.polygon(surf, outline,
                                [(cx - 9, cy - 1), (cx + 9, cy - 1), (cx, cy + 8)], 1)
            pygame.draw.rect(surf, main, (cx - 2, cy - 7, 4, 6))
            pygame.draw.rect(surf, outline, (cx - 2, cy - 7, 4, 6), 1)
        elif self.label == "FLOR":
            # florecilla amarilla pixel art: 4 petalos + corazon + tallo
            pygame.draw.rect(surf, S.YELLOW, (cx - 6, cy - 7, 5, 5))
            pygame.draw.rect(surf, S.YELLOW, (cx + 1, cy - 7, 5, 5))
            pygame.draw.rect(surf, S.YELLOW, (cx - 6, cy + 2, 5, 5))
            pygame.draw.rect(surf, S.YELLOW, (cx + 1, cy + 2, 5, 5))
            pygame.draw.rect(surf, S.ORANGE, (cx - 2, cy - 2, 4, 4))
            pygame.draw.rect(surf, S.GREEN, (cx - 1, cy + 7, 3, 6))
        elif self.label == "E":
            ui.text(surf, "E", (cx, cy - 4), 11, main, shadow=None, center=True)

    def _build_pads(self):
        """Pre-renderiza el marco del boton (reposo y presionado) una vez."""
        r = self.rect

        def make(pressed):
            pad = pygame.Surface(r.size, pygame.SRCALPHA)
            box = pad.get_rect()
            if pressed:
                fill = (88, 62, 78, 224)
                edge = (255, 236, 160, 255)
                inner = (255, 250, 220, 255)
            else:
                fill = (52, 42, 62, 128)
                edge = (255, 238, 150, 190)
                inner = (255, 214, 74, 120)
            pygame.draw.rect(pad, (18, 14, 24, 80), box.move(2, 3), border_radius=12)
            pygame.draw.rect(pad, edge, box, border_radius=12)
            pygame.draw.rect(pad, fill, box.inflate(-3, -3), border_radius=10)
            pygame.draw.rect(pad, inner, box.inflate(-3, -3), 2, border_radius=10)
            pygame.draw.line(pad, (255, 250, 230, 120 if not pressed else 220),
                             (4, 4), (r.w - 5, 4))
            return pad

        if self._pad_idle is None:
            self._pad_idle = make(False)
        if self._pad_pressed is None:
            self._pad_pressed = make(True)

    def draw(self, surf):
        if not self.enabled:
            return
        r = self.rect
        pressed = self.pressed
        if self._pad_idle is None or self._pad_pressed is None:
            self._build_pads()
        pad = self._pad_pressed if pressed else self._pad_idle
        surf.blit(pad, r.topleft)

        cx, cy = r.center
        if pressed:
            cy += 2
        if pressed:
            main = (46, 38, 54)
            outline = (255, 244, 214)
        else:
            main = (255, 244, 214)
            outline = (46, 38, 54)
        self._icon(surf, cx, cy, main, outline)
        if self.caption:
            ui.text(surf, self.caption, (int(cx), int(r.bottom - 7)), 9,
                    (255, 214, 74) if pressed else (226, 206, 168),
                    center=True, alpha=240)


class TouchInput:
    """Botones tactiles de las esquinas inferiores (pantalla horizontal).

    Izquierda: flechas de movimiento. Derecha: SALTO (grande), AGACHARSE y
    FLOR/ataque. El boton de flor solo aparece cuando el poder de lanzar
    flores esta desbloqueado; el de interactuar solo cuando hay algo que
    desencadenar. Se dibujan y quedan activos con set_visible(True), que el
    juego activa cada frame mientras el jugador recorre el mundo sin dialogos.
    """

    def __init__(self, enabled):
        self.enabled = enabled or os.environ.get("TOUCH_TEST") == "1"
        w, h = S.GAME_W, S.GAME_H
        m = 12
        size = int(h * 0.26)          # boton estandar
        gap = max(8, int(size * 0.16))
        jsize = int(h * 0.30)         # boton de salto, el mas grande
        csize = int(h * 0.23)         # agacharse / interactuar, compactos
        asize = int(h * 0.26)         # ataque / flor

        self.buttons = [
            TouchButton("left", (m, h - m - size, size, size), "<"),
            TouchButton("right", (m + size + gap, h - m - size, size, size), ">"),
            TouchButton("jump", (w - m - jsize, h - m - jsize, jsize, jsize),
                        "^", "SALTO"),
            TouchButton("down", (w - m - jsize + int(jsize * 0.18),
                                 h - m - jsize - csize - int(gap * 0.7),
                                 csize, csize), "v", "AGACH."),
        ]
        self.attack = TouchButton(
            "attack", (w - m - jsize - asize - gap,
                       h - m - jsize + int((jsize - asize) // 2),
                       asize, asize), "FLOR", "FLOR")
        self.interact = TouchButton(
            "interact", (w - m - jsize - asize - int(gap * 1.5),
                         h - m - jsize - csize - int(gap * 0.7) - 2,
                         csize, csize), "E")
        self.attack.enabled = False
        self.buttons += (self.attack, self.interact)
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

    def set_power(self, on):
        """Muestra/oculta el boton FLOR cuando se desbloquea el poder."""
        if not self.enabled:
            return
        self.attack.enabled = bool(on)

    def set_interact(self, on):
        """Muestra el boton de interactuar solo cuando hay algo cerca."""
        if not self.enabled:
            return
        self.interact.enabled = bool(on)

    def _hit(self, pos):
        for b in self.buttons:
            if b.enabled and b.rect.collidepoint(pos):
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

    def set_power(self, on):
        self.touch.set_power(on)

    def set_interact(self, on):
        self.touch.set_interact(on)

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