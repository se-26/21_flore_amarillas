"""Constantes globales del juego: resolucion, paleta y rutas."""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
SAVE_PATH = os.path.join(BASE_DIR, "save.json")
CONFIG_PATH = os.path.join(BASE_DIR, "save.json")


def _detect_web():
    """True si corre dentro de un navegador (build pygbag/emscripten)."""
    try:
        if "emscripten" in str(getattr(sys, "platform", "")):
            return True
        import platform
        return "Emscripten" in platform.system()
    except Exception:
        return False


IS_WEB = _detect_web()


def _touch_window():
    """Devuelve el objeto 'window' del navegador en la build web (o None)."""
    try:
        from platform import window  # pygbag
        return window if window is not None else None
    except Exception:
        try:
            from browser import window  # fallback
            return window
        except Exception:
            return None


def _detect_mobile():
    """True solo cuando hay capacidad tactil REAL (o un UA movil).

    En escritorio nativo es siempre False (no hay navegador). En la web se
    consultan las capacidades del navegador (maxTouchPoints / ontouchstart /
    pointer:coarse), NUNCA el tamaño de ventana: el bug anterior devolvia True
    para cualquier build emscripten y mostraba los controles tactiles en un
    Chrome de PC. El userAgent queda como ultimo recurso.
    """
    if not IS_WEB:
        return False
    try:
        w = _touch_window()
        if w is not None:
            if float(w.maxTouchPoints or 0) > 0:
                return True
            if getattr(w, "ontouchstart", None) is not None:
                return True
            try:
                media = w.matchMedia("(pointer: coarse)")
                if bool(getattr(media, "matches", False)):
                    return True
            except Exception:
                pass
    except Exception:
        pass
    try:
        from browser import navigator
        ua = (navigator.userAgent or "").lower()
    except Exception:
        ua = ""
    return any(k in ua for k in ("mobile", "android", "iphone",
                                 "ipad", "webos", "blackberry"))


IS_MOBILE = _detect_mobile()

# Resolucion interna pixel art (se escala a la ventana)
GAME_W, GAME_H = 384, 216
# SOLO WEB usa SCALE=2 (384x216 -> framebuffer 768x432): el coste de
# presentar/componer el framebuffer es el principal gasto en la build web
# (antes 1152x648 con SCALE=3). PC conserva SCALE=3 porque funciona excelente.
SCALE = 2 if IS_WEB else 3
WINDOW_W, WINDOW_H = GAME_W * SCALE, GAME_H * SCALE
FPS = 60


def desktop_window_size(screen_w, screen_h):
    """Tamano inicial de la ventana en escritorio: 16:9 que llena ~90% del
    alto disponible del monitor (nunca pasa del ancho ni es menor que el
    tamano base del pixel art). La resolucion logica del juego no cambia:
    el render se escala a lo que ocupe la ventana."""
    h = int(float(screen_h) * 0.9)
    w = int(h * 16 / 9)
    w = min(w, int(float(screen_w)))
    base_w, base_h = GAME_W * SCALE, GAME_H * SCALE
    return (max(base_w, w), max(base_h, h))
TILE = 16
TITLE = "21 de Septiembre: Flores para Ti"

FLOWERS_GOAL = 10

# ------------- Fisica del plataformas -------------
# ---------------- Musica: histeresis de tension ----------------
# La transicion de pista entre "exploracion" (tema del nivel) y "tension" se
# hace con histeresis para que el tema no cambie a la minima fluctuacion.
#
#   * ENTRAR en tension exige que algun enemigo vivo permanezca DENTRO de la
#     caja NEAR un tiempo sostenido (TENSION_ENTER_T). Evita activar tension
#     por un enemigo que patrulla y cruza el borde un instante.
#   * SALIR exige que TODOS los enemigos queden FUERA de la caja FAR (mas
#     grande que NEAR) un tiempo largo y sostenido (TENSION_EXIT_T). Asi una
#     pista no se corta a la minima que el enemigo se aleja y vuelve.
#
# La caja FAR amplia + los tiempos de espera dan histeresis: el tema no
# "flipea" cuando un enemigo esta justo en el limite, evitando reinicios
# constantes de la misma pista de musica.
TENSION_NEAR_X = 150.0
TENSION_NEAR_Y = 110.0
TENSION_FAR_X = 260.0
TENSION_FAR_Y = 200.0
TENSION_ENTER_T = 0.30
TENSION_EXIT_T = 2.5

GRAVITY = 900.0
MAX_FALL = 420.0
ACCEL = 1000.0
FRICTION = 1500.0
AIR_ACCEL = 700.0
WALK_SPEED = 78.0
RUN_SPEED = 118.0
CROUCH_SPEED = 38.0
JUMP_VELOCITY = -272.0
AIR_JUMP_VELOCITY = -320.0
MAX_JUMPS = 2
JUMP_CUT = 0.42
COYOTE_TIME = 0.10
JUMP_BUFFER = 0.12
MAX_HEARTS = 3
INVULN_TIME = 1.2
ATTACK_COOLDOWN = 0.38
THROW_COOLDOWN = 0.32
MAX_AMMO = 5

# ---------------- Paleta ----------------
BLACK      = (18, 16, 22)
DARK       = (38, 34, 46)
INK        = (56, 46, 62)
WHITE      = (250, 248, 240)
CREAM      = (255, 244, 214)
CREAM_D    = (226, 206, 168)

YELLOW     = (255, 214, 74)
YELLOW_D   = (226, 162, 40)
GOLD       = (255, 238, 150)
ORANGE     = (240, 148, 66)
ORANGE_D   = (198, 106, 52)

GREEN_L    = (158, 212, 104)
GREEN      = (112, 182, 88)
GREEN_D    = (68, 138, 76)
GREEN_DD   = (42, 96, 58)
GREEN_NIGHT= (34, 74, 62)

SKY        = (142, 202, 236)
SKY_D      = (104, 172, 214)

WATER_L    = (146, 208, 234)
WATER      = (86, 164, 206)
WATER_D    = (54, 118, 172)

BROWN_L    = (188, 142, 94)
BROWN      = (146, 100, 62)
BROWN_D    = (96, 64, 44)

STONE_L    = (188, 186, 192)
STONE      = (156, 154, 162)
STONE_D    = (110, 108, 120)

PINK       = (248, 188, 198)
PINK_D     = (222, 142, 158)
RED        = (214, 86, 86)
PURPLE     = (168, 132, 198)
NIGHT      = (46, 52, 104)

# Tintes ambientales por zona (color, alpha)
TINT_NONE   = None
TINT_FOREST = ((40, 78, 96), 62)
TINT_SUNSET = ((255, 138, 62), 78)
TINT_GARDEN = ((255, 196, 92), 52)


# ---------------- Colores extra (plataformas) ----------------
MAGENTA    = (214, 122, 196)
VIOLET     = (128, 96, 176)
VIOLET_D   = (78, 58, 120)
TEAL       = (86, 188, 176)
DREAM_BG   = (54, 40, 96)
DREAM_BG2  = (96, 62, 132)
SKY_UP     = (120, 190, 236)
SKY_DOWN   = (206, 238, 246)
CRYSTAL    = (150, 216, 238)
CRYSTAL_D  = (86, 152, 196)
WOOD       = (168, 118, 72)
WOOD_D     = (112, 74, 48)
HEART_RED  = (236, 96, 112)
HEART_D    = (170, 52, 74)
