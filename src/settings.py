"""Constantes globales del juego: resolucion, paleta y rutas."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
SAVE_PATH = os.path.join(BASE_DIR, "save.json")
CONFIG_PATH = os.path.join(BASE_DIR, "save.json")

# Resolucion interna pixel art (se escala a la ventana)
GAME_W, GAME_H = 384, 216
SCALE = 3
WINDOW_W, WINDOW_H = GAME_W * SCALE, GAME_H * SCALE
FPS = 60
TILE = 16
TITLE = "21 de Septiembre: Flores para Ti"

FLOWERS_GOAL = 10

# ------------- Fisica del plataformas -------------
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
