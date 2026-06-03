# overworld.py — Escena de exploración top-down
import pygame
import random
from settings import *
from player import Player
from npc import NPC
from dialogue import DialogueBox
from map_data import GAME_MAP, MAP_WIDTH, MAP_HEIGHT, NPC_DATA
from map_data import TILE_COLORS, WALKABLE, PLAYER_START


class Overworld:
    """Maneja la exploración del mundo."""

    def __init__(self, player_data, sound_manager):
        self.player_data = player_data
        self.sound = sound_manager
        self.player = Player(PLAYER_START[0], PLAYER_START[1])
        self.npcs = [NPC(d[0], d[1], d[2], d[3]) for d in NPC_DATA]
        self.dialogue = DialogueBox(sound_manager)
        self.in_dialogue = False
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.encounter_cooldown = 0.0
        self.font = pygame.font.SysFont("Consolas", 16)
        self.font_big = pygame.font.SysFont("Consolas", 20)
        self.grass_anim = 0.0
        # Pre-render tiles
        self._build_tile_surfaces()

    def _build_tile_surfaces(self):
        """Crea superficies para cada tipo de tile."""
        self.tile_surfaces = {}
        for tile_id, color in TILE_COLORS.items():
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill(color)
            if tile_id == 2:  # Pared - textura
                for i in range(0, TILE_SIZE, 8):
                    pygame.draw.line(surf, (color[0]+15, color[1]+10, color[2]+15),
                                     (0, i), (TILE_SIZE, i), 1)
                pygame.draw.rect(surf, (color[0]-10, color[1]-10, color[2]-10),
                                 (0, 0, TILE_SIZE, TILE_SIZE), 1)
            elif tile_id == 3:  # Hierba
                for _ in range(6):
                    gx = random.randint(2, TILE_SIZE - 4)
                    gy = random.randint(2, TILE_SIZE - 8)
                    pygame.draw.line(surf, (40, 100, 40), (gx, gy + 8), (gx, gy), 2)
            elif tile_id == 4:  # Camino
                pygame.draw.rect(surf, (color[0]-8, color[1]-8, color[2]-8),
                                 (0, 0, TILE_SIZE, TILE_SIZE), 1)
            elif tile_id == 5:  # Save point
                pygame.draw.rect(surf, (50, 40, 65), (0, 0, TILE_SIZE, TILE_SIZE))
                # Estrella
                cx, cy = TILE_SIZE // 2, TILE_SIZE // 2
                pts = []
                import math
                for i in range(5):
                    a = math.radians(i * 72 - 90)
                    pts.append((cx + int(10 * math.cos(a)), cy + int(10 * math.sin(a))))
                    a2 = math.radians(i * 72 - 90 + 36)
                    pts.append((cx + int(4 * math.cos(a2)), cy + int(4 * math.sin(a2))))
                pygame.draw.polygon(surf, YELLOW, pts)
            elif tile_id == 6:  # Boss
                pygame.draw.rect(surf, (50, 40, 65), (0, 0, TILE_SIZE, TILE_SIZE))
                # Calavera simple
                pygame.draw.circle(surf, (150, 50, 50), (16, 14), 8)
                pygame.draw.rect(surf, (150, 50, 50), (12, 18, 8, 6))
                pygame.draw.rect(surf, (50, 40, 65), (13, 11, 3, 3))
                pygame.draw.rect(surf, (50, 40, 65), (18, 11, 3, 3))
            self.tile_surfaces[tile_id] = surf

    def is_walkable(self, tx, ty):
        """Verifica si una posición de tile es transitable."""
        if tx < 0 or tx >= MAP_WIDTH or ty < 0 or ty >= MAP_HEIGHT:
            return False
        tile = GAME_MAP[ty][tx]
        if tile not in WALKABLE:
            return False
        # Verificar que no haya NPC
        for npc in self.npcs:
            if npc.tile_x == tx and npc.tile_y == ty:
                return False
        return True

    def handle_event(self, event):
        if self.in_dialogue:
            if self.dialogue.handle_event(event):
                self.in_dialogue = False
            return None

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_z, pygame.K_RETURN):
            # Intentar hablar con NPC adyacente
            npc = self._get_facing_npc()
            if npc:
                self.dialogue.start(npc.dialogues)
                self.in_dialogue = True
                self.sound.play("select")
                return None

            # Save point
            tile = GAME_MAP[self.player.tile_y][self.player.tile_x]
            if tile == 5:
                self.player_data["hp"] = self.player_data["max_hp"]
                self.dialogue.start([
                    "* El brillo de la estrella te llena de DETERMINACIÓN.",
                    f"* HP completamente restaurado. ({self.player_data['max_hp']}/{self.player_data['max_hp']})"
                ])
                self.in_dialogue = True
                self.sound.play("save")
                return None

        return None

    def _get_facing_npc(self):
        """Retorna el NPC al que el jugador mira, si existe."""
        dx, dy = 0, 0
        if self.player.direction == "up":
            dy = -1
        elif self.player.direction == "down":
            dy = 1
        elif self.player.direction == "left":
            dx = -1
        elif self.player.direction == "right":
            dx = 1

        face_x = self.player.tile_x + dx
        face_y = self.player.tile_y + dy
        for npc in self.npcs:
            if npc.tile_x == face_x and npc.tile_y == face_y:
                return npc
        return None

    def update(self, dt):
        """Retorna nombre de enemigo si hay encuentro, None si no."""
        if self.in_dialogue:
            self.dialogue.update(dt)
            return None

        self.grass_anim += dt

        # Input del jugador
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self.is_walkable)
        self.player.update(dt)

        # Cámara sigue al jugador
        target_cx = self.player.x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        target_cy = self.player.y - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        # Clamp
        max_cx = MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH
        max_cy = MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT
        target_cx = max(0, min(target_cx, max_cx))
        target_cy = max(0, min(target_cy, max_cy))
        # Suavizar
        self.cam_x += (target_cx - self.cam_x) * 5 * dt
        self.cam_y += (target_cy - self.cam_y) * 5 * dt

        # Cooldown de encuentros
        if self.encounter_cooldown > 0:
            self.encounter_cooldown -= dt

        # Verificar encuentro aleatorio en hierba
        if not self.player.moving:
            tile = GAME_MAP[self.player.tile_y][self.player.tile_x]
            if tile == 3 and self.encounter_cooldown <= 0:
                if random.random() < 0.08:  # 8% por paso
                    self.encounter_cooldown = 3.0
                    self.sound.play("encounter")
                    return "random"

            # Boss trigger
            if tile == 6:
                self.encounter_cooldown = 5.0
                self.sound.play("encounter")
                return "boss"

        return None

    def draw(self, surface):
        surface.fill((15, 10, 25))
        cx, cy = int(self.cam_x), int(self.cam_y)

        # Tiles visibles
        start_tx = max(0, cx // TILE_SIZE)
        start_ty = max(0, cy // TILE_SIZE)
        end_tx = min(MAP_WIDTH, start_tx + SCREEN_WIDTH // TILE_SIZE + 2)
        end_ty = min(MAP_HEIGHT, start_ty + SCREEN_HEIGHT // TILE_SIZE + 2)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = GAME_MAP[ty][tx]
                if tile == 0:
                    continue
                surf = self.tile_surfaces.get(tile)
                if surf:
                    sx = tx * TILE_SIZE - cx
                    sy = ty * TILE_SIZE - cy
                    surface.blit(surf, (sx, sy))

        # NPCs
        for npc in self.npcs:
            npc.draw(surface, cx, cy)

        # Jugador
        self.player.draw(surface, cx, cy)

        # Diálogo
        if self.in_dialogue:
            self.dialogue.draw(surface)

        # HUD
        self._draw_hud(surface)

    def _draw_hud(self, surface):
        """Dibuja el HUD del overworld."""
        # Fondo del HUD
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 24)
        hud_surf = pygame.Surface((SCREEN_WIDTH, 24), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 150))
        surface.blit(hud_surf, (0, 0))

        pd = self.player_data
        info = f"♥ HP: {pd['hp']}/{pd['max_hp']}  LV: {pd['lv']}  Oro: {pd['gold']}"
        text = self.font.render(info, True, WHITE)
        surface.blit(text, (8, 4))

        hint = self.font.render("[Z] Interactuar  [Flechas] Mover", True, LIGHT_GRAY)
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 8, 4))
