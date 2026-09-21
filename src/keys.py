"""Codigos de tecla compatibles con escritorio y pygbag/web.

pygame-ce en la build web no exporta las constantes de una letra
(pygame.K_a ...). Se resuelven con los codigos SDL equivalentes, que son
identicos en ambas plataformas.
"""
import pygame

_FALLBACK = {
    "a": 97, "d": 100, "e": 101, "j": 106, "s": 115,
    "w": 119, "x": 120, "z": 122,
    "SPACE": 32, "RETURN": 13, "ESCAPE": 27,
    "LSHIFT": 1073742049, "RSHIFT": 1073742053,
    "F5": 1073741886, "F11": 1073741892,
    "LEFT": 1073741904, "RIGHT": 1073741903,
    "UP": 1073741906, "DOWN": 1073741905,
}


def _resolve(name):
    if hasattr(pygame, "K_" + name):
        return getattr(pygame, "K_" + name)
    return _FALLBACK[name]


K_LEFT = _resolve("LEFT")
K_RIGHT = _resolve("RIGHT")
K_UP = _resolve("UP")
K_DOWN = _resolve("DOWN")
K_SPACE = _resolve("SPACE")
K_RETURN = _resolve("RETURN")
K_ESCAPE = _resolve("ESCAPE")
K_LSHIFT = _resolve("LSHIFT")
K_RSHIFT = _resolve("RSHIFT")
K_F5 = _resolve("F5")
K_F11 = _resolve("F11")
K_a = _resolve("a")
K_d = _resolve("d")
K_e = _resolve("e")
K_j = _resolve("j")
K_s = _resolve("s")
K_w = _resolve("w")
K_x = _resolve("x")
K_z = _resolve("z")