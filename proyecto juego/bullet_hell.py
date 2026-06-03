# bullet_hell.py — Mecánica de esquivar proyectiles (corazón en caja)
import pygame
import math
import random
from settings import *


class Projectile:
    """Un proyectil individual en la fase bullet-hell."""

    def __init__(self, x, y, vx, vy, size=8, color=WHITE, shape="circle"):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.shape = shape
        self.active = True
        self.age = 0.0

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.size // 2),
            int(self.y - self.size // 2),
            self.size, self.size
        )

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.age += dt

    def draw(self, surface, box_rect):
        if not self.active:
            return
        ix, iy = int(self.x), int(self.y)
        if self.shape == "circle":
            pygame.draw.circle(surface, self.color, (ix, iy), self.size // 2)
        elif self.shape == "bone_h":
            r = pygame.Rect(ix - self.size, iy - 3, self.size * 2, 6)
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.circle(surface, self.color, (r.left, iy), 5)
            pygame.draw.circle(surface, self.color, (r.right, iy), 5)
        elif self.shape == "bone_v":
            r = pygame.Rect(ix - 3, iy - self.size, 6, self.size * 2)
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.circle(surface, self.color, (ix, r.top), 5)
            pygame.draw.circle(surface, self.color, (ix, r.bottom), 5)
        elif self.shape == "diamond":
            s = self.size // 2
            pts = [(ix, iy - s), (ix + s, iy), (ix, iy + s), (ix - s, iy)]
            pygame.draw.polygon(surface, self.color, pts)


# ─── Patrones de ataque ───

def pattern_petal_drift(bh, dt):
    """Pétalos que caen suavemente desde arriba."""
    bh.spawn_timer += dt
    if bh.spawn_timer >= 0.4:
        bh.spawn_timer = 0
        x = random.randint(bh.box.left + 15, bh.box.right - 15)
        vx = random.uniform(-0.5, 0.5)
        vy = random.uniform(1.2, 2.0)
        bh.projectiles.append(
            Projectile(x, bh.box.top + 5, vx, vy, 10, PINK, "circle")
        )


def pattern_seed_rain(bh, dt):
    """Semillas que caen más rápido, en ráfagas."""
    bh.spawn_timer += dt
    if bh.spawn_timer >= 0.25:
        bh.spawn_timer = 0
        for _ in range(2):
            x = random.randint(bh.box.left + 10, bh.box.right - 10)
            vy = random.uniform(1.8, 2.8)
            bh.projectiles.append(
                Projectile(x, bh.box.top + 5, 0, vy, 7, GREEN, "diamond")
            )


def pattern_bone_horizontal(bh, dt):
    """Huesos que cruzan horizontalmente."""
    bh.spawn_timer += dt
    if bh.spawn_timer >= 0.7:
        bh.spawn_timer = 0
        from_left = random.choice([True, False])
        y = random.randint(bh.box.top + 20, bh.box.bottom - 20)
        vx = random.uniform(2.0, 3.0) * (1 if from_left else -1)
        x = bh.box.left - 10 if from_left else bh.box.right + 10
        bh.projectiles.append(
            Projectile(x, y, vx, 0, 16, WHITE, "bone_h")
        )


def pattern_bone_vertical(bh, dt):
    """Huesos que suben desde abajo."""
    bh.spawn_timer += dt
    if bh.spawn_timer >= 0.5:
        bh.spawn_timer = 0
        x = random.randint(bh.box.left + 20, bh.box.right - 20)
        bh.projectiles.append(
            Projectile(x, bh.box.bottom + 10, 0, -2.5, 14, WHITE, "bone_v")
        )


def pattern_ghost_orbs(bh, dt):
    """Orbes fantasmales que aparecen y se mueven en patrones."""
    bh.spawn_timer += dt
    if bh.spawn_timer >= 0.35:
        bh.spawn_timer = 0
        cx, cy = bh.box.center
        angle = random.uniform(0, math.pi * 2)
        dist = max(bh.box.w, bh.box.h) // 2 + 20
        x = cx + math.cos(angle) * dist
        y = cy + math.sin(angle) * dist
        speed = random.uniform(1.5, 2.5)
        vx = -math.cos(angle) * speed
        vy = -math.sin(angle) * speed
        bh.projectiles.append(
            Projectile(x, y, vx, vy, 12, PURPLE, "circle")
        )


def pattern_shadow_wave(bh, dt):
    """Olas de sombras que cruzan de lado a lado."""
    bh.spawn_timer += dt
    if bh.spawn_timer >= 0.3:
        bh.spawn_timer = 0
        # Ola desde la izquierda o derecha
        from_left = bh.timer % 2 < 1
        wave_y = bh.box.top + 10 + int(
            (bh.timer * 40) % (bh.box.h - 20)
        )
        vx = 2.5 if from_left else -2.5
        x = bh.box.left - 5 if from_left else bh.box.right + 5
        bh.projectiles.append(
            Projectile(x, wave_y, vx, 0, 10, CYAN, "diamond")
        )


# Registro de patrones
PATTERNS = {
    "petal_drift": pattern_petal_drift,
    "seed_rain": pattern_seed_rain,
    "bone_horizontal": pattern_bone_horizontal,
    "bone_vertical": pattern_bone_vertical,
    "ghost_orbs": pattern_ghost_orbs,
    "shadow_wave": pattern_shadow_wave,
}


class BulletHell:
    """Controla la fase de esquivar proyectiles."""

    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.box = pygame.Rect(BATTLE_BOX_X, BATTLE_BOX_Y, BATTLE_BOX_W, BATTLE_BOX_H)
        self.heart_x = float(self.box.centerx)
        self.heart_y = float(self.box.centery)
        self.projectiles = []
        self.active = False
        self.timer = 0.0
        self.duration = 5.0
        self.invulnerable = False
        self.inv_timer = 0.0
        self.damage_taken = 0
        self.spawn_timer = 0.0
        self.pattern_name = ""
        self.pattern_func = None
        self.enemy_atk = 5

    def start(self, pattern_name, duration=5.0, enemy_atk=5):
        self.active = True
        self.timer = 0.0
        self.duration = duration
        self.projectiles.clear()
        self.heart_x = float(self.box.centerx)
        self.heart_y = float(self.box.centery)
        self.invulnerable = False
        self.inv_timer = 0.0
        self.damage_taken = 0
        self.spawn_timer = 0.0
        self.pattern_name = pattern_name
        self.pattern_func = PATTERNS.get(pattern_name)
        self.enemy_atk = enemy_atk

    def update(self, dt):
        if not self.active:
            return None

        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
            return self.damage_taken

        # Input
        keys = pygame.key.get_pressed()
        speed = HEART_SPEED
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.heart_x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.heart_x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.heart_y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.heart_y += speed

        # Clamp dentro de la caja
        hs = HEART_SIZE // 2 + 4
        self.heart_x = max(self.box.left + hs, min(self.box.right - hs, self.heart_x))
        self.heart_y = max(self.box.top + hs, min(self.box.bottom - hs, self.heart_y))

        # Spawnar proyectiles
        if self.pattern_func:
            self.pattern_func(self, dt)

        # Actualizar proyectiles
        for p in self.projectiles:
            p.update(dt)
            if not self.box.inflate(60, 60).collidepoint(p.x, p.y):
                p.active = False
        self.projectiles = [p for p in self.projectiles if p.active]

        # Colisiones
        if not self.invulnerable:
            heart_rect = pygame.Rect(
                int(self.heart_x) - HEART_SIZE // 2,
                int(self.heart_y) - HEART_SIZE // 2,
                HEART_SIZE, HEART_SIZE
            )
            for p in self.projectiles:
                if heart_rect.colliderect(p.rect):
                    dmg = max(1, self.enemy_atk - 3)
                    self.damage_taken += dmg
                    self.invulnerable = True
                    self.inv_timer = 0.6
                    self.sound_manager.play("damage")
                    p.active = False
                    break

        if self.invulnerable:
            self.inv_timer -= dt
            if self.inv_timer <= 0:
                self.invulnerable = False

        return None

    def draw(self, surface):
        if not self.active:
            return
        # Fondo de la caja
        inner = self.box.inflate(-6, -6)
        pygame.draw.rect(surface, BLACK, inner)
        pygame.draw.rect(surface, WHITE, self.box, 3)

        # Proyectiles
        for p in self.projectiles:
            p.draw(surface, self.box)

        # Corazón (parpadea cuando invulnerable)
        if not self.invulnerable or int(self.inv_timer * 12) % 2:
            self._draw_heart(surface)

        # Timer visual
        remaining = max(0, self.duration - self.timer)
        bar_w = int((remaining / self.duration) * 80)
        pygame.draw.rect(surface, DARK_GRAY, (self.box.right - 90, self.box.top - 15, 80, 8))
        pygame.draw.rect(surface, CYAN, (self.box.right - 90, self.box.top - 15, bar_w, 8))

    def _draw_heart(self, surface):
        """Dibuja el corazón/alma roja del jugador."""
        x = int(self.heart_x)
        y = int(self.heart_y)
        s = HEART_SIZE // 2
        # Forma de corazón con polígono
        pts = [
            (x, y + s),           # punta inferior
            (x - s, y),           # izquierda
            (x - s + 1, y - s + 2),  # arriba-izq
            (x - 1, y - s // 2 + 1),
            (x, y - s + 3),       # centro arriba
            (x + 1, y - s // 2 + 1),
            (x + s - 1, y - s + 2),  # arriba-der
            (x + s, y),           # derecha
        ]
        pygame.draw.polygon(surface, RED, pts)
        # Brillo
        pygame.draw.circle(surface, (255, 120, 120), (x - 2, y - 2), 2)
