# main.py — Punto de entrada del juego estilo Undertale
import pygame
import sys
import math
import random
from settings import *
from sounds import SoundManager
from overworld import Overworld
from battle import Battle
from enemies import create_florin, create_huesitos, create_sombra


class Game:
    """Clase principal del juego."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Subsuelo — Un juego estilo Undertale")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.sound = SoundManager()

        # Datos del jugador (compartidos entre overworld y batalla)
        self.player_data = {
            "name": "Humano",
            "hp": PLAYER_MAX_HP,
            "max_hp": PLAYER_MAX_HP,
            "atk": PLAYER_ATK,
            "def": PLAYER_DEF,
            "lv": 1,
            "exp": 0,
            "gold": 0,
            "items": [
                {"name": "Pastel", "heal": 15, "qty": 1},
                {"name": "Galleta", "heal": 8, "qty": 3},
            ],
        }

        # Estado
        self.state = STATE_TITLE
        self.overworld = None
        self.battle = None
        self.title_timer = 0.0
        self.title_selected = 0
        self.transition_alpha = 0.0
        self.transition_phase = None  # None, "fade_in", "fade_out"
        self.transition_callback = None
        self.boss_defeated = False

        # Fuentes
        self.font_title = pygame.font.SysFont("Consolas", 48, bold=True)
        self.font_sub = pygame.font.SysFont("Consolas", 20)
        self.font_menu = pygame.font.SysFont("Consolas", 24)
        self.font_small = pygame.font.SysFont("Consolas", 16)

    def run(self):
        """Game loop principal."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap para evitar saltos

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                    running = False
                else:
                    self._handle_event(event)

            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_event(self, event):
        if self.transition_phase is not None:
            return

        if self.state == STATE_TITLE:
            self._handle_title(event)
        elif self.state == STATE_OVERWORLD:
            result = self.overworld.handle_event(event)
        elif self.state == STATE_BATTLE:
            self.battle.handle_event(event)
        elif self.state == STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    self._restart()
        elif self.state == STATE_VICTORY_SCREEN:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    self._restart()

    def _handle_title(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.title_selected = (self.title_selected - 1) % 2
            self.sound.play("move")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.title_selected = (self.title_selected + 1) % 2
            self.sound.play("move")
        elif event.key in (pygame.K_z, pygame.K_RETURN):
            self.sound.play("confirm")
            if self.title_selected == 0:
                self._start_transition(self._start_game)
            else:
                pygame.quit()
                sys.exit()

    def _update(self, dt):
        self.title_timer += dt

        # Sistema de transiciones (fade in → callback → fade out)
        if self.transition_phase == "fade_in":
            self.transition_alpha += 500 * dt
            if self.transition_alpha >= 255:
                self.transition_alpha = 255.0
                # Ejecutar callback y pasar a fade_out
                if self.transition_callback:
                    self.transition_callback()
                    self.transition_callback = None
                self.transition_phase = "fade_out"
            return

        if self.transition_phase == "fade_out":
            self.transition_alpha -= 500 * dt
            if self.transition_alpha <= 0:
                self.transition_alpha = 0.0
                self.transition_phase = None
            return

        if self.state == STATE_OVERWORLD:
            result = self.overworld.update(dt)
            if result == "random":
                self._start_random_battle()
            elif result == "boss":
                self._start_boss_battle()

        elif self.state == STATE_BATTLE:
            result = self.battle.update(dt)
            if result == "VICTORY" or result == "SPARE":
                self._start_transition(self._end_battle_victory)
            elif result == "DEFEAT":
                self._start_transition(self._end_battle_defeat)

    def _draw(self):
        if self.state == STATE_TITLE:
            self._draw_title()
        elif self.state == STATE_OVERWORLD:
            self.overworld.draw(self.screen)
        elif self.state == STATE_BATTLE:
            self.battle.draw(self.screen)
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over()
        elif self.state == STATE_VICTORY_SCREEN:
            self._draw_victory_screen()

        # Overlay de transición
        if self.transition_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(int(self.transition_alpha))
            self.screen.blit(overlay, (0, 0))

    # ─── Pantalla de título ───

    def _draw_title(self):
        self.screen.fill(BLACK)
        t = self.title_timer

        # Título con efecto
        title_text = "SUBSUELO"
        title_surf = self.font_title.render(title_text, True, WHITE)
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        ty = 100 + int(math.sin(t * 1.5) * 5)
        self.screen.blit(title_surf, (tx, ty))

        # Subtítulo
        sub = self.font_small.render("Un juego estilo Undertale", True, LIGHT_GRAY)
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 160))

        # Decoración - corazón
        hx, hy = SCREEN_WIDTH // 2, 210
        self._draw_big_heart(hx, hy, t)

        # Menú
        options = ["Comenzar", "Salir"]
        for i, opt in enumerate(options):
            color = YELLOW if i == self.title_selected else WHITE
            text = self.font_menu.render(opt, True, color)
            ox = SCREEN_WIDTH // 2 - text.get_width() // 2
            oy = 290 + i * 40
            if i == self.title_selected:
                # Corazón selector
                pts = [
                    (ox - 25, oy + 12),
                    (ox - 15, oy + 2),
                    (ox - 12, oy + 5),
                    (ox - 10, oy + 2),
                    (ox - 5, oy + 12),
                    (ox - 15, oy + 20),
                ]
                pygame.draw.polygon(self.screen, RED, pts)
            self.screen.blit(text, (ox, oy))

        # Créditos
        credit = self.font_small.render("Hecho con Python + Pygame", True, DARK_GRAY)
        self.screen.blit(credit, (SCREEN_WIDTH // 2 - credit.get_width() // 2, 440))

    def _draw_big_heart(self, cx, cy, t):
        """Dibuja un corazón grande decorativo en el título."""
        pulse = 1.0 + math.sin(t * 3) * 0.05
        s = int(25 * pulse)
        pts = [
            (cx, cy + s + 5),
            (cx - s - 5, cy - 2),
            (cx - s, cy - s + 2),
            (cx - s // 2, cy - s - 2),
            (cx, cy - s // 2),
            (cx + s // 2, cy - s - 2),
            (cx + s, cy - s + 2),
            (cx + s + 5, cy - 2),
        ]
        pygame.draw.polygon(self.screen, RED, pts)
        # Brillo
        pygame.draw.circle(self.screen, (255, 120, 120), (cx - 5, cy - 8), 4)

    # ─── Transiciones y estados ───

    def _start_transition(self, callback):
        self.transition_phase = "fade_in"
        self.transition_alpha = 0.0
        self.transition_callback = callback

    def _start_game(self):
        self.overworld = Overworld(self.player_data, self.sound)
        self.state = STATE_OVERWORLD

    def _start_random_battle(self):
        enemy_creators = [create_florin, create_huesitos]
        enemy = random.choice(enemy_creators)()
        self.battle = Battle(enemy, self.player_data, self.sound)
        self.state = STATE_BATTLE

    def _start_boss_battle(self):
        if self.boss_defeated:
            return
        enemy = create_sombra()
        self.battle = Battle(enemy, self.player_data, self.sound)
        self.state = STATE_BATTLE

    def _end_battle_victory(self):
        if self.battle and self.battle.enemy.name == "Sombra":
            self.boss_defeated = True
            self.state = STATE_VICTORY_SCREEN
        else:
            # Subir de nivel si es necesario
            self._check_level_up()
            self.state = STATE_OVERWORLD
            self.overworld.encounter_cooldown = 3.0

    def _end_battle_defeat(self):
        self.state = STATE_GAME_OVER

    def _check_level_up(self):
        pd = self.player_data
        thresholds = [0, 10, 30, 70, 120, 200]
        new_lv = 1
        for i, th in enumerate(thresholds):
            if pd["exp"] >= th:
                new_lv = i + 1
        if new_lv > pd["lv"]:
            pd["lv"] = new_lv
            pd["max_hp"] = PLAYER_MAX_HP + (new_lv - 1) * 4
            pd["atk"] = PLAYER_ATK + (new_lv - 1) * 2
            pd["def"] = PLAYER_DEF + (new_lv - 1) * 1
            pd["hp"] = pd["max_hp"]

    def _restart(self):
        self.player_data["hp"] = PLAYER_MAX_HP
        self.player_data["max_hp"] = PLAYER_MAX_HP
        self.player_data["atk"] = PLAYER_ATK
        self.player_data["def"] = PLAYER_DEF
        self.player_data["lv"] = 1
        self.player_data["exp"] = 0
        self.player_data["gold"] = 0
        self.player_data["items"] = [
            {"name": "Pastel", "heal": 15, "qty": 1},
            {"name": "Galleta", "heal": 8, "qty": 3},
        ]
        self.boss_defeated = False
        self.state = STATE_TITLE
        self.title_selected = 0

    # ─── Pantallas finales ───

    def _draw_game_over(self):
        self.screen.fill(BLACK)
        t = self.title_timer

        # Texto GAME OVER con efecto
        go = self.font_title.render("GAME OVER", True, RED)
        gx = SCREEN_WIDTH // 2 - go.get_width() // 2
        gy = 150 + int(math.sin(t * 2) * 3)
        self.screen.blit(go, (gx, gy))

        # Corazón roto
        cx, cy = SCREEN_WIDTH // 2, 260
        # Mitad izquierda
        left_pts = [
            (cx - 3, cy + 20), (cx - 20, cy - 5),
            (cx - 15, cy - 15), (cx - 3, cy - 5),
        ]
        pygame.draw.polygon(self.screen, RED, left_pts)
        # Mitad derecha (desplazada)
        right_pts = [
            (cx + 5, cy + 20), (cx + 22, cy - 5),
            (cx + 17, cy - 15), (cx + 5, cy - 5),
        ]
        pygame.draw.polygon(self.screen, RED, right_pts)

        # Texto continuar
        if int(t * 2) % 2:
            cont = self.font_sub.render("Presiona [Z] para reintentar", True, WHITE)
            self.screen.blit(cont, (SCREEN_WIDTH // 2 - cont.get_width() // 2, 340))

        sub = self.font_small.render("No te rindas. Estás lleno de DETERMINACIÓN.", True, LIGHT_GRAY)
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 400))

    def _draw_victory_screen(self):
        self.screen.fill(BLACK)
        t = self.title_timer

        # Texto victoria
        vic = self.font_title.render("¡VICTORIA!", True, YELLOW)
        vx = SCREEN_WIDTH // 2 - vic.get_width() // 2
        vy = 80 + int(math.sin(t * 1.5) * 4)
        self.screen.blit(vic, (vx, vy))

        # Estrella
        cx, cy = SCREEN_WIDTH // 2, 190
        import math as m
        for i in range(5):
            a = m.radians(i * 72 - 90 + t * 30)
            px = cx + int(25 * m.cos(a))
            py = cy + int(25 * m.sin(a))
            a2 = m.radians(i * 72 - 90 + 36 + t * 30)
            px2 = cx + int(10 * m.cos(a2))
            py2 = cy + int(10 * m.sin(a2))
            pygame.draw.line(self.screen, YELLOW, (cx, cy), (px, py), 3)
            pygame.draw.line(self.screen, YELLOW, (px, py), (px2, py2), 2)

        # Mensaje
        msgs = [
            "Has derrotado a Sombra y encontrado la salida.",
            "La luz del exterior te baña con su calidez.",
            "",
            f"  Nivel: {self.player_data['lv']}",
            f"  EXP: {self.player_data['exp']}",
            f"  Oro: {self.player_data['gold']}",
            "",
            "¡Gracias por jugar!",
        ]
        for i, msg in enumerate(msgs):
            color = WHITE if msg.startswith("  ") else LIGHT_GRAY
            if "Gracias" in msg:
                color = YELLOW
            text = self.font_sub.render(msg, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 240 + i * 25))

        if int(t * 2) % 2:
            cont = self.font_small.render("Presiona [Z] para volver al inicio", True, WHITE)
            self.screen.blit(cont, (SCREEN_WIDTH // 2 - cont.get_width() // 2, 450))


if __name__ == "__main__":
    game = Game()
    game.run()
