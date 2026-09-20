# -*- coding: utf-8 -*-
# Auditoría fina nivel 3: flor cuya x coincide con la x de un tope de escalón
# (block escalonado de raíces) y cuya y está 1..2 tiles POR ENCIMA de ese tope
# => se ve "montada" sobre el muro escalonado.
import re
import random as __rnd

P = r'C:/21_septiembre_game/src/levels.py'
t = open(P, encoding='utf-8').read()
i3 = t.find('def level_3()'); i4 = t.find('def level_4()', i3)
seg = t[i3:i4]

# Limpia comentarios y recoge llamadas en orden real con regex tolerante
calls = []
for m in re.finditer(r'b\.(\w+)\s*\((.*?)\)\n', seg, re.S):
    kind = m.group(1)
    args = m.group(2)
    if kind == 'ground':
        a = [x.strip() for x in args.split(',')]
        calls.append(('GROUND', a[0], a[1]))
    elif kind == 'block':
        a = [x.strip() for x in args.split(',')]
        calls.append(('BLOCK', a))
    elif kind in ('flower', 'plat', 'spikes', 'enemy', 'deco', 'plat_cadena'):
        calls.append((kind.upper(), args))

# Evaluamos símbolos: x (xactual del loop), i, gy. Reconstruimos el recorrido
# del bucle: creamos un mini-evaluador caminando x del mismo modo.
def ev_expr(e, x, i, gy):
    e = e.strip()
    e = e.replace('gy', '(' + str(gy) + ')')
    e = e.replace('x + i * ', '(x)+i*')
    e = e.replace('x + ', '(x)+')
    e = e.replace('x - ', '(x)-')
    e = re.sub(r'\bx\b', '(%d)' % x, e)
    e = e.replace('i', '(%d)' % i)
    if e.strip() == 'gy':
        return gy
    try:
        return int(eval(e))
    except Exception:
        return None

random.seed = 0
import random as rnd
gy = 20
x = 0
topes = []   # (x_bloque, tope_y) de bloques escalonados tipo raíces
montadas = []
i = 0
for kind, *rest in [c for c in calls]:
    if kind == 'BLOCK':
        a = rest[0]
        bx = ev_expr(a[0], x, 0, gy)
        by = ev_expr(a[1], x, 0, gy)
        bolder = ev_expr(a[2], x, 0, gy)
        topes.append((bx, by + bolder))   # tope superior = y+h
    elif kind == 'FLOWER':
        a = [z.strip() for z in rest[0].split(',')]
        fx = ev_expr(a[0], x, 0, gy)
        fy = ev_expr(a[1], x, 0, gy)
        for (bx, tope) in topes:
            if fx == bx and fy < tope and fy >= tope - 2:
                montadas.append((fx, fy, 'tope=%d (2 arriba)' % tope))

print('FLORES nivel3 montadas sobre tope de escalón (fx == bx, 1..2 tiles arriba):')
if montadas:
    for fx, fy, nota in montadas:
        print('  flor(%d, %d) -> %s' % (fx, fy, nota))
else:
    print('  NINGUNA')
