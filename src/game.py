"""Nucleo del juego de plataformas: estados, bucle y reglas."""
import asyncio
import math
import random

import pygame

from . import savegame, settings as S, ui
from . import keys as K
from .art import PlatformArt
from .audio import AudioManager
from .camera import Camera
from .dialogue import DialogueSystem
from .input_manager import InputManager
from .inventory import Progress
from .level import Level
from .menu import (CharacterSelect, ControlsScreen, DeathScreen,
                   LevelCompleteScreen, MainMenu, PauseMenu, PetalBackdrop,
                   SettingsMenu, TargetSelect)
from .particles import ParticleSystem
from .player import Player
from .projectile import Projectile
from .scenes import EndingScreen, FinalScene, PowerUnlockScene
from .ui import HUD, ObjectiveCard, QuickPanel

TOTAL_LEVELS = 6


class Game:
    def __init__(self):
        if S.IS_WEB:
            # La build web de pygame-ce (pygbag) no exporta todas las
            # constantes de escritorio (ej. pygame.K_a, pygame.RESIZABLE):
            # se inicializa por subsistemas y la ventana se crea dentro del
            # bucle asincrono con flags seguros (_init_display).
            pygame.display.init()
            pygame.font.init()
            self.window = None
            self.scale_rect = pygame.Rect(0, 0,
                                          S.GAME_W * S.SCALE, S.GAME_H * S.SCALE)
        else:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init()
            info = pygame.display.Info()
            self.window = pygame.display.set_mode(
                S.desktop_window_size(int(info.current_w),
                                      int(info.current_h)),
                pygame.RESIZABLE)
            pygame.display.set_caption(S.TITLE)
            self.scale_rect = self.window.get_rect()
        self.screen = pygame.Surface((S.GAME_W, S.GAME_H))
        if not S.IS_WEB:
            try:
                self.screen = self.screen.convert()
            except pygame.error:
                pass
        self.clock = pygame.time.Clock()
        self.running = True

        self.art = PlatformArt()
        try:
            pygame.display.set_icon(pygame.transform.scale(self.art.flower[0], (32, 32)))
        except Exception:
            pass
        self.audio = AudioManager()
        self.input = InputManager()

        self.particles = ParticleSystem(ui.get_font(11))
        self.dialogue = DialogueSystem(self)
        self.progress = Progress()
        self.hud = HUD(self)
        self.quick = QuickPanel(self)
        self.camera = Camera()

        self.menu = MainMenu(self)
        self.char_select = CharacterSelect(self)
        self.target_select = TargetSelect(self)
        self.settings_menu = SettingsMenu(self)
        self.pause = PauseMenu(self)
        self.controls = ControlsScreen(self)
        self.death = DeathScreen(self)
        self.complete = LevelCompleteScreen(self)
        self.ending = EndingScreen(self)

        self.state = "menu"
        self.prev_state = "menu"
        self.level = None
        self.player = None
        self.objective = None
        self.power_scene = None
        self.final = None
        self.projectiles = []
        self.enemy_shots = []
        self.checkpoint_pos = None
        self.notice = ""
        self.notice_t = 0.0
        self.fade = 0.0
        self.fade_state = None
        self.fade_cb = None
        self.tension_t = 0.0
        self.level_done = False
        self.interact_target = None
        if self.window is not None:
            self.scale_rect = self.window.get_rect()
        self.zoom = 1.0
        self._frame_key = None
        self._frame_surf = None

        data = savegame.load()
        self.audio.apply_config(data.get("audio", {}))
        self.progress.from_dict(data)
        self.audio.play_music("exploration")

    # ------------------------------------------------------------ utiles
    def _init_display(self):
        """Crea la ventana Pygame.

        En web se llama desde run() ya dentro del bucle asincrono, despues
        de ceder unas cuantas veces para que el runtime de pygbag (el
        window_resize() del template) deje el canvas listo. Se usa `0` como
        flags porque pygame.RESIZABLE no esta disponible en la build web.
        """
        if self.window is not None:
            return
        flags = 0 if S.IS_WEB else pygame.RESIZABLE
        self.window = pygame.display.set_mode(
            (S.GAME_W * S.SCALE, S.GAME_H * S.SCALE), flags)
        pygame.display.set_caption(S.TITLE)
        self.scale_rect = self.window.get_rect()

    def notify(self, msg, seconds=3.0):
        self.notice = msg
        self.notice_t = seconds

    def to_internal(self, pos):
        r = self.scale_rect
        if r.w == 0 or r.h == 0:
            return pos
        x = (pos[0] - r.x) * S.GAME_W / r.w
        y = (pos[1] - r.y) * S.GAME_H / r.h
        return (x, y)

    def transition(self, cb):
        if self.fade_state is None:
            self.fade_state = "out"
            self.fade_cb = cb

    def _update_fade(self, dt):
        if self.fade_state == "out":
            self.fade = min(1.0, self.fade + dt * 3.0)
            if self.fade >= 1.0:
                if self.fade_cb:
                    self.fade_cb()
                    self.fade_cb = None
                self.fade_state = "in"
        elif self.fade_state == "in":
            self.fade = max(0.0, self.fade - dt * 2.4)
            if self.fade <= 0.0:
                self.fade_state = None

    # ------------------------------------------------------- flujo de juego
    def start_new_game(self):
        self.progress.level_index = 0
        self.progress.unlocked = max(1, self.progress.unlocked)
        self.progress.power = False
        self.progress.ammo = 0
        self.progress.total_flowers = 0
        self.progress.deaths = 0
        self.start_level(0)

    def continue_game(self):
        data = savegame.load()
        self.progress.from_dict(data)
        if data.get("nivel_desbloqueado", 1) <= 1 and data.get("nivel_actual", 0) == 0 \
                and data.get("flores_totales", 0) == 0:
            return False
        self.start_level(self.progress.level_index)
        return True

    def start_level(self, index):
        index = max(0, min(TOTAL_LEVELS - 1, index))
        self.progress.level_index = index
        self.progress.reset_level()
        self.progress.ammo = 0
        self.level = Level(index, self)
        self.player = Player(self.art.heroes[self.progress.hero],
                             *self.level.spawn_point, self)
        self.checkpoint_pos = self.level.spawn_point
        self.camera.set_world(*self.level.pixel_size)
        self.camera.snap(self.player.rect)
        self.particles.clear()
        self.projectiles.clear()
        self.enemy_shots.clear()
        self.dialogue.active = False
        self.final = None
        self.power_scene = None
        self.objective = ObjectiveCard(self.level.data, PetalBackdrop(30))
        self.level_done = False
        self.zoom = 1.0
        self.state = "objective"
        self.audio.play_music(self.level.data.music)
        self.save_game()

    def next_level(self):
        nxt = self.progress.level_index + 1
        if nxt >= TOTAL_LEVELS:
            self.go_to_menu()
            return
        self.transition(lambda: self.start_level(nxt))
        self.state = "play"

    def go_to_menu(self):
        self.state = "menu"
        self.level = None
        self.player = None
        self.zoom = 1.0
        self.audio.play_music("exploration")

    def open_settings(self, origin):
        self.settings_menu.origin = origin
        self.prev_state = origin
        self.settings_menu.index = 0
        self.state = "settings"

    def close_settings(self):
        self.save_game()
        self.state = self.settings_menu.origin

    def save_game(self):
        data = self.progress.to_dict()
        data["audio"] = self.audio.config()
        savegame.save(data)

    # ------------------------------------------------------ vida y muerte
    def respawn_player(self):
        if not self.checkpoint_pos:
            return
        self.player.place(*self.checkpoint_pos)
        self.player.invuln = 1.2
        self.camera.snap(self.player.rect)

    def on_player_dead(self):
        self.progress.deaths += 1
        self.notice_t = 0.0
        self.death.reset()
        self.state = "death"

    def restart_level(self):
        """Reinicia desde el principio del nivel actual (se agotaron las vidas)."""
        self.start_level(self.progress.level_index)

    # ---------------------------------------------------------- proyectiles
    def spawn_projectile(self, player):
        x = player.rect.centerx + player.facing * 8
        y = player.rect.centery - 2
        self.projectiles.append(Projectile(self.art.projectile, x, y,
                                           player.facing * 190, -40, "player"))

    def spawn_enemy_shot(self, x, y, vx, vy):
        self.enemy_shots.append(Projectile(self.art.enemy_shot, x, y, vx, vy,
                                           "enemy", life=3.0))

    # ------------------------------------------------------------- escenas
    def start_power_scene(self, sunflower):
        sunflower.used = True
        self.power_scene = PowerUnlockScene(self, sunflower)
        self.state = "power"

    def end_power_scene(self):
        self.power_scene = None
        self.state = "play"
        self.notify("¡Pulsa X para lanzar flores!", 3.0)

    def start_final_scene(self):
        self.progress.total_flowers += self.progress.flowers
        door = self.level.door
        self.enemy_shots.clear()
        self.projectiles.clear()
        tx = door.rect.centerx + 20
        tiles = self.level.tiles
        col = int(tx) // S.TILE
        ty = door.rect.bottom
        for r in range(tiles.rows):
            if tiles.is_solid(col, r) or tiles.is_platform(col, r):
                ty = r * S.TILE
                break
        self.final = FinalScene(self, tx, ty)
        self.state = "final"

    def complete_level(self):
        if self.progress.level_index == TOTAL_LEVELS - 1:
            self.start_final_scene()
            return
        self.progress.total_flowers += self.progress.flowers
        self.progress.unlocked = max(self.progress.unlocked,
                                     self.progress.level_index + 2)
        self.progress.level_index += 1
        self.save_game()
        self.progress.level_index -= 1
        self.audio.play("level_complete")
        self.audio.play_music("victory", force=True)
        self.complete.start(self.level.data, self.progress.flowers)
        self.state = "level_complete"

    # ---------------------------------------------------------- eventos
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type == pygame.VIDEORESIZE:
                if S.IS_WEB:
                    continue
                self.window = pygame.display.set_mode((event.w, event.h),
                                                      pygame.RESIZABLE)
                continue
            if event.type == pygame.KEYDOWN and event.key == K.K_F11:
                try:
                    pygame.display.toggle_fullscreen()
                except pygame.error:
                    pass
                continue
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN,
                              pygame.KEYDOWN):
                self.audio.inicializar_audio_navegador()
            self.input.handle_event(event, self.to_internal)

            st = self.state
            if st == "menu":
                self.menu.handle(event, self.to_internal)
            elif st == "char_select":
                self.char_select.handle(event, self.to_internal)
            elif st == "target_select":
                self.target_select.handle(event, self.to_internal)
            elif st == "settings":
                self.settings_menu.handle(event, self.to_internal)
            elif st == "controls":
                self.controls.handle(event, self.to_internal)
            elif st == "pause":
                self.pause.handle(event, self.to_internal)
            elif st == "death":
                self.death.handle(event, self.to_internal)
            elif st == "level_complete":
                self.complete.handle(event, self.to_internal)
            elif st == "ending":
                self.ending.handle(event, self.to_internal)
            elif st == "objective":
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN,
                                  pygame.FINGERDOWN):
                    self.objective.skip()
            elif st == "play":
                self._play_event(event)

    def _play_event(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if self.quick.handle(event, self.to_internal):
                return
            # boton "continuar" del dialogo (mouse / touch)
            if self.dialogue.active:
                pos = None
                try:
                    if event.type == pygame.FINGERDOWN:
                        w, h = pygame.display.get_surface().get_size()
                        pos = self.to_internal((event.x * w, event.y * h))
                    else:
                        pos = self.to_internal(event.pos)
                except Exception:
                    pos = None
                if pos and self.dialogue.button_rect().collidepoint(pos):
                    self.dialogue.advance()
                    return
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == K.K_ESCAPE:
            self.pause.index = 0
            self.prev_state = "play"
            self.state = "pause"
        elif event.key == K.K_F5:
            self.save_game()
            self.notify("Partida guardada")

    # ------------------------------------------------------ interacciones
    def interact(self):
        target = self.interact_target
        if not target:
            return
        obj, kind = target
        if kind == "npc":
            obj.talked = True
            self.dialogue.start(obj.name, obj.lines)
        elif kind == "sunflower":
            if not self.progress.power:
                self.dialogue.start("", [
                    "¿Quieres descubrir su poder?",
                    "Ese girasol guarda una pequeña sorpresa...",
                ], on_end=lambda o=obj: self.start_power_scene(o))
            else:
                obj.used = True
                self.progress.add_ammo()
                self.audio.play("sunflower_power")
                self.particles.burst(obj.rect.centerx, obj.rect.centery,
                                     S.GOLD, 18, 90)
                self.particles.text(obj.rect.centerx, obj.rect.top, "Poder recargado")

    def find_interactable(self):
        if not self.level:
            return None
        p = self.player.rect
        best, bd = None, 9999
        for n in self.level.npcs:
            d = abs(n.rect.centerx - p.centerx) + abs(n.rect.centery - p.centery)
            if d < 34 and d < bd:
                best, bd = (n, "npc"), d
        for s in self.level.sunflowers:
            if s.used:
                continue
            d = abs(s.rect.centerx - p.centerx) + abs(s.rect.centery - p.centery)
            if d < 34 and d < bd:
                best, bd = (s, "sunflower"), d
        return best

    # ------------------------------------------------------------ update
    def update(self, dt):
        self.input.update()
        self._update_fade(dt)
        if self.notice_t > 0:
            self.notice_t -= dt

        st = self.state
        # Botones tactiles SOLO mientras se recorre el mundo: si hay un dialogo
        # o caja de texto activo se ocultan para no tapar la lectura.
        self.input.touch_active = (st == "play" and not self.dialogue.active)
        # el boton de flor solo aparece con el poder desbloqueado, y el de
        # interactuar solo cuando hay algo cerca.
        self.input.set_power(st == "play" and self.progress.power)
        self.input.set_interact(st == "play" and self.interact_target is not None
                                and not self.dialogue.active)
        if st == "menu":
            self.menu.update(dt)
        elif st == "char_select":
            self.char_select.update(dt)
        elif st == "target_select":
            self.target_select.update(dt)
        elif st == "death":
            self.death.update(dt)
            self.particles.update(dt)
        elif st == "level_complete":
            self.complete.update(dt)
            self.particles.update(dt)
        elif st == "ending":
            self.ending.update(dt)
        elif st == "objective":
            self.objective.update(dt)
            self.particles.update(dt)
            if self.objective.done:
                self.state = "play"
        elif st == "power":
            self.power_scene.update(dt)
            self.particles.update(dt)
            self.camera.update(dt, self.player.rect)
        elif st == "final":
            self._update_final(dt)
        elif st == "play":
            self._update_play(dt)

    def _update_final(self, dt):
        self.final.update(dt)
        self.player._physics(dt, self.level)
        self.player._animate(dt, forced="celebrate" if self.final.phase >= 1 else "walk")
        self.level.update(dt, self.player, self.particles)
        self.particles.update(dt)
        self.camera.update(dt, self.player.rect)

    def _update_play(self, dt):
        level, player, prog = self.level, self.player, self.progress
        talking = self.dialogue.active
        if talking:
            if self.input.pressed("interact") or self.input.pressed("jump"):
                self.dialogue.advance()
            player.vx = 0
            player._physics(dt, level)
            player._animate(dt)
            self.dialogue.update(dt)
        elif self.fade_state is None:
            if self.input.pressed("interact") and self.interact_target:
                self.interact()
            player.update(dt, level, self.input)

        level.update(dt, player, self.particles)
        self.particles.update(dt)

        # --------------------------------------------------- coleccionables
        for f in level.flowers:
            if not f.taken and player.hitbox.colliderect(f.rect):
                f.taken = True
                prog.flowers += 1
                self.audio.play("flower_collect")
                self.particles.burst(f.rect.centerx, f.rect.centery, S.YELLOW, 14, 80)
                self.particles.sparkle(f.rect.centerx, f.rect.centery, 6)
                self.particles.text(f.rect.centerx, f.rect.top - 4, "+1", S.GOLD)
        level.flowers = [f for f in level.flowers if not f.taken]

        for c in level.checkpoints:
            if not c.active and player.hitbox.colliderect(c.rect):
                c.active = True
                tiles = level.tiles
                col = int(c.rect.centerx) // S.TILE - 1
                row = int(c.rect.bottom) // S.TILE
                while row < tiles.rows and not (
                        tiles.is_solid(col, row) or tiles.is_platform(col, row)):
                    row += 1
                self.checkpoint_pos = (col * S.TILE,
                                       row * S.TILE - player.H)
                self.audio.play("checkpoint")
                self.particles.sparkle(c.rect.centerx, c.rect.top, 14)
                self.notify("CHECKPOINT", 1.6)

        # ------------------------------------------------------------ puerta
        door = level.door
        if door:
            need = level.data.flowers_required
            boss_ok = (not level.data.boss) or (level.boss is None) or level.boss.dead
            door.open = prog.flowers >= need and boss_ok
            if door.open and not self.level_done and self.fade_state is None \
                    and player.hitbox.colliderect(door.rect):
                self.level_done = True
                self.complete_level()
                return

        # ---------------------------------------------------------- enemigos
        atk = player.attack_rect()
        for e in level.enemies:
            if e.dying:
                continue
            if atk and atk.colliderect(e.rect):
                e.hurt(1, player.rect.centerx)
                player.attack_t = 0
                self.camera.shake(2, 0.16)
            if player.hitbox.colliderect(e.rect) and not player.dead:
                stomp = player.vy > 40 and player.rect.bottom <= e.rect.top + 10
                if stomp:
                    e.hurt(1, None)
                    player.vy = -200
                    self.audio.play("jump")
                else:
                    player.take_damage(e.rect.centerx, e.cfg["touch"])

        # ------------------------------------------------------- proyectiles
        for pr in self.projectiles:
            pr.update(dt, level, self.particles)
            for e in level.enemies:
                if not e.dying and pr.rect.colliderect(e.rect):
                    e.hurt(1, pr.x)
                    pr.explode(self.particles)
                    self.camera.shake(1.6, 0.14)
                    break
        self.projectiles = [p for p in self.projectiles if not p.dead]

        for sh in self.enemy_shots:
            sh.update(dt, level, self.particles)
            if sh.rect.colliderect(player.hitbox) and not player.dead:
                player.take_damage(sh.x)
                sh.explode(self.particles)
        self.enemy_shots = [p for p in self.enemy_shots if not p.dead]

        # ------------------------------------------------------------ pinchos
        for r in level.spike_rects(player.hitbox):
            if player.hitbox.colliderect(r):
                player.take_damage(None)
                break

        self.interact_target = self.find_interactable() if not talking else None
        self.camera.update(dt, player.rect)
        self._update_music(dt, level, player)

    def _update_music(self, dt, level, player):
        near = any(not e.dying and abs(e.rect.centerx - player.rect.centerx) < 150
                   and abs(e.rect.centery - player.rect.centery) < 110
                   for e in level.enemies)
        if near:
            self.tension_t = 2.5
        else:
            self.tension_t = max(0.0, self.tension_t - dt)
        want = "tension" if self.tension_t > 0 else level.data.music
        if want != self.audio.current:
            self.audio.play_music(want, fade_ms=700)

    # ------------------------------------------------------------- dibujo
    def draw_level(self):
        surf = self.screen
        self.level.draw_background(surf, self.camera)
        self.level.draw_decor(surf, self.camera)
        self.level.draw_world(surf, self.camera)
        for pr in self.projectiles:
            pr.draw(surf, self.camera)
        for sh in self.enemy_shots:
            sh.draw(surf, self.camera)
        if self.state == "final" and self.final:
            self.final.draw_target(surf, self.camera)
        self.player.draw(surf, self.camera)
        self.particles.draw(surf, self.camera)

    def draw(self):
        surf = self.screen
        win_w, win_h = self.window.get_size()
        self._draw_scale = min(win_w / S.GAME_W, win_h / S.GAME_H)
        layer = None
        if self.zoom == 1.0:
            layer = ui.prepare_hires(self.screen, self._draw_scale)
        surf.fill(S.SKY)
        st = self.state

        if st == "menu":
            self.menu.draw(surf)
        elif st == "char_select":
            self.char_select.draw(surf)
        elif st == "target_select":
            self.target_select.draw(surf)
        elif st == "ending":
            self.ending.draw(surf)
        elif st == "settings":
            if self.settings_menu.origin == "menu":
                self.menu.bg.draw(surf)
            elif self.level:
                self.draw_level()
                self.hud.draw(surf)
            self.settings_menu.draw(surf)
        elif st == "controls":
            if self.level:
                self.draw_level()
            else:
                self.menu.draw(surf)
            self.controls.draw(surf)
        elif self.level:
            self.draw_level()
            self.hud.draw(surf)
            if st == "play":
                if self.interact_target and not self.dialogue.active:
                    obj, kind = self.interact_target
                    msg = "E  Hablar" if kind == "npc" else "E  Descubrir"
                    x, y = self.camera.to_screen(obj.rect.centerx, obj.rect.top - 2)
                    ui.prompt(surf, msg, x, y)
                self.dialogue.draw(surf)
                self.input.draw(surf)
                self.quick.draw(surf)
            elif st == "objective":
                self.objective.draw(surf)
            elif st == "power":
                self.power_scene.draw(surf, self.camera)
            elif st == "final":
                self.final.draw_overlay(surf, self.camera)
            elif st == "pause":
                self.pause.draw(surf)
            elif st == "death":
                self.death.draw(surf)
            elif st == "level_complete":
                self.complete.draw(surf)

        if self.notice_t > 0:
            font = ui.get_font(12)
            r = pygame.Rect(0, 0, min(S.GAME_W - 20, font.size(self.notice)[0] + 22), 20)
            # En el menu de inicio el aviso (ej. "No hay progreso guardado
            # todavia") se muestra debajo de los botones para no tapar el
            # titulo "FLORES PARA TI"; en el resto de estados se mantiene arriba.
            if st == "menu":
                r.midtop = (S.GAME_W // 2, 180)
            else:
                r.midtop = (S.GAME_W // 2, 46)
            alpha = 255 if self.notice_t > 0.6 else int(self.notice_t * 420)
            ui.panel(surf, r, fill=(36, 30, 48), alpha=min(232, alpha), shadow=False)
            ui.text(surf, self.notice, (r.centerx, r.y + 4), 12, S.GOLD, center=True)

        if self.fade > 0:
            veil = pygame.Surface((S.GAME_W, S.GAME_H))
            veil.fill(S.BLACK)
            veil.set_alpha(int(self.fade * 255))
            surf.blit(veil, (0, 0))

        self._present()

    def _present(self):
        win_w, win_h = self.window.get_size()
        scale = getattr(self, "_draw_scale", min(win_w / S.GAME_W, win_h / S.GAME_H))
        w, h = int(S.GAME_W * scale), int(S.GAME_H * scale)
        x, y = (win_w - w) // 2, (win_h - h) // 2
        self.scale_rect = pygame.Rect(x, y, w, h)
        self.window.fill((10, 8, 14))
        source = self.screen
        if self.zoom != 1.0:
            z = max(1.0, self.zoom)
            zw, zh = S.GAME_W * z, S.GAME_H * z
            big = pygame.transform.scale(source, (int(zw), int(zh)))
            crop = pygame.Rect(int((zw - S.GAME_W) / 2), int((zh - S.GAME_H) / 2),
                               S.GAME_W, S.GAME_H)
            source = big.subsurface(crop)
        frame = None
        if self.zoom == 1.0 and self._frame_surf is not None \
                and self._frame_key == (w, h):
            pygame.transform.scale(source, (w, h), self._frame_surf)
            frame = self._frame_surf
        else:
            frame = pygame.transform.scale(source, (w, h))
            if self.zoom == 1.0:
                self._frame_key = (w, h)
                self._frame_surf = frame
        self.window.blit(frame, (x, y))
        ui.blit_hires(self.window, (x, y))
        ui.end_hires()
        pygame.display.flip()

    # -------------------------------------------------------------- bucle
    async def run(self):
        if S.IS_WEB:
            # dejar que el runtime de pygbag termine de ubicar el canvas
            # (custom_site -> window_resize) antes de crear la ventana.
            for _ in range(4):
                await asyncio.sleep(0)
        self._init_display()
        while self.running:
            dt = min(0.05, self.clock.tick(S.FPS) / 1000.0)
            self.handle_events()
            self.update(dt)
            self.draw()
            await asyncio.sleep(0)
        self.save_game()
        pygame.quit()
