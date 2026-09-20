# -*- coding: utf-8 -*-
# Separacion definitiva flor<muro nivel 3: reemplaza la flor que esta sentada
# sobre el tope de la columnata de raices/espejo por su propio tramo separado.
# Unica fuente: levels.py real + Builder REAL del motor.
import sys, re, random
sys.path.insert(0, r'C:/21_septiembre_game/src')
sys.path.insert(0, r'C:/21_septiembre_game')

# --- Motor real: Builder/LevelBuilder reales para ejecutar level_3 en vivo ---
try:
    from src.level import Builder      # Builder real
    from src.levels import level_3     # para poder instrumentar
    HAS_REAL = True
except Exception as e:
    print('motor real NO importable:', e); HAS_REAL = False

# --- Entorno Builder de captura (API tipo source) ---
class Decoy:
    def __init__(self):
        self.calls = []
        self.rnd = type('R', (), {'choice': lambda self, seq: seq[-1]})()
    def __getattr__(self, n):
        def f(*a, **k):
            self.calls.append((n, a, k))
        return f

# --- Cargamos level_3 como SUBCONJUNTO y ejecutamos con el decoy para ver
#     la secuencia REAL (sin importar pygame) ---
import importlib.util, types
src = open(r'C:/21_septiembre_game/src/levels.py', encoding='utf-8').read()
i3 = src.find('def level_3()'); i4 = src.find('def level_4()', i3)
body3 = src[i3:i4]

# instrumentar: reemplazar 'b = Builder(...)' dentro de level_3 para usar decoy
body3_inst = body3.replace('b = Builder(', 'b = _DECOY ').replace('b=Builder(', 'b=_DECOY ')
# gy y rnd/random: reemplazar referencias
body3_inst = body3_inst.replace('b.rnd', '_DECOY.rnd')
# (builder usa b.* via decoy; keep d, LevelData real si importable)
ns = {}
exec(compile(
    'import random\n' + body3_inst,
    '<l3>', 'exec'), ns)
