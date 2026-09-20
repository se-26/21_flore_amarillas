"""Interfaz: texto legible con contorno, paneles pixel art, HUD y avisos."""
import math
import os

import pygame

from . import settings as S

_FONTS = {}

# Capa de texto en alta resolucion: reescala el texto a la resolucion real de
# la ventana y lo superpone al lienzo pixel-art, para que las letras se vean
# nitidas (nunca pixeladas ni borrosas).
_HIRES = None  # (superficie_base, factor, capa_tamanio_ventana)


def prepare_hires(base, scale):
    """Activa la capa nativa. Llama una vez por frame antes de dibujar."""
    global _HIRES
    q = int(round(scale))
    if q < 2:
        return None
    w = int(round(base.get_width() * scale))
    h = int(round(base.get_height() * scale))
    layer = pygame.Surface((w, h), pygame.SRCALPHA)
    try:
        layer = layer.convert_alpha()
    except pygame.error:
        pass
    _HIRES = (base, q, layer)
    return layer


def blit_hires(window, pos):
    if _HIRES:
        window.blit(_HIRES[2], pos)


def end_hires():
    global _HIRES
    _HIRES = None


def _hires_for(surf):
    if _HIRES and surf is _HIRES[0]:
        return _HIRES[2], _HIRES[1]
    return None, 1


def get_font(size):
    key = int(round(size))
    if key in _FONTS:
        return _FONTS[key]
    path = None
    if os.path.isdir(S.FONTS_DIR):
        for f in sorted(os.listdir(S.FONTS_DIR)):
            if f.lower().endswith((".ttf", ".otf")):
                path = os.path.join(S.FONTS_DIR, f)
                break
    if path:
        _FONTS[key] = pygame.font.Font(path, key)
    else:
        arial = pygame.font.match_font("arial")
        if arial:
            _FONTS[key] = pygame.font.Font(arial, key)
        else:
            _FONTS[key] = pygame.font.Font(None, key)
    return _FONTS[key]


def _render_aa(msg, size, color, q, alpha=None):
    img = get_font(size * q).render(msg, True, color)
    if alpha is not None and alpha < 255:
        img = img.copy()
        img.set_alpha(max(0, min(255, int(alpha))))
    return img


