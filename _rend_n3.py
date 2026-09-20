# coding: utf-8
# Render exclusivo del nivel 3 con SDL dummy y guarda un PNG de ancho acotado
# para inspeccion visual. Reutiliza los sistemas reales del juego.
import os, sys
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, r'C:/21_septiembre_game')
sys.path.insert(0, r'C:/21_septiembre_game/src')

import pygame
import levels as L

# --- Construir level_3 con un Builder que sepa RESOLVER coordenadas en vivo ---
# Reutilizamos el Builder REAL del juego (src/builder? en levels.py hay Builder)
# Lo mas simple: usar el Builder real que exporta canon (b.ground...). Lo busco:
import levels as levels_mod
Builder = getattr(levels_mod, 'Builder', None)
print('Builder real presente:', Builder is not None)

# Para captura visual haremos un builder de REGISTRO con resolucion de
# aritmetica real, y al final DIBUJAMOS directo el mapa de tiles en pygame.
class Reg:
    def __init__(self):
        self.tiles = {}
        self.ents = []
    def _S(self, v, x, gy):
        # resuelve 'v' usando x y gy del contexto
        return eval(v, {'x': x, 'gy': gy}, {})
    def ground(self, a, b_, gy_):
        x, gy = a, gy_
        x0 = self._S(str(a), x, gy); x1 = self._S(str(b_), x, gy)
        for i in range(int(x0), int(x1)):
            self.tiles[(i, int(gy))] = 'ground'
        self._last = (int(x0), int(x1), int(gy))
    def block(self, a, y, w, h):
        x, gy = a, None
        x0 = self._S(str(a), x, None); y0 = self._S(str(y), x, None)
        w = self._S(str(w), x, None); h = self._S(str(h), x, None)
        for i in range(int(w)):
            for j in range(int(h)):
                self.tiles[(int(x0)+i, int(y0)+j)] = 'block'
    def plat(self, a, y, w):
        x0 = self._S(str(a), x, self._gy)
        return None
    def flower(self, a, y):
        x0 = self._S(str(a), self._x, self._gy)
        y0 = self._S(str(y), self._x, self._gy)
        self.tiles[(int(x0), int(y0))] = 'flower'
    def enemy(self, *a):
        pass
    def scatter_deco(self, *a):
        pass
    def scatter_deco_grace(self, *a):
        pass
    def deco_pend(self, *a):
        pass
    def plat_hidden(self, *a):
        pass
    def plat_vanish(self, *a):
        pass
    def spikes(self, *a):
        pass
    def plat_flag(self, *a):
        pass
    def enemy_volador(self, *a):
        pass
    def scatter_deco_raised(self, *a):
        pass
    def platform_pend(self, *a):
        pass
    def plat_elevada(self, *a):
        pass
    def door(self, *a):
        pass
    def check(self, *a):
        pass
    def checkpoint(self, *a):
        pass
    def deco_ok(self, *a):
        pass
    def deco_vine(self, *a):
        pass
    def enemy_slow(self, *a):
        pass
    def plat_ghost(self, *a):
        pass
    def flower_alt(self, *a):
        pass
    def finish(self, *a):
        return ('finish', a)

# FALLA: los parámetros de los builders reales son funcionales (x, gy), la
# ejecución necesita trazar x. Este camino es complicado. Cambiamos de
# estrategia simple y DIRECTA: inspección textual con python puro del bloque
# espejo real en el archivo (sin ejecutar), imprimiendo esa ventana exacta.
import re
P = r'C:/21_septiembre_game/src/levels.py'
t = open(P, encoding='utf-8').read()
i3 = t.find('def level_3()'); i4 = t.find('def level_4()', i3)
seg = t[i3:i4]
# ventana: todo hasta el primer def de fuera
print('=== VENTANA REAL level_3 (fragmentos clave) ===')
for m in re.finditer(r'elif p == "espejo":.*?x \+= \d+', seg, re.S):
    print(m.group(0)[:400])
"