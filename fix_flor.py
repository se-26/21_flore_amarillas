import re

p = r'C:/21_septiembre_game/src/levels.py'
t = open(p, encoding='utf-8').read()

old = '''        else:
            b.ground(x, x + 14, gy)
            for i in range(3):
                b.block(x + 2 + i * 4, gy - 3 - i, 2, 3 + i)
            b.flower(x + 10, gy - 7)
            b.scatter_deco(x, x + 14, gy - 1, 0.7)
            b.enemy("saltarin", x + 12, gy - 1)
            x += 16
            b.ground(x, x + 4, gy)
            b.flower(x + 2, gy - 2)
            x += 5'''

n = t.count(old)
print('n =', n)
assert n == 1, 'matches ' + str(n)

new = '''        else:
            b.ground(x, x + 14, gy)
            for i in range(3):
                b.block(x + 2 + i * 4, gy - 3 - i, 2, 3 + i)
            b.scatter_deco(x, x + 14, gy - 1, 0.7)
            b.enemy("saltarin", x + 12, gy - 1)
            x += 16
            b.ground(x, x + 4, gy)
            b.flower(x + 2, gy - 2)
            x += 9
            b.ground(x, x + 4, gy)
            b.flower(x + 2, gy - 2)
            x += 5'''

t = t.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(t)
import py_compile
py_compile.compile(p, doraise=True)
print('OK nivel3: flor quitada de encima de la pared escalonada; cada flor con su propia base de suelo')