def text(surf, msg, pos, size=14, color=S.CREAM, shadow=S.DARK,
         center=False, right=False, alpha=None):
    layer, q = _hires_for(surf)
    img = _render_aa(msg, size, color, q, alpha)
    rect = img.get_rect()
    if center:
        rect.midtop = (pos[0] * q, pos[1] * q)
    elif right:
        rect.topright = (pos[0] * q, pos[1] * q)
    else:
        rect.topleft = (pos[0] * q, pos[1] * q)
    if layer is not None:
        if shadow:
            sh = _render_aa(msg, size, shadow, q, alpha)
            layer.blit(sh, (rect.x + q, rect.y + q))
        layer.blit(img, rect)
        return pygame.Rect(int(rect.x / q), int(rect.y / q),
                           max(1, rect.w // q), max(1, rect.h // q))
    if shadow:
        sh = _render_aa(msg, size, shadow, q, alpha)
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def title(surf, msg, pos, size=25, color=S.CREAM, outline_col=(28, 22, 34),
          center=True, alpha=None):
    """Texto grande con contorno completo: legible sobre cualquier fondo."""
    layer, q = _hires_for(surf)
    img = _render_aa(msg, size, color, q, alpha)
    out = _render_aa(msg, size, outline_col, q, alpha)
    rect = img.get_rect()
    if center:
        rect.midtop = (pos[0] * q, pos[1] * q)
    else:
        rect.topleft = (pos[0] * q, pos[1] * q)
    if layer is not None:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            layer.blit(out, (rect.x + dx * q, rect.y + dy * q))
        layer.blit(img, rect)
        return pygame.Rect(int(rect.x / q), int(rect.y / q),
                           max(1, rect.w // q), max(1, rect.h // q))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(out, (rect.x + dx, rect.y + dy))
    surf.blit(img, rect)
    return rect


def wrap(msg, size, max_w):
    font = get_font(size)
    lines, cur = [], ""
    for w in msg.split(" "):
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def panel(surf, rect, fill=(44, 38, 56), border=S.CREAM, alpha=236, accent=S.YELLOW_D,
          shadow=True):
    if shadow:
        sh = pygame.Surface(rect.size, pygame.SRCALPHA)
        sh.fill((14, 10, 20, 90))
        surf.blit(sh, (rect.x + 3, rect.y + 3))
    box = pygame.Surface(rect.size, pygame.SRCALPHA)
    r = box.get_rect()
    pygame.draw.rect(box, (*fill, alpha), pygame.Rect(0, 1, r.w, r.h - 2))
    pygame.draw.rect(box, (*fill, alpha), pygame.Rect(1, 0, r.w - 2, r.h))
    pygame.draw.rect(box, border, pygame.Rect(1, 0, r.w - 2, 1))
    pygame.draw.rect(box, border, pygame.Rect(1, r.h - 1, r.w - 2, 1))
    pygame.draw.rect(box, border, pygame.Rect(0, 1, 1, r.h - 2))
    pygame.draw.rect(box, border, pygame.Rect(r.w - 1, 1, 1, r.h - 2))
    pygame.draw.rect(box, accent, pygame.Rect(2, 2, r.w - 4, r.h - 4), 1)
    surf.blit(box, rect.topleft)


def bar(surf, rect, ratio, fill=S.YELLOW, back=(58, 50, 66)):
    pygame.draw.rect(surf, S.DARK, rect.inflate(2, 2))
    pygame.draw.rect(surf, back, rect)
    inner = rect.copy()
    inner.w = max(0, int(rect.w * max(0.0, min(1.0, ratio))))
    pygame.draw.rect(surf, fill, inner)
    if inner.w > 2:
        pygame.draw.rect(surf, S.GOLD, (inner.x, inner.y, inner.w, 1))


def prompt(surf, msg, x, y):
    font = get_font(11)
    r = pygame.Rect(0, 0, font.size(msg)[0] + 14, 17)
    r.midbottom = (int(x), int(y))
    r.clamp_ip(pygame.Rect(2, 2, S.GAME_W - 4, S.GAME_H - 4))
    panel(surf, r, fill=(32, 28, 44), alpha=228)
    text(surf, msg, (r.centerx, r.y + 3), 11, S.GOLD, center=True)


class HUD:
    def __init__(self, game):
        self.game = game

    def draw(self, surf):
        p = self.game.progress
        art = self.game.art
        box = pygame.Rect(4, 4, 112, 38)
        panel(surf, box, fill=(38, 32, 50), alpha=196, shadow=False)

        for i in range(S.MAX_HEARTS):
            img = art.heart_full if i < p.hearts else art.heart_empty
            surf.blit(img, (box.x + 6 + i * 10, box.y + 5))

        surf.blit(art.flower[0], (box.x + 4, box.y + 15))
        need = self.game.level.data.flowers_required if self.game.level else 0
        text(surf, f"{p.flowers:02d} / {need:02d}", (box.x + 18, box.y + 18), 12,
             S.GOLD if p.flowers >= need else S.CREAM)

        if p.power:
            for i in range(S.MAX_AMMO):
                icon = art.ammo.copy()
                if i >= p.ammo:
                    icon.set_alpha(70)
                surf.blit(icon, (box.x + 60 + i * 8, box.y + 17))

        if self.game.level and self.game.state != "pause":
            lv = self.game.level.data
            txt = f"NIVEL {lv.number}  {lv.name}"
            max_right = S.GAME_W - 4 - 32 - 4
            min_left = 118
            size = 12
            while size > 8 and max_right - (get_font(size).size(txt)[0] + 16) < min_left:
                size -= 1
            w = get_font(size).size(txt)[0] + 16
            r = pygame.Rect(max_right - w, 4, w, 20)
            panel(surf, r, fill=(38, 32, 50), alpha=196, shadow=False)
            text(surf, txt, (r.centerx, r.y + 4), size, S.CREAM, center=True)


class QuickPanel:
    """Boton de pausa en la esquina superior derecha durante el juego.

    El volumen y demas opciones se controlan dentro de la ventana de pausa.
    """

    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(S.GAME_W - 4 - 32, 4, 32, 20)

    def handle(self, event, to_internal=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = to_internal(event.pos) if to_internal else event.pos
        else:
            return False
        if not self.rect.collidepoint(pos):
            return False
        self.game.pause.index = 0
        self.game.prev_state = "play"
        self.game.state = "pause"
        self.game.audio.play("menu_confirm")
        return True

    def draw(self, surf):
        panel(surf, self.rect, fill=(38, 32, 50), alpha=200, shadow=False)
        x, y = self.rect.x, self.rect.y
        pygame.draw.rect(surf, S.YELLOW, (x + 10, y + 6, 3, 8))
        pygame.draw.rect(surf, S.YELLOW, (x + 16, y + 6, 3, 8))


class ObjectiveCard:
    """Tarjeta de objetivo al empezar cada nivel, con el estilo de los menus."""

    def __init__(self, level_data, backdrop=None):
        self.data = level_data
        self.backdrop = backdrop
        self.t = 0.0
        self.done = False

    def update(self, dt):
        self.t += dt
        if self.backdrop:
            self.backdrop.update(dt)
        if self.t > 4.2:
            self.done = True

    def skip(self):
        self.done = True

    def draw(self, surf):
        alpha = 255
        if self.t < 0.4:
            alpha = int(self.t / 0.4 * 255)
        elif self.t > 3.4:
            alpha = max(0, int((4.2 - self.t) / 0.8 * 255))
        layer = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        dim = pygame.Surface((S.GAME_W, S.GAME_H), pygame.SRCALPHA)
        dim.fill((14, 12, 22, 130))
        layer.blit(dim, (0, 0))
        if self.backdrop:
            self.backdrop.draw(layer)
        box = pygame.Rect(0, 0, 318, 128)
        box.center = (S.GAME_W // 2, S.GAME_H // 2)
        panel(layer, box, fill=(40, 34, 54))
        pygame.draw.line(layer, S.YELLOW_D, (box.x + 24, box.y + 66),
                         (box.right - 24, box.y + 66))
        layer.set_alpha(alpha)
        surf.blit(layer, (0, 0))
        title(surf, f"NIVEL {self.data.number}", (box.centerx, box.y + 10), 22, S.GOLD,
              alpha=alpha)
        title(surf, self.data.name, (box.centerx, box.y + 38), 17, S.CREAM,
              alpha=alpha)
        text(surf, "OBJETIVO", (box.centerx, box.y + 70), 12, S.YELLOW,
             center=True, alpha=alpha)
        for i, line in enumerate(self.data.objective):
            text(surf, line, (box.centerx, box.y + 88 + i * 15), 13, S.CREAM,
                 center=True, alpha=alpha)
