# ui.py — Interfaz de usuario: HP bar, menús de batalla, HUD
import pygame
from settings import *


class HPBar:
    """Barra de HP con animación de reducción gradual."""

    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.display_hp = float(max_hp)

    def set_hp(self, hp):
        self.current_hp = max(0, min(hp, self.max_hp))

    def update(self, dt):
        speed = 25
        if self.display_hp > self.current_hp:
            self.display_hp = max(self.current_hp, self.display_hp - speed * dt)
        elif self.display_hp < self.current_hp:
            self.display_hp = min(self.current_hp, self.display_hp + speed * dt)

    def draw(self, surface):
        # Fondo rojo
        pygame.draw.rect(surface, RED, (self.x, self.y, self.w, self.h))
        # HP actual amarillo
        if self.display_hp > 0:
            fill = int(self.w * self.display_hp / self.max_hp)
            color = YELLOW if self.display_hp > self.max_hp * 0.3 else ORANGE
            pygame.draw.rect(surface, color, (self.x, self.y, fill, self.h))
        # Borde
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.w, self.h), 1)


class FightBar:
    """Barra de timing para el ataque LUCHAR."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.marker = 0.0  # 0 a 1
        self.speed = 1.8
        self.direction = 1
        self.active = False
        self.result = None

    def start(self):
        self.marker = 0.0
        self.direction = 1
        self.active = True
        self.result = None

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_z, pygame.K_RETURN):
            dist = abs(self.marker - 0.5) * 2  # 0=centro, 1=borde
            self.result = 1.0 - dist * 0.65
            self.active = False

    def update(self, dt):
        if not self.active:
            return
        self.marker += self.direction * self.speed * dt
        if self.marker >= 1.0:
            self.marker = 1.0
            self.direction = -1
        elif self.marker <= 0.0:
            self.marker = 0.0
            self.direction = 1

    def draw(self, surface):
        if not self.active and self.result is None:
            return
        # Barra de fondo
        pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y, self.w, self.h))
        # Zona central verde
        cw = self.w // 6
        cx = self.x + self.w // 2 - cw // 2
        pygame.draw.rect(surface, (0, 80, 0), (cx, self.y, cw, self.h))
        # Borde
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.w, self.h), 2)
        # Marcador
        if self.active:
            mx = self.x + int(self.marker * self.w)
            pygame.draw.rect(surface, WHITE, (mx - 2, self.y - 4, 5, self.h + 8))


def draw_battle_menu(surface, options, selected, x, y, font):
    """Dibuja el menú de opciones de batalla."""
    spacing = 140
    for i, opt in enumerate(options):
        ox = x + i * spacing
        color = YELLOW if i == selected else WHITE
        # Corazón selector
        if i == selected:
            _draw_mini_heart(surface, ox - 16, y + 6, YELLOW)
        text = font.render(opt, True, color)
        surface.blit(text, (ox, y))


def draw_sub_menu(surface, options, selected, x, y, font):
    """Dibuja un submenú vertical."""
    for i, opt in enumerate(options):
        oy = y + i * 30
        color = YELLOW if i == selected else WHITE
        if i == selected:
            _draw_mini_heart(surface, x - 16, oy + 4, YELLOW)
        text = font.render(opt, True, color)
        surface.blit(text, (x, oy))


def _draw_mini_heart(surface, x, y, color):
    """Dibuja un corazón pequeño como selector."""
    s = 5
    pygame.draw.polygon(surface, color, [
        (x, y + s * 2),
        (x - s, y + s // 2),
        (x - s + 2, y - 2),
        (x, y + s // 2 - 1),
        (x + s - 2, y - 2),
        (x + s, y + s // 2),
    ])
