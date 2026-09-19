# 🌻 21 de Septiembre: Flores para Ti

Juego **2D de plataformas** en **Python + Pygame**, con estética pixel art propia,
seis niveles, enemigos, combate, poder mágico del girasol y una escena final
para entregarle un ramo a esa persona especial.

Todo el arte se genera por código: personajes, enemigos, tiles, props, fondos
por capas e interfaz. No hace falta descargar ninguna imagen ni sonido.

---

## 🎮 Controles

| Tecla | Acción |
|---|---|
| `A` / `←` y `D` / `→` | Moverse |
| `ESPACIO` / `W` / `↑` | Saltar (salto variable según lo que mantengas; pulsa 2 veces para saltar más alto) |
| `S` / `↓` | Agacharse |
| `X` | Atacar / lanzar flor (tras desbloquear el poder) |
| `E` | Hablar con NPCs e interactuar con girasoles |
| `SHIFT` | Correr |
| `ESC` | Pausa |
| `F5` | Guardado rápido |
| `F11` | Pantalla completa |

En móvil aparecen automáticamente botones táctiles pixel art (izquierda, derecha,
agacharse, salto, flor e interactuar) y un aviso para girar el dispositivo.

---

## 🗺️ Los seis niveles

1. **El Campo Dorado** — tutorial: moverse, saltar, recoger flores, primer enemigo, checkpoint y el primer **girasol especial**.
2. **El Bosque Susurrante** — plataformas, huecos, monstruos saltadores y flores escondidas en las alturas.
3. **El Bosque al Revés** — plataformas colgadas del techo, criaturas perseguidoras, pinchos y secretos.
4. **Las Islas del Cielo** — islas flotantes, plataformas móviles y enemigos voladores.
5. **El Mundo de los Sueños** — plataformas que aparecen y desaparecen, enemigos con proyectiles y trampas.
6. **El Jardín Final** — guardián del jardín, jardín enorme y entrega del ramo.

**Progresión:** cada nivel pide más flores y añade una mecánica nueva.

---

## 🌻 Poder del girasol

Al principio **no puedes lanzar flores**. Cuando encuentres un girasol especial
y pulses `E`, se desbloquea el poder (animación + sonido). A partir de ahí `X`
lanza flores amarillas con munición limitada (`5`), que se recarga en los
siguientes girasoles. Sin munición el ataque vuelve a ser cuerpo a cuerpo.
También puedes derrotar enemigos saltando encima.

---

## 🖥️ Instalación en Windows (paso a paso)

### 1. Python
Descarga **Python 3.10+** en <https://www.python.org/downloads/> y marca
**"Add Python to PATH"** al instalar.

### 2. Git Bash
```bash
cd ~/Descargas
cd 21_septiembre_game
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python main.py
```
Para salir del entorno: `deactivate`

### 3. Visual Studio Code
1. **File > Open Folder…** → `21_septiembre_game`
2. Instala la extensión **Python** de Microsoft.
3. `Ctrl+Shift+P` → **Python: Select Interpreter** → `.\venv\Scripts\python.exe`
4. Terminal integrada (`` Ctrl+` ``):
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
5. O abre `main.py` y pulsa ▶ (*Run Python File*).

---

## 📁 Estructura

```
21_septiembre_game/
├── main.py                 # solo inicia el juego
├── requirements.txt
├── README.md
├── save.json               # se crea solo al jugar
├── assets/                 # opcional: música, sonidos y fuentes propias
└── src/
    ├── settings.py         # resolución, física, paleta y rutas
    ├── art.py              # TODO el pixel art procedural
    ├── sprites.py          # utilidades de dibujo (rejillas, contornos)
    ├── input_manager.py    # InputManager + KeyboardInput + TouchInput
    ├── levels.py           # definición y generación de los 6 niveles
    ├── level.py            # nivel en ejecución, parallax y plataformas especiales
    ├── tilemap.py          # tiles sólidos, plataformas y pinchos
    ├── player.py           # física y animaciones del héroe
    ├── enemy.py            # 6 tipos de enemigos + jefe
    ├── projectile.py       # flores lanzadas y disparos enemigos
    ├── flower.py           # flores, girasoles, checkpoints y puerta
    ├── npc.py              # NPCs
    ├── camera.py           # cámara suave con shake
    ├── particles.py        # partículas y textos flotantes
    ├── dialogue.py         # cajas de diálogo con word wrapping
    ├── ui.py               # HUD, paneles, títulos con contorno
    ├── menu.py             # menús, selección de personaje y ajustes
    ├── scenes.py           # poder del girasol, entrega del ramo y final
    ├── inventory.py        # progreso de la partida
    ├── savegame.py         # guardado JSON tolerante a fallos
    └── game.py             # estados y bucle principal
```

---

## 🎵 Audio: qué puedes reemplazar

El juego sintetiza música y efectos, pero si colocas archivos propios se usan
esos automáticamente.

**Música** (`assets/music/`):
`exploration.ogg`, `tension.ogg`, `victory.ogg`, `final_theme.ogg`,
`flores_amarillas_final.ogg`

> `flores_amarillas_final.ogg` es el punto exacto en el que suena la canción al
> entregar el ramo. Coloca ahí **solo una pista que tengas autorización para usar**.
> Si el archivo no existe, se usa `final_theme.ogg` y el juego funciona igual.

**Efectos** (`assets/sounds/`, en `.wav` o `.ogg`):
`jump`, `crouch`, `attack`, `projectile`, `flower_collect`, `sunflower_power`,
`enemy_hit`, `enemy_death`, `player_damage`, `player_death`, `checkpoint`,
`dialogue`, `menu_select`, `menu_confirm`, `level_complete`, `final_bouquet`

**Fuente** (`assets/fonts/`): cualquier `.ttf` pixel art se usa en toda la interfaz.

En **Configuración** puedes activar/desactivar música y efectos y ajustar los
volúmenes; se guardan en `save.json`.

---

## 💾 Guardado

`save.json` guarda personaje, destinatario, nivel actual, nivel desbloqueado,
flores totales, poder y configuración de audio. Si el archivo no existe se crea,
y si está corrupto se repara solo.

---

## 📱 Sobre móvil

La arquitectura de entrada ya está preparada para táctil (`InputManager` con
`KeyboardInput` y `TouchInput`), con interfaz adaptable y botones grandes.
**Esto no convierte el proyecto en un APK**: para Android habría que empaquetarlo
después con una herramienta externa (por ejemplo python-for-android / Buildozer,
que requiere trabajo adicional). En PC funciona tal cual.

---

## 🛠️ Problemas frecuentes

| Problema | Solución |
|---|---|
| `python no se reconoce` | Reinstala Python marcando *Add Python to PATH* |
| `No module named pygame` | `pip install -r requirements.txt` con el entorno activo |
| No se escucha nada | Normal sin `numpy` o sin tarjeta de sonido; el juego funciona igual |
| La ventana se ve pequeña | `F11`, redimensiona la ventana o cambia `SCALE` en `src/settings.py` |
# 21_flore_amarillas
