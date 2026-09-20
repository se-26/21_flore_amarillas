import re, sys, random
sys.path.insert(0, r'C:/21_septiembre_game/src')

# Importamos SOLO los nombres que level_3 necesita (Builder + LevelData) leyendo el archivo fuente
src = open(r'C:/21_septiembre_game/src/levels.py', encoding='utf-8').read()

# Builder real: instrumentado para capturar llamadas
class B:
    def __init__(self):
        self.calls = []
        self.counter = 0
    def __getattr__(self, name):
        def f(*a, **k):
            self.calls.append((name, a, k))
        return f

# Necesitamos el Builder real que usa `b.rnd` y métodos como enemy/spikes etc — reemplazamos
# capturando TODA llamada. Para ejecutar level_3 debemos tener `b` y `d` reales.
# En vez de importar (arriesgado con pygame), ejecutamos el cuerpo textualmente con un builder tonto.
# Extraemos el CÓDIGO literal de level_3() del archivo:
i = src.find('def level_3()'); j = src.find('def level_4()', i)
code = src[i:j]
# Reemplazamos la cabecera para no necesitar imports
mhead = re.match(r'def level_3\(\):\n(.*?\n)\s*(b = Builder\(d.\)|b = Builder\()', code, re.S)
body = code
# Buscamos la línea de creación del Builder y la quitamos del body a ejecutar
k1 = body.find('b = Builder')
line_b = body[body.rfind('\n', 0, k1)+1:body.find('\n', k1)+1]
body = body.replace(line_b, '', 1)

env = {'Builder': type('FB', (), {'__init__': lambda s,*a,**k: None}),
       'LevelData': type('FL', (), {'__init__': lambda s,*a,**k: None}),
       'random': random}
env['b'] = None

# Extraer bloque hasta 'def level_4' ya no está: ejecutamos `body` pero la flor necesita el Builder real.
# Enfoque definitivo: PARSER de intención — leer todas las llamadas b.X(...) con sus ARGUMENTOS TEXTUALES
calls = re.findall(r'b\.(\w+)\(([^)]*)\)', body)
flowers = []
for name, args in calls:
    if name == 'flower':
        flowers.append(args)
blocks = []
for name, args in calls:
    if name == 'block':
        blocks.append(args)
spikes = [a for n, a in calls if n == 'spikes']

# Evaluar geometría: gy=20, cada flower(X, gy-...) — calculamos y si X cae en [bx, bx+bw] y florY en [by, by+bh]
def evalv(expr, basex=0, gy=20):
    e = expr
    e = e.replace('gy', str(gy)).replace('x', str(basex))
    try:
        return int(eval(e, {'__builtins__': {}}, {'i': 0, 'r': 17}))
    except Exception:
        return None

print('=== FLORES (textuales) ===')
for f in flowers:
    print('   b.flower(%s)' % f)
print('=== BLOCKS (textuales) ===')
for b in blocks:
    print('   b.block(%s)' % b)
