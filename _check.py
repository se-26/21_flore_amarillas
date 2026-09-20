import re, sys, random
sys.path.insert(0, r'C:/21_septiembre_game/src')
p = r'C:/21_septiembre_game/src/levels.py'
t = open(p, encoding='utf-8').read()

import py_compile
py_compile.compile(p, doraise=True)

# ------------------------------------------------------------
# Builder real instrumentado: recoge cada llamada (nombre, args)
# ------------------------------------------------------------
class Builder:
    def __init__(self, d, w, h, gy_):
        self.calls = []
        self.rnd = random.Random(42)
        self.d = d
    def __getattr__(self, name):
        def f(*a, **k):
            self.calls.append((name, a, k))
        return f

class LevelData:
    def __init__(self):
        self.entities = []
        self.objects = []

class B:
    def __init__(self, d, w, h, gy_):
        pass
    def rnd(self):
        return random.Random(42)

mod = sys.modules.get('levels')
if mod is None:
    import types
    mod = types.ModuleType('levels')
sys.modules['levels'] = mod

ns = {}
# Cargamos solo level_3 evaluando el texto de forma controlada
src = open(p, encoding='utf-8').read()
i3 = src.find('def level_3()')
i4 = src.find('def level_4()', i3)
seg0 = src[i3:i4]

# Sustituir el encabezado para inyectar nuestro Builder/LevelData
head = '''LEVEL_PATTERNS = ["espejo", "raices", "espejo", "raices"]
'''
seg = head + seg0
# La funcion usa Builder (alias b) y LevelData (d) y random
random.seed(42)
import random as _rnd
# Creamos el LevelData real necesario por d.entities
try:
    from level import LevelData as RealLevelData, Builder as RealBuilder
    have_real = True
except Exception as e:
    have_real = False

if have_real:
    pass

exec compile(seg, 'l3', 'exec')
PY