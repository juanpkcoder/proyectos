# player.py — Jugador del overworld
import pygame
from settings import *


class Player:
    """Jugador que se mueve en el overworld."""

    def __init__(self, tile_x, tile_y):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.x = float(tile_x * TILE_SIZE)
        self.y = float(tile_y * TILE_SIZE)
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False
        self.direction = "down"  # up, down, left, right
        self.speed = 120.0  # pixels per second
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.size = TILE_SIZE - 4

    def handle_input(self, keys, walkable_check):
        """Procesa input y mueve al jugador si es posible."""
        if self.moving:
            return

        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            self.direction = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            self.direction = "right"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            self.direction = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            self.direction = "down"

        if dx != 0 or dy != 0:
            new_tx = self.tile_x + dx
            new_ty = self.tile_y + dy
            if walkable_check(new_tx, new_ty):
                self.tile_x = new_tx
                self.tile_y = new_ty
                self.target_x = float(new_tx * TILE_SIZE)
                self.target_y = float(new_ty * TILE_SIZE)
                self.moving = True

    def update(self, dt):
        if self.moving:
            self.anim_timer += dt
            if self.anim_timer >= 0.15:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4

            # Mover suavemente hacia el target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < 2:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
            else:
                move = self.speed * dt
                if move >= dist:
                    self.x = self.target_x
                    self.y = self.target_y
                    self.moving = False
                else:
                    self.x += (dx / dist) * move
                    self.y += (dy / dist) * move

    def draw(self, surface, cam_x, cam_y):
        """Dibuja al jugador en pantalla."""
        sx = int(self.x - cam_x) + 2
        sy = int(self.y - cam_y) + 2
        s = self.size

        # Cuerpo
        body_color = (0, 80, 220)
        pygame.draw.rect(surface, body_color, (sx + 4, sy + 10, s - 8, s - 14))

        # Cabeza
        head_color = (240, 200, 160)
        pygame.draw.rect(surface, head_color, (sx + 6, sy + 2, s - 12, 12))

        # Ojos según dirección
        if self.direction == "down":
            pygame.draw.rect(surface, BLACK, (sx + 9, sy + 6, 3, 3))
            pygame.draw.rect(surface, BLACK, (sx + 16, sy + 6, 3, 3))
        elif self.direction == "up":
            pygame.draw.rect(surface, BLACK, (sx + 9, sy + 4, 3, 2))
            pygame.draw.rect(surface, BLACK, (sx + 16, sy + 4, 3, 2))
        elif self.direction == "left":
            pygame.draw.rect(surface, BLACK, (sx + 7, sy + 6, 3, 3))
            pygame.draw.rect(surface, BLACK, (sx + 13, sy + 6, 3, 3))
        elif self.direction == "right":
            pygame.draw.rect(surface, BLACK, (sx + 10, sy + 6, 3, 3))
            pygame.draw.rect(surface, BLACK, (sx + 18, sy + 6, 3, 3))

        # Piernas (animación simple)
        leg_color = (30, 30, 80)
        leg_offset = 2 if self.anim_frame % 2 == 0 and self.moving else 0
        pygame.draw.rect(surface, leg_color, (sx + 7, sy + s - 6 + leg_offset, 5, 5))
        pygame.draw.rect(surface, leg_color, (sx + 16, sy + s - 6 - leg_offset, 5, 5))

        # Pelo
        hair_color = (60, 30, 10)
        pygame.draw.rect(surface, hair_color, (sx + 5, sy + 1, s - 10, 5))
