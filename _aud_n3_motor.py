# -*- coding: utf-8 -*-
# Auditoria REAL nivel 3 con el motor: ejecuta level_3() tal cual, luego busca
# flores (kind flower/sunflower) cuyo rect toca el rect de al menos un block.
import sys, os, random
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, r'C:/21_septiembre_game/src')

random.seed(7)
import levels
import level as lvl

try:
    from src.levels import level_3
except Exception:
    from levels import level_3

d = level_3()
print('entidades totales N3:', len(d.entities))

def rect_of(e):
    k = e['kind']; x = e['x']; y = e['y']
    if k == 'flower':
        return (x, y, x + 1, y + 1)   # 1x1
    if k == 'block':
        return (x, y, x + e['w'], y + e['h'])
    return None

flowers = [e for e in d.entities if e['kind'] in ('flower', 'sunflower')]
blocks = [e for e in d.entities if e['kind'] == 'block']

conflictos = []
for f in flowers:
    fx0, fy0, fx1, fy1 = rect_of(f)
    for bl in blocks:
        bx0, by0, bx1, by1 = rect_of(bl)
        overlap_x = fx0 < bx1 and fx1 > bx0
        overlap_y = fy0 < by1 and fy1 > by0
        if overlap_x and overlap_y:
            conflictos.append((f['x'], f['y'], bl['x'], bl['y'], bl['w'], bl['h']))

print('N3 flores:', len(flowers), '| blocks:', len(blocks))
if conflictos:
    print('CONFLICTO FLOR-<->-BLOCK (%d):' % len(conflictos))
    for c in conflictos:
        print('   flor(%d,%d) dentro de block(%d,%d,w=%d,h=%d)' % c)
else:
    print('NINGUNA flor toca un block. NIVEL 3 LIMPIO.')
