"""AudioManager: musica, efectos, fades y configuracion.

Prioridad: si existe el archivo en assets/ se usa; si no, se sintetiza con
numpy; si tampoco hay numpy o tarjeta de sonido, el juego sigue en silencio.
Nunca falla por un archivo ausente.

Musica y efectos se reproducen con pygame.mixer.Sound (NO mixer.music): en la
build web de pygbag, pygame.mixer.music.load() decodifica el OGG completo de
forma sincrona en el hilo principal cada vez que se cambia de pista y, con el
stream todavia en fade, su puente SDL<>JS se estancaba y congelaba TODO el
juego (personaje, controles y musica) nada mas avanzar al primer cambio de
tema. Por eso la musica web usa Sound precargado en loop:

  * Todas las pistas (archivos OGG) se decodifican UNA sola vez en el primer
    clic (_preload_web_music) y quedan como objetos Sound en RAM. Cambiar de
    tema durante el gameplay ya no lee ni decodifica nada: solo play/stop de
    un buffer ya en memoria.
  * La musica se reproduce SIEMPRE en un canal dedicado
    (pygame.mixer.Channel(0), creado con try/except): aunque el motor de
    audio del navegador ignore set_reserved, ningun SFX (canales automaticos)
    puede arrebatarle el canal y cortarla. Esto elimina el entrecorte que
    causaba la musica asignada a un canal cualquiera del pool y que un SFX
    pisara al sonar.
  * canales reservados (set_reserved) y 12 canales en total: suficientes para
    una oleada de efectos sin exceder lo que WebAudio mezcla en tiempo real
    en un movil (demasiadas fuentes simultaneas == entrecortes).
  * stop_music y set_music_volume tocan SOLO el canal/buffers de musica,
    nunca los efectos (SFX en self.sounds quedan intactos).

En escritorio el comportamiento es identico al clasico (Sound con carga
perezosa): no se altero nada.
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
        self._sound_cache = {}
        self.final_lock = None
        self._pending_music = None
        self._web_music = {}
        self._music_channel = None
        self._reserved_set = False
        if not S.IS_WEB:
            self._iniciar_audio()

    # ------------------------------------------------------------ encendido
    def _iniciar_audio(self):
        """Abre el mixer y carga sonidos. En la web se llama al primer clic."""
        try:
            if not pygame.mixer.get_init():
                # PC: 1024 (23 ms) en vez de 512 para dar margen al mixer contra
                # picos del hilo principal (presentacion/escala del frame) sin
                # notar latencia. En web se mantiene 4096 (limite de pygbag).
                buffer = 4096 if S.IS_WEB else 1024
                pygame.mixer.init(SR, -16, 2, buffer)
            if S.IS_WEB:
                # Canales equilibrados: suficientes para una oleada de SFX sin
                # exceder lo que el motor de audio del navegador mezcla en
                # tiempo real (demasiadas fuentes WebAudio simultaneas en un
                # movil de gama media == entrecortes). La musica se reserva.
                try:
                    pygame.mixer.set_num_channels(12)
                except Exception:
                    pass
                if not self._reserved_set:
                    try:
                        pygame.mixer.set_reserved(2)
                        self._reserved_set = True
                    except Exception:
                        self._reserved_set = False
                # Canal dedicado para la musica: aunque set_reserved no se
                # respete en la build web, la musica SIEMPRE se pincha aqui
                # explicitamente y ningun SFX (que usa canales automaticos)
                # puede robarle/arrebatarle el canal y cortarla.
                if self._music_channel is None:
                    try:
                        self._music_channel = pygame.mixer.Channel(0)
                    except Exception:
                        self._music_channel = None
        except Exception:
            print("El navegador bloque\u00f3 el audio temporalmente")
            return
        self.enabled = True
        try:
            self._scan_files()
        except Exception:
            pass
        if np is not None:
            try:
                self._synth()
            except Exception:
                pass
        if S.IS_WEB:
            try:
                self._preload_web_music()
            except Exception:
                pass

    def inicializar_audio_navegador(self):
        """Activa el audio una vez el jugador hizo su primer clic (autoplay
        de Chrome) y reanuda la musica del menu si quedo pendiente."""
        if self.enabled:
            return
        self._iniciar_audio()
        if self.enabled:
            key, fade_ms = self._pending_music or ("exploration", 600)
            self._pending_music = None
            self.play_music(key, fade_ms=fade_ms, force=True)

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
            pref = {}
            for f in sorted(os.listdir(S.MUSIC_DIR)):
                name, ext = os.path.splitext(f)
                ext = ext.lower()
                if ext not in (".ogg", ".mp3", ".wav"):
                    continue
                # Alias: "flores amarillas (...)" del usuario -> flores_amarillas_final
                low = name.lower()
                key = "flores_amarillas_final" \
                    if ("flores" in low and "amarill" in low) else name
                rank = (0 if ext == ".ogg" else 1 if ext == ".wav" else 2)
                prev = pref.get(key)
                if prev is None or rank < prev[1]:
                    pref[key] = (os.path.join(S.MUSIC_DIR, f), rank)
            self._file_music = {k: v[0] for k, v in pref.items()}

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
            self._pending_music = (key, fade_ms)
            return
        if self.final_lock and not force and key != self.final_lock:
            return
        if key == self.current and not force:
            return
        self.stop_music(fade_ms if not force else 0)
        self.current = key
        if not self.music_on:
            return
        self._start(key, fade_ms)

    def _preload_web_music(self):
        """Web: decodifica UNA sola vez todas las pistas de archivo (al primer
        clic, en el menu) y las deja en RAM listas para tocar en loop. Asi
        cambiar de tema durante el gameplay nunca lee ni decodifica el disco:
        solo play/stop de un buffer ya en memoria. Si una pista falla se quita
        de _file_music para que _start use la version sintetizada si existe."""
        for key, path in list(self._file_music.items()):
            try:
                self._web_music[key] = pygame.mixer.Sound(path)
            except Exception:
                self._file_music.pop(key, None)

    def _start(self, key, fade_ms=600):
        path = self._file_music.get(key)
        snd = None
        if S.IS_WEB:
            # Web: solo buffers ya precargados en memoria. Nunca abrir o
            # decodificar un archivo en pleno juego, es lo que congelaba el
            # hilo principal (pygame.mixer.music hacia exactamente eso en cada
            # cambio de tema).
            snd = self._web_music.get(key) or self.music.get(key)
            if snd is None:
                return
            # En la build web el fade se DESCARTA (fade_ms -> 0):
            #
            #   * Channel.play(loops=-1, fade_ms=N) sobre un buffer que acaba
            #     de pasar por fadeout (el tema anterior) es exactamente la
            #     secuencia que, en el audio WebAudio de pygbag (mezcla en el
            #     hilo principal JS), atasca el engine y CONGELA el juego al
            #     cambiar de tema con la musica encendida. La musica de menu
            #     (misma llamada pero sin fadeout previo ni SFX entrantes)
            #     nunca se congelaba: el disparador es el fadeout+play-fade en
            #     cadena, no el propio bucle.
            #   * El corte/paso al cambiar de tema pierde el crossfade suave,
            #     pero en web un corte brusco infinitamente preferible a un
            #     bloqueo total del hilo principal. En escritorio los fades se
            #     conservan intactos.
            fade_ms = 0
        else:
            try:
                if path:
                    if path not in self._sound_cache:
                        self._sound_cache[path] = pygame.mixer.Sound(path)
                    snd = self._sound_cache[path]
                else:
                    snd = self.music.get(key)
            except Exception:
                snd = self.music.get(key)
            if snd is None:
                return
        snd.set_volume(self.music_volume)
        fade_ms = 0 if S.IS_WEB else fade_ms
        if S.IS_WEB and self._music_channel is not None:
            try:
                self._music_channel.play(snd, loops=-1, fade_ms=fade_ms)
                return
            except Exception:
                pass
        try:
            snd.play(loops=-1, fade_ms=fade_ms)
        except Exception:
            try:
                snd.play(loops=-1)
            except Exception:
                pass

    def play_final_song(self):
        """Pista final: usa flores_amarillas_final.ogg si existe."""
        key = "flores_amarillas_final" if "flores_amarillas_final" in self._file_music \
            else "final_theme"
        self.final_lock = key
        self.play_music(key, fade_ms=900, force=True)

    def stop_music(self, fade_ms=400):
        if not self.enabled:
            return
        if S.IS_WEB and self._music_channel is not None:
            # Web: corte SECO, nunca fade.
            #
            #   * En el audio WebAudio de pygbag, encadenar un fadeout del
            #     canal dedicado (o de TODOS los buffers de musica, como hacia
            #     el bucle de abajo) con un play(loops=-1, fade_ms) inmediato
            #     en el MISMO canal dejaba al engine JS esperando a que el
            #     canal se libere del fade y congelaba TODO el juego en el
            #     primer cambio de tema. El menu nunca lo disparaba porque
            #     ahi no hay stop/play en cadena (solo el primer play).
            #   * Solucion web: stop() puro del canal y cero fades. El buffer
            #     que suena vive solo en ese canal, asi que con parar el canal
            #     basta; no hace falta (y congelaba) tocar uno a uno los otros
            #     buffers. Cambiar de tema es entonces: stop() + play() sin
            #     ningun fade ni espera => no hay nada en lo que atascarse.
            #   * En escritorio si se mantienen los fades tal cual.
            try:
                self._music_channel.stop()
            except Exception:
                pass
            return
        if S.IS_WEB:
            # Web (sin canal dedicado): solo los buffers de musica.
            targets = set(self.music.values()) | set(self._web_music.values())
        else:
            targets = set(self.music.values()) | set(self._sound_cache.values())
        for snd in targets:
            try:
                if fade_ms:
                    snd.fadeout(int(fade_ms))
                else:
                    snd.stop()
            except Exception:
                pass

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
        if S.IS_WEB and self._music_channel is not None:
            try:
                self._music_channel.set_volume(self.music_volume)
            except Exception:
                pass
        targets = set(self.music.values()) | set(self._sound_cache.values())
        if S.IS_WEB:
            targets |= set(self._web_music.values())
        for snd in targets:
            try:
                snd.set_volume(self.music_volume)
            except Exception:
                pass

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
