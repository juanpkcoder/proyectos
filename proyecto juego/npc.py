# npc.py — NPCs del overworld
import pygame
import math
from settings import *


class NPC:
    """Un NPC en el overworld con diálogo."""

    def __init__(self, tile_x, tile_y, name, dialogues):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.name = name
        self.dialogues = dialogues
        self.x = tile_x * TILE_SIZE
        self.y = tile_y * TILE_SIZE

    def draw(self, surface, cam_x, cam_y):
        sx = self.x - cam_x + 2
        sy = self.y - cam_y + 2
        s = TILE_SIZE - 4

        # Color según NPC
        if "Anciano" in self.name:
            body_c = (140, 100, 160)
            head_c = (220, 190, 170)
        elif "Mercader" in self.name:
            body_c = (180, 130, 50)
            head_c = (200, 220, 180)
        else:
            body_c = (100, 180, 100)
            head_c = (220, 200, 160)

        # Cuerpo
        pygame.draw.rect(surface, body_c, (sx + 4, sy + 10, s - 8, s - 14))
        # Cabeza
        pygame.draw.rect(surface, head_c, (sx + 6, sy + 2, s - 12, 12))
        # Ojos
        pygame.draw.rect(surface, BLACK, (sx + 9, sy + 6, 3, 3))
        pygame.draw.rect(surface, BLACK, (sx + 16, sy + 6, 3, 3))

        # Indicador de interacción (signo !)
        t = pygame.time.get_ticks() / 600.0
        oy = int(math.sin(t * math.pi) * 2)
        font = pygame.font.SysFont("Consolas", 14, bold=True)
        mark = font.render("!", True, YELLOW)
        surface.blit(mark, (sx + s // 2 - 3, sy - 10 + oy))
