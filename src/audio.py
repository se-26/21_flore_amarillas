"""AudioManager: musica, efectos, fades y configuracion.

Prioridad: si existe el archivo en assets/ se usa; si no, se sintetiza con
numpy; si tampoco hay numpy o tarjeta de sonido, el juego sigue en silencio.
Nunca falla por un archivo ausente.
"""
import os

import pygame

from . import settings as S

try:
    import numpy as np
except Exception:           # pragma: no cover
    np = None

SR = 44100

MUSIC_KEYS = ("exploration", "tension", "victory", "final_theme",
              "flores_amarillas_final")

SFX_KEYS = ("jump", "crouch", "attack", "projectile", "flower_collect",
            "sunflower_power", "enemy_hit", "enemy_death", "player_damage",
            "player_death", "checkpoint", "dialogue", "menu_select",
            "menu_confirm", "level_complete", "final_bouquet")

ALIASES = {
    "pick": "flower_collect", "talk": "dialogue", "select": "menu_select",
    "confirm": "menu_confirm", "special": "sunflower_power",
    "quest": "level_complete", "final": "final_bouquet", "step": "crouch",
}

NOTES = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.00,
         "A": 440.00, "B": 493.88, "C5": 523.25, "D5": 587.33, "E5": 659.25,
         "F5": 698.46, "G5": 783.99, "A5": 880.00, "C6": 1046.5, "E6": 1318.5}


def _env(n, attack=0.008, release=0.25):
    e = np.ones(n)
    a = max(1, int(SR * attack))
    r = max(1, min(n - 1, int(SR * release)))
    e[:a] = np.linspace(0, 1, a)
    e[-r:] = np.linspace(1, 0, r)
    return e


def _tone(freq, dur, vol=0.35, wave="sine", release=None):
    n = max(2, int(SR * dur))
    t = np.linspace(0, dur, n, endpoint=False)
    if wave == "square":
        w = np.sign(np.sin(2 * np.pi * freq * t)) * 0.45
    elif wave == "tri":
        w = 2 * np.abs(2 * ((t * freq) % 1) - 1) - 1
    elif wave == "noise":
        w = np.random.uniform(-1, 1, n)
    else:
        w = np.sin(2 * np.pi * freq * t) + 0.28 * np.sin(4 * np.pi * freq * t)
    return w * _env(n, 0.006, release if release is not None else min(0.3, dur * 0.8)) * vol


def _sweep(f0, f1, dur, vol=0.3, wave="sine"):
    n = max(2, int(SR * dur))
    t = np.linspace(0, dur, n, endpoint=False)
    f = np.linspace(f0, f1, n)
    ph = np.cumsum(2 * np.pi * f / SR)
    w = np.sin(ph) if wave == "sine" else np.sign(np.sin(ph)) * 0.5
    return w * _env(n) * vol


def _sound(mono):
    mono = np.clip(mono, -1, 1)
    data = (mono * 23000).astype(np.int16)
    return pygame.sndarray.make_sound(np.ascontiguousarray(np.column_stack((data, data))))


class AudioManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.music = {}
        self.current = None
        self.music_on = True
        self.sfx_on = True
        self.music_volume = 0.45
        self.sfx_volume = 0.6
        self._file_music = {}
        try:
            pygame.mixer.init(SR, -16, 2, 512)
            self.enabled = True
        except Exception:
            return
        self._scan_files()
        if np is not None:
            self._synth()

    # ------------------------------------------------------------ carga
    def _scan_files(self):
        if os.path.isdir(S.SOUNDS_DIR):
            for f in os.listdir(S.SOUNDS_DIR):
                name, ext = os.path.splitext(f)
                if ext.lower() in (".wav", ".ogg"):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(
                            os.path.join(S.SOUNDS_DIR, f))
                    except Exception:
                        pass
        if os.path.isdir(S.MUSIC_DIR):
            for f in os.listdir(S.MUSIC_DIR):
                name, ext = os.path.splitext(f)
                if ext.lower() in (".ogg", ".mp3", ".wav"):
                    self._file_music[name] = os.path.join(S.MUSIC_DIR, f)
            # Alias: "flores amarillas (...)" del usuario -> flores_amarillas_final
            for name, path in list(self._file_music.items()):
                low = name.lower()
                if "flores" in low and "amarill" in low and \
                        "flores_amarillas_final" not in self._file_music:
                    self._file_music["flores_amarillas_final"] = path

    def _synth(self):
        def add(name, samples):
            if name not in self.sounds:
                self.sounds[name] = _sound(samples)

        add("jump", _sweep(300, 640, 0.14, 0.3, "square"))
        add("crouch", _tone(150, 0.07, 0.2, "tri"))
        add("attack", np.concatenate([_tone(420, .05, .3, "square"),
                                      _tone(300, .07, .22, "square")]))
        add("projectile", _sweep(700, 1200, 0.16, 0.28))
        # "PLIN" de la flor
        add("flower_collect", np.concatenate([
            _tone(NOTES["E6"], .05, .34), _tone(NOTES["A5"], .10, .28)]))
        add("sunflower_power", np.concatenate([
            _tone(NOTES["C5"], .10), _tone(NOTES["E5"], .10), _tone(NOTES["G5"], .10),
            _tone(NOTES["C6"], .40, .4)]))
        add("enemy_hit", np.concatenate([_tone(220, .05, .3, "square"),
                                         _tone(160, .07, .22, "noise")]))
        add("enemy_death", np.concatenate([_sweep(500, 120, .22, .3, "square"),
                                           _tone(90, .12, .2, "noise")]))
        add("player_damage", np.concatenate([_tone(200, .08, .34, "square"),
                                             _sweep(240, 110, .18, .3)]))
        add("player_death", np.concatenate([_sweep(420, 90, .5, .34),
                                            _tone(90, .3, .22, "tri")]))
        add("checkpoint", np.concatenate([_tone(NOTES["G"], .09), _tone(NOTES["C5"], .09),
                                          _tone(NOTES["E5"], .26)]))
        add("dialogue", _tone(NOTES["G"], .045, .16, "tri"))
        add("menu_select", _tone(NOTES["D5"], .05, .22, "square"))
        add("menu_confirm", np.concatenate([_tone(NOTES["G"], .06, .26),
                                            _tone(NOTES["C5"], .14, .26)]))
        add("level_complete", np.concatenate([
            _tone(NOTES["C5"], .12), _tone(NOTES["E5"], .12), _tone(NOTES["G5"], .12),
            _tone(NOTES["C6"], .38, .4)]))
        add("final_bouquet", np.concatenate([
            _tone(NOTES["F"], .22), _tone(NOTES["A"], .22), _tone(NOTES["C5"], .22),
            _tone(NOTES["F5"], .7, .38)]))

        if "exploration" not in self._file_music:
            self.music["exploration"] = _sound(self._melody(
                ["C5", "E5", "G5", "E5", "A", "C5", "E5", "D5",
                 "F", "A", "C5", "A", "G", "B", "D5", "G5"], .40, .11))
        if "tension" not in self._file_music:
            self.music["tension"] = _sound(self._melody(
                ["A", "A", "C5", "B", "E", "E", "G", "F",
                 "D", "D", "F", "E", "A", "C5", "E5", "D5"], .26, .12, "tri"))
        if "victory" not in self._file_music:
            self.music["victory"] = _sound(np.concatenate([
                _tone(NOTES["C5"], .14, .3), _tone(NOTES["E5"], .14, .3),
                _tone(NOTES["G5"], .14, .3), _tone(NOTES["C6"], .5, .34)]))
        if "final_theme" not in self._file_music:
            self.music["final_theme"] = _sound(self._melody(
                ["F", "A", "C5", "A", "G", "B", "D5", "B",
                 "E", "G", "C5", "G", "F", "A", "F5", "C5"], .62, .12))

    def _melody(self, notes, dur, vol, wave="sine"):
        out = []
        for n in notes:
            f = NOTES[n]
            out.append(_tone(f, dur, vol, wave) + _tone(f / 2, dur, vol * .45, "tri"))
        return np.concatenate(out)

    # ------------------------------------------------------------ efectos
    def play(self, name, volume=None):
        if not self.enabled or not self.sfx_on:
            return
        name = ALIASES.get(name, name)
        snd = self.sounds.get(name)
        if snd:
            snd.set_volume(self.sfx_volume if volume is None else volume)
            snd.play()

    # ------------------------------------------------------------ musica
    def play_music(self, key, fade_ms=600, force=False):
        if not self.enabled:
            return
        if key == self.current and not force:
            return
        self.stop_music(fade_ms if not force else 0)
        self.current = key
        if not self.music_on:
            return
        self._start(key, fade_ms)

    def _start(self, key, fade_ms=600):
        path = self._file_music.get(key)
        try:
            if path:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1, fade_ms=fade_ms)
            elif key in self.music:
                snd = self.music[key]
                snd.set_volume(self.music_volume)
                snd.play(loops=-1, fade_ms=fade_ms)
        except Exception:
            pass

    def play_final_song(self):
        """Pista final: usa flores_amarillas_final.ogg si existe."""
        key = "flores_amarillas_final" if "flores_amarillas_final" in self._file_music \
            else "final_theme"
        self.play_music(key, fade_ms=900, force=True)

    def stop_music(self, fade_ms=400):
        if not self.enabled:
            return
        try:
            if fade_ms:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
        except Exception:
            pass
        for snd in self.music.values():
            if fade_ms:
                snd.fadeout(fade_ms)
            else:
                snd.stop()

    # --------------------------------------------------------- ajustes
    def set_music_on(self, value):
        self.music_on = bool(value)
        if not self.music_on:
            self.stop_music(300)
        elif self.current:
            self._start(self.current)

    def set_sfx_on(self, value):
        self.sfx_on = bool(value)

    def set_music_volume(self, value):
        self.music_volume = round(max(0.0, min(1.0, value)), 2)
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass
        for snd in self.music.values():
            snd.set_volume(self.music_volume)

    def set_sfx_volume(self, value):
        self.sfx_volume = round(max(0.0, min(1.0, value)), 2)

    def config(self):
        return {"musica": self.music_on, "efectos": self.sfx_on,
                "volumen_musica": round(self.music_volume, 2),
                "volumen_efectos": round(self.sfx_volume, 2)}

    def apply_config(self, cfg):
        self.music_on = bool(cfg.get("musica", True))
        self.sfx_on = bool(cfg.get("efectos", True))
        self.set_music_volume(float(cfg.get("volumen_musica", 0.45)))
        self.set_sfx_volume(float(cfg.get("volumen_efectos", 0.6)))
