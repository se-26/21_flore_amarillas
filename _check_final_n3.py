# -*- coding: utf-8 -*-
# Auditor final N3 basado SOLO en el archivo de datos de coords
# (_aud_l3.json) generado ejecutando level_3() real.
import json, sys
P = r'C:/21_septiembre_game/levels.py'
PY = r'C:/21_septiembre_game/src/levels.py'
sys.path.insert(0, r'C:/21_septiembre_game/src')
import importlib.util
spec = importlib.util.spec_from_file_location('audbuilder', r'C:/21_septiembre_game/src/level.py')
# NO usar el real si no queremos cargar pygame; generamos JSON con un mini-builder
# (ya hecho en _aud_source.py). Leemos ese JSON:
d = json.load(open(r'C:/21_septiembre_game/_aud_l3.json', encoding='utf-8'))
calls = d['calls']  # [['ground', x0, x1], ['flower', x, gy2], ['block', x, y, w, h], ...]

def intern(a):
    # devuelve (x,y) absoluto si y == gy-2 y x coincide con ancho de un tramo ground
    pass

# --- CRITERIO DEL USUARIO ---
# "flor que este unida con el muro": flor cuyo x cae DENTRO de la columna de
# algun block (bloque sólido) y cuya y == gy-2 (apoyada en el suelo que rodea al muro).
flores_peligro = []
for c in calls:
    if c[0] == 'flower':
        fx, fy = c[1], c[2]
        for b in calls:
            if b[0] == 'block':
                bx, by, bw, bh = b[1], b[2], b[3], b[4]
                if bx <= fx <= bx + bw - 1:
                    # flor DENTRO del ancho del muro
                    flores_peligro.append((fx, fy, (bx, by, bw, bh)))
                    break

if not flores_peligro:
    print('OK: ninguna flor del N3 cae dentro del ancho de un muro/block')
else:
    for fx, fy, blok in flores_peligro:
        print('PELIGRO: flor(%d,%d) dentro del ancho de block %s' % (fx, fy, blok))
    sys.exit(1)
