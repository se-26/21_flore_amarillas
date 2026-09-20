# -*- coding: utf-8 -*-
# Audita nivel 3: localiza cualquier b.flower() cuya coordenada (x', y') quede
# DENTRO del rectangulo horizontal de un b.block() y a menos de 1 tile vertical
# de su borde superior (es decir, flor "pegada" colgada del muro). Devuelve
# coincidencias; NO modifica nada (auditoría pura).
import re

P = r'C:/21_septiembre_game/src/levels.py'
t = open(P, encoding='utf-8').read()
i3 = t.find('def level_3()')
i4 = t.find('def level_4()', i3)
assert i3 != -1 and i4 != -1
seg = t[i3:i4]

# --- recolectar llamadas con sus coordenadas como EXPRESIONES ---
calls = []  # (tipo, expr_x, expr_y, linea_entera)
for m in re.finditer(r'\bb\.(\w+)\((.*?)\)', seg, re.S):
    kind = m.group(1)
    args = m.group(2)
    if kind == 'flower':
        if ',' in args:
            a = args.split(',')
            calls.append(('flower', a[0].strip(), a[1].strip(), m.group(0).strip()))
    elif kind == 'block':
        a = args.split(',')
        calls.append(('block', a[0].strip(), a[1].strip(), m.group(0).strip()))

# --- resolver variables: trazamos x/gy a lo largo de level_3 (gy const) ---
# Simulamos la secuencia de llamadas con un evaluador simple de expresiones
# aritmeticas (x, x+i*4, gy, ints, gy-2 ...)
def ev(expr, xval, gyval):
    import random
    e = expr.replace('gy', str(gyval))
    e = e.replace('x', str(xval))
    # eliminar sufijo rnd/reserva no aplicable
    try:
        return int(eval(e))
    except Exception:
        return None

gyval = 20
xval = 0
flor_blocks = []
for typ, ex, ey, raw in calls:
    if ex in ('x',) or ex.startswith('150') or ex.isdigit() or 'gy' in ey:
        px = ev(ex, xval, gyval)
        py = ev(ey, xval, gyval)
        flor_blocks.append(('F', px, py, raw))
    elif typ == 'block':
        px = ev(ex, xval, gyval)
        py = ev(ey, xval, gyval)
        flor_blocks.append(('B', px, py, raw))

# --- deteccion geometrica ---
# bloques con X range: block(x0, y0, w, h) -> horizontal [x0, x0+w)
holes = []
for kind, x0, y0, raw in flor_blocks:
    if kind == 'B':
        m2 = re.match(r'b\.block\((.*?),\s*(.*?),\s*(\d+),\s*(\d+)\)', raw)
        if m2:
            w = int(m2.group(3)); h = int(m2.group(4))
            holes.append((x0, y0, w, h))
res = []
for kind, fx, fy, raw in flor_blocks:
    if kind != 'F':
        continue
    for bx, by, w, h in holes:
        if bx <= fx < bx + w and fy >= by and fy <= by + h:
            res.append((fx, fy, bx, by, w, h, raw))

print('NIVEL3: flores que CAEN DENTRO de un bloque (flor pegada al muro):')
if not res:
    print('  NINGUNA (ya estan todas separadas)')
for fx, fy, bx, by, w, h, raw in res:
    print('  flor en (%d,%d) DENTRO de block(%d,%d,%d,%d) -> %s' % (fx, fy, bx, by, w, h, raw))
