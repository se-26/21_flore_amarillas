# -*- coding: utf-8 -*-
# UNICO proceso: 1) parsea level_3(). 2) evalua geometria real con mini-builder.
# 3) si una flor queda dentro del ancho de un block (pegada al muro), la separa
# dandole su propio tramo de suelo. 4) escribe+compila y reporta.
import re, sys, random

P = r'C:/21_septiembre_game/src/levels.py'
t = open(P, encoding='utf-8').read()
i3 = t.find('def level_3()'); i4 = t.find('def level_4()', i3)
assert i3 != -1 and i4 != -1
seg = t[i3:i4]

# ---- mini-builder: evalua las llamadas usando x,gy SIMULADAS ----
class Rnd:
    def choice(self, seq): return 'L_CONTINUO'  # fuerzo rama continua: no queremos
random  # noop
# levantar name 'b' como objeto cuya __call__ graba
calls = []

class Grab:
    def __init__(self): pass
    def __getattr__(self, n):
        def f(*a, **k):
            calls.append((n, a, k))
        return f
b = Grab()

# ejecutar el BLOQUE con simulador de nivel: hay que evaluar gy, x, while, random
# en vez de ejecutar, extramemos textualmente con un PARSER SIMPLE: partimos el
# código en llamadas b.NOMBRE(ARG...) con matching de paréntesis.

def find_paren(s, k):
    # s[k] == '('
    depth = 0
    i = k
    while i < len(s):
        c = s[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError('unbalanced')

# ejecutamos de verdad usando exec con un faker de Builder que guarde TODAS las
# llamadas con sus arg-tuples y dejamos que level_3() se ejecute.
# Para reproducir variable por variable (x, i, gy, d) sin pygame:
import types
faker_space = {'Builder': lambda *a, **k: b,
               'LevelData': lambda *a, **k: types.SimpleNamespace(entities=[])}
# El módulo usa nombres globales 'Builder','LevelData' dentro del def.
# Hacemos exec del body con esos nombres inyectados.
body = seg.split('\n')
# cambiar corchetes de módulo: no, basta inyectar globals
g = {'Builder': type('B', (), {'__init__': lambda s, *a, **k: None}),
     'LevelData': type('L', (), {'__init__': lambda s, *a, **k: None}),
     'b': b, 'd': None, 'rnd': random, 'random': random,
     '__name__': '__main__'}
# el body usa 'b.rnd.choice' -> nuestro b no tiene rnd: damos attribute rnd
class rndw:
    def choice(self, s):
        return s[0]
b.rnd = rndw()
# scatter_deco etc: en n3 se llaman b.scatter_deco, b.spikes... todos pasan por
# __getattr__ -> grabados. PERO 'scatter_deco' real existe con default 0.6->graba=ok
# Simular x: el codigo setea x via 'x += N'. Ejecutamos.
code = seg[seg.find('\n')+1:]  # quitar 'def level_3():'
# inyectar asignación inicial de x y gy que el cuerpo asume? El cuerpo define:
#   d = LevelData(...); b = Builder(d, 170, 26, 303); gy=20; x=0 ... (arriba en level)
# Aquí el seg empieza en '    d = LevelData("inverso"...'. Ejecutamos tal cual.
g['Builder'] = fake  # usar nuestro grab-builder que guarda llamadas
exec(code, g)
PYTHON = True
