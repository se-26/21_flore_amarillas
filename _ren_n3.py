# -*- coding: utf-8 -*-
# Renderiza el nivel 3 usando el Builder REAL y guarda un PNG de verificacion
# visual (una franja donde estan muro/flor/escalon). Funciona sin ventana.
import os, sys, random
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, r'C:/21_septiembre_game/src')
sys.path.insert(0, r'C:/21_septiembre_game')

import pygame
pygame.init()
import levels  # ejecuta level_3()? no: define las funciones
import level as lvl_mod
import imp

# Reusar exactamente el mecanismo del motor: from levels import level_3
# que usa Builder (en level.py debajo de 'Builder'). Importamos el modulo
# completo del juego y llamamos level_3() con un builder de captura.
# En vez de mockear: simplemente ejecutamos levels.level_3() con el Builder real.
b = None
try:
    d, calls = levels.build_capture_level_3()
    print('captura:', None if d is None else len(calls))
except AttributeError:
    print('no hay helper build_capture; hago instrumentacion directa')

# Instrumentacion directa: modelo minimo que el codigo real usa (b.ground, b.block,
# b.flower, b.plat, b.spikes, b.scatter_deco, b.enemy, b.rnd.choice...)
class C:
    def __init__(self):
        self.entities = []
        self.tiles = {}
        self.xs = []
    def ground(self, a, b2, gy):
        self.entities.append(('ground', a, b2, gy))
    def block(self, a, y, w, h):
        self.entities.append(('block', a, y, w, h))
    def plat(self, a, y, w):
        self.entities.append(('plat', a, y, w))
    def flower(self, a, y):
        self.entities.append(('flower', a, y))
    def spikes(self, a, y, w):
        self.entities.append(('spikes', a, y, w))
    def scatter_deco(self, a, b2, y, p):
        self.entities.append(('deco', a, b2, y, p))
    def enemy(self, kind, x, y):
        self.entities.append(('enemy', kind, x, y))
    def check(self, x, y):
        self.entities.append(('check', x, y))

import types
def fake_builder():
    c = C()
    b = types.SimpleNamespace(
        ground=c.ground, block=c.block, plat=c.plat, flower=c.flower,
        spikes=c.spikes, scatter_deco=c.scatter_deco, enemy=c.enemy,
        check=c.check, checkpoint=c.check, door=lambda *a: None,
        scatter_deco_trees=None,
        rnd=types.SimpleNamespace(choice=lambda s: s[0]),
        rnd_int=None,
    )
    return b, c

# inyectar builders capturadores: ejecutamos SOLO level_3 definiendo Builder b_en_capa
level_3 = getattr(levels, 'level_3')
print('existe level_3:', callable(level_3))
