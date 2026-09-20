# -*- coding: utf-8 -*-
# Nivel 3, patron "espejo" REAL (dump por Builder real):
#   else:
#       b.ground(x, x + 8, gy)
#       b.block(x + 2, gy - 8, 6, 2)   <- muro (tope gy-6)
#       b.plat(x + 3, gy - 4, 4)
#       b.flower(x + 5, gy - 10)       <- FLOR PEGADA ENCIMA DEL MURO
# La flor se separa: se elimina del muro y se coloca en su propio tramo de suelo.
P = r'C:/21_septiembre_game/src/levels.py'
t = open(P, encoding='utf-8').read()

old = '''            b.block(x + 2, gy - 8, 6, 2)
            b.plat(x + 3, gy - 4, 4)
            b.flower(x + 5, gy - 10)'''
n = t.count(old)
assert n == 1, 'matches espejo N3=%d' % n

new = '''            b.block(x + 2, gy - 8, 6, 2)
            b.plat(x + 3, gy - 4, 4)'''
t = t.replace(old, new, 1)

# Agregar el tramo propio de la flor al final de la rama espejo (despues del x += 13)
i3 = t.find('def level_3()'); i4 = t.find('def level_4()', i3)
seg = t[i3:i4]
oldtail = '''            b.enemy("perseguidor", x + 8, gy - 1)
            b.scatter_deco(x, x + 2, gy - 1, 0.6)
            x += 13'''
n2 = seg.count(oldtail)
assert n2 == 1, 'tail espejo N3=%d' % n2
newtail = '''            b.enemy("perseguidor", x + 8, gy - 1)
            b.scatter_deco(x, x + 2, gy - 1, 0.6)
            x += 13
            b.ground(x, x + 5, gy)
            b.flower(x + 2, gy - 2)
            x += 5'''
seg = seg.replace(oldtail, newtail, 1)
t = t[:i3] + seg + t[i4:]

open(P, 'w', encoding='utf-8').write(t)
import py_compile
py_compile.compile(P, doraise=True)
print('OK: flor N3/espejo ya NO esta sobre el muro; tiene su propio tramo de suelo.')
