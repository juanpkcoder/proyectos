# battle.py — Sistema de combate por turnos estilo Undertale
import pygame
import random
import math
from settings import *
from ui import HPBar, FightBar, draw_battle_menu, draw_sub_menu
from dialogue import DialogueBox
from bullet_hell import BulletHell


class Battle:
    """Maneja toda la lógica y renderizado de un combate."""

    def __init__(self, enemy, player_data, sound_manager):
        self.enemy = enemy
        self.enemy.reset()
        self.player = player_data
        self.sound = sound_manager
        self.state = BATTLE_INTRO
        self.menu_options = ["LUCHAR", "ACTUAR", "OBJETO", "PIEDAD"]
        self.selected = 0
        self.sub_selected = 0

        # Componentes
        self.font = pygame.font.SysFont("Consolas", 20)
        self.font_big = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 16)
        self.dialogue = DialogueBox(sound_manager)
        self.bullet_hell = BulletHell(sound_manager)
        self.fight_bar = FightBar(
            BATTLE_BOX_X + 40, BATTLE_BOX_Y + 50,
            BATTLE_BOX_W - 80, 30
        )
        self.hp_bar = HPBar(340, 448, 120, 16, self.player["max_hp"])
        self.hp_bar.set_hp(self.player["hp"])
        self.enemy_hp_bar = HPBar(270, 200, 100, 10, self.enemy.max_hp)

        # Estado interno
        self.turn_count = 0
        self.result = None  # "VICTORY", "DEFEAT", "SPARE"
        self.pending_texts = []
        self.after_text_state = None
        self.shake_timer = 0.0
        self.flash_timer = 0.0
        self.victory_timer = 0.0
        self.defeat_timer = 0.0

        # Iniciar intro
        self.dialogue.start([self.enemy.intro_text])

    def handle_event(self, event):
        if self.state == BATTLE_INTRO:
            if self.dialogue.handle_event(event):
                self._to_menu()

        elif self.state == BATTLE_TEXT:
            if self.dialogue.handle_event(event):
                if self.after_text_state == BATTLE_ENEMY_TURN:
                    self._start_enemy_turn()
                elif self.after_text_state == BATTLE_VICTORY:
                    self.state = BATTLE_VICTORY
                elif self.after_text_state == BATTLE_DEFEAT:
                    self.state = BATTLE_DEFEAT
                elif self.after_text_state == BATTLE_MENU:
                    self._to_menu()
                else:
                    self._to_menu()

        elif self.state == BATTLE_MENU:
            self._handle_menu(event)

        elif self.state == BATTLE_FIGHT:
            self.fight_bar.handle_event(event)

        elif self.state == BATTLE_ACT_MENU:
            self._handle_sub_menu(event, self.enemy.act_options)

        elif self.state == BATTLE_ITEM_MENU:
            items = [f"{it['name']} (x{it['qty']})" for it in self.player["items"]]
            if not items:
                items = ["(vacío)"]
            self._handle_sub_menu_item(event, items)

        elif self.state == BATTLE_MERCY_MENU:
            self._handle_mercy(event)

    def _handle_menu(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.selected = (self.selected - 1) % 4
            self.sound.play("move")
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.selected = (self.selected + 1) % 4
            self.sound.play("move")
        elif event.key in (pygame.K_z, pygame.K_RETURN):
            self.sound.play("confirm")
            if self.selected == 0:  # LUCHAR
                self.state = BATTLE_FIGHT
                self.fight_bar.start()
            elif self.selected == 1:  # ACTUAR
                self.state = BATTLE_ACT_MENU
                self.sub_selected = 0
            elif self.selected == 2:  # OBJETO
                self.state = BATTLE_ITEM_MENU
                self.sub_selected = 0
            elif self.selected == 3:  # PIEDAD
                self.state = BATTLE_MERCY_MENU
                self.sub_selected = 0

    def _handle_sub_menu(self, event, options):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.sub_selected = (self.sub_selected - 1) % len(options)
            self.sound.play("move")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.sub_selected = (self.sub_selected + 1) % len(options)
            self.sound.play("move")
        elif event.key in (pygame.K_x, pygame.K_ESCAPE):
            self._to_menu()
            self.sound.play("select")
        elif event.key in (pygame.K_z, pygame.K_RETURN):
            self.sound.play("confirm")
            opt = options[self.sub_selected]
            text = self.enemy.act_texts.get(opt, f"* Hiciste {opt}.")
            self.enemy.mercy_count += 1
            self.enemy.check_mercy()
            self._show_text([text], BATTLE_ENEMY_TURN)

    def _handle_sub_menu_item(self, event, items):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.sub_selected = (self.sub_selected - 1) % max(1, len(items))
            self.sound.play("move")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.sub_selected = (self.sub_selected + 1) % max(1, len(items))
            self.sound.play("move")
        elif event.key in (pygame.K_x, pygame.K_ESCAPE):
            self._to_menu()
            self.sound.play("select")
        elif event.key in (pygame.K_z, pygame.K_RETURN):
            if not self.player["items"]:
                self._show_text(["* No tienes objetos."], BATTLE_MENU)
                return
            item = self.player["items"][self.sub_selected]
            if item["qty"] <= 0:
                return
            item["qty"] -= 1
            heal = item.get("heal", 0)
            if heal > 0:
                self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + heal)
                self.hp_bar.set_hp(self.player["hp"])
                self.sound.play("heal")
                text = f"* Usaste {item['name']}.\n* ¡Recuperaste {heal} HP!"
            else:
                text = f"* Usaste {item['name']}."
            if item["qty"] <= 0:
                self.player["items"].remove(item)
            self._show_text([text], BATTLE_ENEMY_TURN)

    def _handle_mercy(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_x, pygame.K_ESCAPE):
            self._to_menu()
            self.sound.play("select")
        elif event.key in (pygame.K_z, pygame.K_RETURN):
            self.sound.play("confirm")
            if self.enemy.spareable:
                self._show_text(
                    [f"* ¡Perdonaste a {self.enemy.name}!",
                     f"* Ganaste {self.enemy.gold_reward} monedas de oro."],
                    BATTLE_VICTORY
                )
                self.player["gold"] += self.enemy.gold_reward
                self.result = "SPARE"
            else:
                self._show_text(
                    [f"* {self.enemy.name} no quiere ser perdonado todavía..."],
                    BATTLE_ENEMY_TURN
                )

    def _to_menu(self):
        self.state = BATTLE_MENU
        self.selected = 0
        # Mostrar flavor text del enemigo
        flavor = self.enemy.get_flavor()
        self.dialogue.start([flavor])

    def _show_text(self, texts, next_state):
        self.state = BATTLE_TEXT
        self.dialogue.start(texts)
        self.after_text_state = next_state

    def _start_enemy_turn(self):
        self.state = BATTLE_ENEMY_TURN
        self.turn_count += 1
        pattern_idx = (self.turn_count - 1) % len(self.enemy.attack_patterns)
        pattern = self.enemy.attack_patterns[pattern_idx]
        duration = 4.0 + min(self.turn_count * 0.3, 2.0)
        self.bullet_hell.start(pattern, duration, self.enemy.atk)

    def _apply_fight_damage(self):
        mult = self.fight_bar.result if self.fight_bar.result else 0.3
        base_dmg = max(1, self.player["atk"] - self.enemy.defense)
        dmg = max(1, int(base_dmg * mult))
        self.enemy.hp -= dmg
        self.enemy_hp_bar.set_hp(self.enemy.hp)
        self.shake_timer = 0.4
        self.sound.play("hit")

        if self.enemy.hp <= 0:
            self.enemy.hp = 0
            self.player["exp"] += self.enemy.exp_reward
            self.player["gold"] += self.enemy.gold_reward
            self.result = "VICTORY"
            self._show_text(
                [f"* ¡Derrotaste a {self.enemy.name}!",
                 f"* Ganaste {self.enemy.exp_reward} EXP y {self.enemy.gold_reward} oro."],
                BATTLE_VICTORY
            )
        else:
            self._show_text(
                [f"* ¡Hiciste {dmg} de daño a {self.enemy.name}!"],
                BATTLE_ENEMY_TURN
            )

    def update(self, dt):
        self.dialogue.update(dt)
        self.hp_bar.update(dt)
        self.enemy_hp_bar.update(dt)

        if self.shake_timer > 0:
            self.shake_timer -= dt

        if self.state == BATTLE_FIGHT:
            self.fight_bar.update(dt)
            if self.fight_bar.result is not None and not self.fight_bar.active:
                self._apply_fight_damage()
                self.fight_bar.result = None

        elif self.state == BATTLE_ENEMY_TURN:
            result = self.bullet_hell.update(dt)
            if result is not None:
                dmg = result
                if dmg > 0:
                    self.player["hp"] -= dmg
                    self.hp_bar.set_hp(self.player["hp"])
                if self.player["hp"] <= 0:
                    self.player["hp"] = 0
                    self.hp_bar.set_hp(0)
                    self.result = "DEFEAT"
                    self._show_text(
                        ["* No puedes seguir luchando..."],
                        BATTLE_DEFEAT
                    )
                else:
                    self._to_menu()

        elif self.state == BATTLE_VICTORY:
            self.victory_timer += dt
            if self.victory_timer > 2.0:
                return self.result or "VICTORY"

        elif self.state == BATTLE_DEFEAT:
            self.defeat_timer += dt
            if self.defeat_timer > 2.0:
                return "DEFEAT"

        return None

    def draw(self, surface):
        surface.fill(BLACK)
        self._draw_enemy(surface)
        self._draw_bottom_ui(surface)

        if self.state == BATTLE_FIGHT and self.fight_bar.active:
            self.fight_bar.draw(surface)
        elif self.state == BATTLE_ENEMY_TURN and self.bullet_hell.active:
            self.bullet_hell.draw(surface)
        elif self.state in (BATTLE_ACT_MENU, BATTLE_ITEM_MENU, BATTLE_MERCY_MENU):
            self._draw_sub_menu(surface)
        elif self.state == BATTLE_MENU:
            self.dialogue.draw(surface, BATTLE_BOX_X, BATTLE_BOX_Y, BATTLE_BOX_W, BATTLE_BOX_H)
        elif self.state in (BATTLE_INTRO, BATTLE_TEXT):
            self.dialogue.draw(surface, BATTLE_BOX_X, BATTLE_BOX_Y, BATTLE_BOX_W, BATTLE_BOX_H)

        if self.state == BATTLE_VICTORY:
            self._draw_victory(surface)
        elif self.state == BATTLE_DEFEAT:
            self._draw_defeat(surface)

    def _draw_enemy(self, surface):
        """Dibuja el sprite del enemigo."""
        cx, cy = SCREEN_WIDTH // 2, 120
        # Shake
        sx = 0
        if self.shake_timer > 0:
            sx = int(math.sin(self.shake_timer * 40) * 5)
        color = self.enemy.sprite_color
        name = self.enemy.name

        if "Florín" in name:
            self._draw_flower(surface, cx + sx, cy, color)
        elif "Huesitos" in name:
            self._draw_skeleton(surface, cx + sx, cy, color)
        elif "Sombra" in name:
            self._draw_ghost(surface, cx + sx, cy, color)
        else:
            pygame.draw.rect(surface, color, (cx - 25 + sx, cy - 35, 50, 70))

        # Nombre y HP
        name_surf = self.font.render(self.enemy.name, True, WHITE)
        surface.blit(name_surf, (cx - name_surf.get_width() // 2, 185))
        self.enemy_hp_bar.draw(surface)

    def _draw_flower(self, surface, cx, cy, color):
        """Dibuja una flor estilizada."""
        # Tallo
        pygame.draw.rect(surface, (40, 160, 40), (cx - 3, cy, 6, 50))
        # Hojas
        pygame.draw.ellipse(surface, (40, 180, 40), (cx - 18, cy + 20, 16, 10))
        pygame.draw.ellipse(surface, (40, 180, 40), (cx + 2, cy + 30, 16, 10))
        # Pétalos
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            px = cx + int(math.cos(rad) * 20)
            py = cy - 15 + int(math.sin(rad) * 20)
            pygame.draw.circle(surface, YELLOW, (px, py), 10)
        # Centro
        pygame.draw.circle(surface, color, (cx, cy - 15), 12)
        # Ojos
        pygame.draw.circle(surface, BLACK, (cx - 4, cy - 18), 3)
        pygame.draw.circle(surface, BLACK, (cx + 4, cy - 18), 3)
        # Sonrisa
        pygame.draw.arc(surface, BLACK, (cx - 6, cy - 16, 12, 8), 3.14, 6.28, 2)

    def _draw_skeleton(self, surface, cx, cy, color):
        """Dibuja un esqueleto estilizado."""
        # Cabeza
        pygame.draw.circle(surface, color, (cx, cy - 25), 18)
        # Ojos
        pygame.draw.circle(surface, BLACK, (cx - 6, cy - 28), 5)
        pygame.draw.circle(surface, BLACK, (cx + 6, cy - 28), 5)
        pygame.draw.circle(surface, WHITE, (cx - 6, cy - 29), 2)
        pygame.draw.circle(surface, WHITE, (cx + 6, cy - 29), 2)
        # Sonrisa
        pygame.draw.rect(surface, BLACK, (cx - 10, cy - 18, 20, 4))
        for i in range(5):
            x = cx - 8 + i * 4
            pygame.draw.rect(surface, color, (x, cy - 18, 2, 4))
        # Cuerpo
        pygame.draw.rect(surface, color, (cx - 3, cy - 7, 6, 35))
        # Costillas
        for i in range(3):
            y = cy + i * 8
            pygame.draw.rect(surface, color, (cx - 14, y, 28, 3))
        # Brazos
        pygame.draw.line(surface, color, (cx - 3, cy), (cx - 22, cy + 15), 3)
        pygame.draw.line(surface, color, (cx + 3, cy), (cx + 22, cy + 15), 3)

    def _draw_ghost(self, surface, cx, cy, color):
        """Dibuja un fantasma estilizado."""
        t = pygame.time.get_ticks() / 1000.0
        oy = int(math.sin(t * 2) * 5)
        # Cuerpo (semicírculo + ondas)
        pygame.draw.circle(surface, color, (cx, cy - 10 + oy), 25)
        pygame.draw.rect(surface, color, (cx - 25, cy - 10 + oy, 50, 30))
        # Ondas inferiores
        for i in range(5):
            x = cx - 20 + i * 10
            wave = int(math.sin(t * 3 + i) * 3)
            pygame.draw.circle(surface, color, (x, cy + 20 + oy + wave), 6)
        # Ojos
        pygame.draw.circle(surface, WHITE, (cx - 8, cy - 15 + oy), 6)
        pygame.draw.circle(surface, WHITE, (cx + 8, cy - 15 + oy), 6)
        pygame.draw.circle(surface, BLACK, (cx - 8, cy - 14 + oy), 3)
        pygame.draw.circle(surface, BLACK, (cx + 8, cy - 14 + oy), 3)
        # Aura
        alpha_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        alpha = int(80 + math.sin(t * 4) * 40)
        pygame.draw.circle(alpha_surf, (*color, alpha), (40, 40), 38)
        surface.blit(alpha_surf, (cx - 40, cy - 30 + oy))

    def _draw_bottom_ui(self, surface):
        """Dibuja la interfaz inferior (menú, HP, etc.)."""
        # Separador
        pygame.draw.line(surface, WHITE, (0, 430), (SCREEN_WIDTH, 430), 2)

        # Info del jugador
        name_s = self.font.render(self.player["name"], True, WHITE)
        surface.blit(name_s, (32, 440))
        lv_s = self.font_small.render(f"LV {self.player['lv']}", True, WHITE)
        surface.blit(lv_s, (32, 460))

        # HP label
        hp_label = self.font_small.render("HP", True, WHITE)
        surface.blit(hp_label, (310, 450))
        self.hp_bar.draw(surface)

        # Menú principal
        if self.state == BATTLE_MENU:
            draw_battle_menu(
                surface, self.menu_options, self.selected,
                50, 405, self.font
            )

    def _draw_sub_menu(self, surface):
        """Dibuja submenú dentro de la caja de batalla."""
        # Caja
        box = pygame.Rect(BATTLE_BOX_X, BATTLE_BOX_Y, BATTLE_BOX_W, BATTLE_BOX_H)
        pygame.draw.rect(surface, BLACK, box)
        pygame.draw.rect(surface, WHITE, box, 3)

        if self.state == BATTLE_ACT_MENU:
            options = self.enemy.act_options
        elif self.state == BATTLE_ITEM_MENU:
            options = [f"{it['name']} (x{it['qty']})" for it in self.player["items"]]
            if not options:
                options = ["(vacío)"]
        elif self.state == BATTLE_MERCY_MENU:
            spare_color = YELLOW if self.enemy.spareable else WHITE
            spare_text = f"Perdonar{' ★' if self.enemy.spareable else ''}"
            options = [spare_text]
        else:
            options = []

        draw_sub_menu(
            surface, options, self.sub_selected,
            BATTLE_BOX_X + 40, BATTLE_BOX_Y + 20, self.font
        )

        # Instrucción
        hint = self.font_small.render("[Z] Aceptar  [X] Volver", True, LIGHT_GRAY)
        surface.blit(hint, (BATTLE_BOX_X + 40, BATTLE_BOX_Y + BATTLE_BOX_H - 25))

    def _draw_victory(self, surface):
        alpha = min(255, int(self.victory_timer * 200))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(alpha, 180)))
        surface.blit(overlay, (0, 0))
        txt = self.font_big.render("¡VICTORIA!", True, YELLOW)
        surface.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 200))

    def _draw_defeat(self, surface):
        alpha = min(255, int(self.defeat_timer * 200))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((80, 0, 0, min(alpha, 200)))
        surface.blit(overlay, (0, 0))
        txt = self.font_big.render("GAME OVER", True, RED)
        surface.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 200))
