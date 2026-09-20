# -*- coding: utf-8 -*-
# Separa la flor del patrón "espejo" (nivel 3) del muro: la flor pasa a su
# propio tramo con su propio suelo, lejos del muro.

P = r'C:/21_septiembre_game/src/levels.py'
t = open(P, encoding='utf-8').read()

i3 = t.find('def level_3()')
i4 = t.find('def level_4()', i3)
assert i3 != -1 and i4 != -1
seg = t[i3:i4]

old = '''        elif p == "espejo":
            b.ground(x, x + 8, gy)
            b.block(x + 2, gy - 8, 6, 2)
            b.plat(x + 3, gy - 4, 4)
            b.flower(x + 5, gy - 10)
            b.spikes(x + 4, gy - 1, 3)
            b.enemy("perseguidor", x + 8, gy - 1)
            b.scatter_deco(x, x + 2, gy - 1, 0.6)
            x += 13'''

n = seg.count(old)
print('matches espejo N3:', n)
assert n == 1, 'matches=%d' % n

new = '''        elif p == "espejo":
            b.ground(x, x + 8, gy)
            b.block(x + 2, gy - 8, 6, 2)
            b.plat(x + 3, gy - 4, 4)
            b.spikes(x + 4, gy - 1, 3)
            b.enemy("perseguidor", x + 8, gy - 1)
            b.scatter_deco(x, x + 2, gy - 1, 0.6)
            x += 11
            b.ground(x, x + 4, gy)
            b.flower(x + 2, gy - 2)
            x += 5'''

seg2 = seg.replace(old, new, 1)
t = t[:i3] + seg2 + t[i4:]
open(P, 'w', encoding='utf-8').write(t)

import py_compile
py_compile.compile(P, doraise=True)
print('OK: flor del espejo N3 ahora con su propio suelo, separada del muro')
