"""Entrada unificada: teclado.

El gameplay solo consulta acciones ("left", "jump", ...) y nunca al teclado
directamente.
"""
import pygame

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


class InputManager:
    def __init__(self):
        self.keyboard = KeyboardInput()
        self.state = {a: False for a in ACTIONS}
        self.prev = dict(self.state)

    def handle_event(self, event, to_internal):
        pass

    def update(self):
        self.prev = dict(self.state)
        keys = self.keyboard.update()
        self.state = {a: keys[a] for a in ACTIONS}
        return self.state

    def down(self, action):
        return self.state.get(action, False)

    def pressed(self, action):
        return self.state.get(action, False) and not self.prev.get(action, False)

    def released(self, action):
        return not self.state.get(action, False) and self.prev.get(action, False)

    def draw(self, surf):
        pass