import sys
p = r'C:/21_septiembre_game/src/levels.py'
t = open(p, encoding='utf-8').read()
i3 = t.find('def level_3()')
i4 = t.find('def level_4()', i3)
seg = t[i3:i4]
print('=== NIVEL 3 COMPLETO (por número de línea real) ===')
lines = seg.split('\n')
for k, l in enumerate(lines):
    print('%3d %s' % (k + 1, l))
PY = True
