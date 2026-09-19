"""Heroe del modo plataformas: fisica, estados y combate."""
import pygame

from . import settings as S


class Player:
    W, H = 11, 22

    def __init__(self, frames, x, y, game):
        self.frames = frames
        self.game = game
        self.rect = pygame.Rect(int(x), int(y), self.W, self.H)
        self.fx, self.fy = float(x), float(y)
        self.vx = self.vy = 0.0
        self.facing = 1
        self.on_ground = False
        self.was_on_ground = False
        self.crouching = False
        self.state = "idle"
        self.anim_t = 0.0
        self.coyote = 0.0
        self.buffer = 0.0
        self.jumps = S.MAX_JUMPS - 1
        self.air_jumped = False
        self.attack_t = 0.0
        self.cooldown = 0.0
        self.hurt_t = 0.0
        self.invuln = 0.0
        self.dead = False
        self.dead_t = 0.0
        self.celebrating = False
        self.land_t = 0.0
        self.dust_t = 0.0
        self.riding = None

    # ------------------------------------------------------------ ayuda
    def sync(self):
        self.rect.x = int(round(self.fx))
        self.rect.y = int(round(self.fy))

    def place(self, x, y):
        self.fx, self.fy = float(x), float(y)
        self.vx = self.vy = 0.0
        self.jumps = S.MAX_JUMPS - 1
        self.air_jumped = False
        self.sync()

    @property
    def hitbox(self):
        if self.crouching:
            r = self.rect.copy()
            r.height = 14
            r.bottom = self.rect.bottom
            return r
        return self.rect

    def attack_rect(self):
        if self.attack_t <= 0:
            return None
        r = pygame.Rect(0, 0, 18, 16)
        r.centery = self.rect.centery
        if self.facing > 0:
            r.left = self.rect.right - 2
        else:
            r.right = self.rect.left + 2
        return r

    # ---------------------------------------------------------- acciones
    def jump(self):
        self.vy = S.JUMP_VELOCITY
        self.on_ground = False
        self.coyote = 0.0
        self.buffer = 0.0
        self.air_jumped = False
        self.game.audio.play("jump")

    def air_jump(self):
        self.jumps -= 1
        self.air_jumped = True
        self.vy = S.AIR_JUMP_VELOCITY
        self.coyote = 0.0
        self.buffer = 0.0
        self.game.audio.play("jump")
        self.game.particles.burst(self.rect.centerx, self.rect.bottom,
                                  S.GOLD, 8, 66, 0.35, 1, 100)
        self.game.particles.sparkle(self.rect.centerx, self.rect.bottom, 4)

    def attack(self):
        prog = self.game.progress
        if prog.power and prog.ammo > 0:
            prog.ammo -= 1
            self.state = "throw"
            self.anim_t = 0.0
            self.attack_t = 0.18
            self.cooldown = S.THROW_COOLDOWN
            self.game.spawn_projectile(self)
            self.game.audio.play("projectile")
        else:
            self.state = "attack"
            self.anim_t = 0.0
            self.attack_t = 0.22
            self.cooldown = S.ATTACK_COOLDOWN
            self.game.audio.play("attack")

    def take_damage(self, source_x=None, amount=1):
        if self.invuln > 0 or self.dead:
            return False
        prog = self.game.progress
        prog.hearts -= amount
        self.invuln = S.INVULN_TIME
        self.hurt_t = 0.35
        d = 1 if source_x is None or source_x < self.rect.centerx else -1
        self.vx = d * 110
        self.vy = -150
        self.game.camera.shake(3.2, 0.3)
        self.game.particles.burst(self.rect.centerx, self.rect.centery,
                                  S.HEART_RED, 12, 70)
        if prog.hearts <= 0:
            prog.hearts = 0
            self.die()
        else:
            self.game.audio.play("player_damage")
        return True

    def die(self):
        if self.dead:
            return
        self.dead = True
        self.dead_t = 0.0
        self.vy = -190
        self.state = "dead"
        self.game.audio.play("player_death")
        self.game.camera.shake(4, 0.4)

    # -------------------------------------------------------------- ciclo
    def update(self, dt, level, inp):
        if self.dead:
            self.dead_t += dt
            self.vy = min(S.MAX_FALL, self.vy + S.GRAVITY * dt)
            self.fy += self.vy * dt
            self.sync()
            if self.dead_t > 1.1:
                self.game.on_player_dead()
            return

        self.invuln = max(0.0, self.invuln - dt)
        self.hurt_t = max(0.0, self.hurt_t - dt)
        self.attack_t = max(0.0, self.attack_t - dt)
        self.cooldown = max(0.0, self.cooldown - dt)
        self.land_t = max(0.0, self.land_t - dt)

        if self.celebrating:
            self.vx = 0
            self._physics(dt, level)
            self._animate(dt, forced="celebrate")
            return

        left = inp.down("left")
        right = inp.down("right")
        want_crouch = inp.down("down") and self.on_ground
        was_crouch = self.crouching
        self.crouching = want_crouch and not (left or right)
        if self.crouching and not was_crouch:
            self.game.audio.play("crouch")

        target = 0.0
        if left and not right:
            target = -1
            self.facing = -1
        elif right and not left:
            target = 1
            self.facing = 1

        keys = pygame.key.get_pressed()
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = S.CROUCH_SPEED if self.crouching else (
            S.RUN_SPEED if running else S.WALK_SPEED)
        accel = S.ACCEL if self.on_ground else S.AIR_ACCEL

        if target != 0 and self.hurt_t <= 0:
            self.vx += target * accel * dt
            self.vx = max(-speed, min(speed, self.vx))
        else:
            fric = S.FRICTION if self.on_ground else S.FRICTION * 0.35
            if self.vx > 0:
                self.vx = max(0.0, self.vx - fric * dt)
            else:
                self.vx = min(0.0, self.vx + fric * dt)

        # salto con coyote time, buffer y doble salto
        if inp.pressed("jump"):
            self.buffer = S.JUMP_BUFFER
        self.buffer = max(0.0, self.buffer - dt)
        if self.buffer > 0 and not self.crouching:
            if self.on_ground or self.coyote > 0:
                self.jump()
            elif self.jumps > 0:
                self.air_jump()
        if inp.released("jump") and self.vy < 0 and not self.air_jumped:
            self.vy *= S.JUMP_CUT

        if inp.pressed("attack") and self.cooldown <= 0:
            self.attack()

        self._physics(dt, level)
        self._animate(dt)

        # polvo al correr: solo al moverse en horizontal, sin agacharse
        if self.on_ground and not self.crouching and target != 0 and abs(self.vx) > 60:
            self.dust_t -= dt
            if self.dust_t <= 0:
                self.dust_t = 0.12
                self.game.particles.dust(self.rect.centerx, self.rect.bottom - 1)

    def _physics(self, dt, level):
        self.was_on_ground = self.on_ground
        self.vy = min(S.MAX_FALL, self.vy + S.GRAVITY * dt)

        # ---- eje X
        self.fx += self.vx * dt
        self.sync()
        for r in level.solid_rects(self.rect):
            if self.rect.colliderect(r):
                if self.vx > 0:
                    self.rect.right = r.left
                elif self.vx < 0:
                    self.rect.left = r.right
                self.fx = self.rect.x
                self.vx = 0

        # ---- eje Y
        prev_bottom = self.rect.bottom
        self.fy += self.vy * dt
        self.sync()
        self.on_ground = False
        for r in level.solid_rects(self.rect):
            if self.rect.colliderect(r):
                if self.vy > 0:
                    self.rect.bottom = r.top
                    self.on_ground = True
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = r.bottom
                    self.vy = 0
                self.fy = self.rect.y
        if self.vy >= 0:
            for r in level.oneway_rects(self.rect):
                if self.rect.colliderect(r) and prev_bottom <= r.top + 2:
                    self.rect.bottom = r.top
                    self.fy = self.rect.y
                    self.vy = 0
                    self.on_ground = True

        # plataformas moviles: arrastre
        self.riding = None
        for mp in level.movers:
            if mp.solid and self.rect.colliderect(mp.rect.inflate(0, 4)) and \
                    self.rect.bottom <= mp.rect.top + 6 and self.vy >= 0:
                self.rect.bottom = mp.rect.top
                self.fy = self.rect.y
                self.vy = 0
                self.on_ground = True
                self.riding = mp
                self.fx += mp.vx * dt
                self.fy += mp.vy * dt
                self.sync()

        if self.on_ground:
            self.coyote = S.COYOTE_TIME
            self.jumps = S.MAX_JUMPS - 1
            self.air_jumped = False
            if not self.was_on_ground:
                self.land_t = 0.16
        else:
            self.coyote = max(0.0, self.coyote - dt)

        # limites del nivel
        w, h = level.pixel_size
        if self.rect.left < 0:
            self.rect.left = 0
            self.fx = 0
        if self.rect.right > w:
            self.rect.right = w
            self.fx = self.rect.x
        if self.rect.top > h + 40:
            self.take_damage(None, 1)
            if not self.dead:
                self.game.respawn_player()

    def _animate(self, dt, forced=None):
        self.anim_t += dt
        if forced:
            self.state = forced
        elif self.hurt_t > 0:
            self.state = "hurt"
        elif self.attack_t > 0:
            self.state = "throw" if self.state == "throw" else "attack"
        elif self.crouching:
            self.state = "crouch"
        elif not self.on_ground:
            self.state = "jump" if self.vy < 0 else "fall"
        elif self.land_t > 0:
            self.state = "land"
        elif abs(self.vx) > S.WALK_SPEED + 5:
            self.state = "run"
        elif abs(self.vx) > 6:
            self.state = "walk"
        else:
            self.state = "idle"

    def current_image(self):
        frames = self.frames.get(self.state, self.frames["idle"])
        rates = {"idle": 3.5, "walk": 9.0, "run": 13.0, "fall": 6.0,
                 "attack": 12.0, "throw": 12.0, "crouch": 3.0, "celebrate": 5.0}
        rate = rates.get(self.state, 6.0)
        img = frames[int(self.anim_t * rate) % len(frames)]
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        return img

    def draw(self, surf, camera):
        if self.invuln > 0 and int(self.invuln * 20) % 2 == 0:
            return
        img = self.current_image()
        x = self.rect.centerx - img.get_width() // 2
        y = self.rect.bottom - img.get_height() + 1
        surf.blit(img, camera.to_screen(x, y))
