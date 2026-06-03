# dialogue.py — Sistema de diálogos con efecto typewriter
import pygame
import math
from settings import *


class DialogueBox:
    """Caja de diálogo estilo Undertale con texto progresivo."""

    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.messages = []
        self.msg_index = 0
        self.char_index = 0
        self.displayed = ""
        self.active = False
        self.timer = 0.0
        self.char_delay = 0.03
        self.finished_line = False
        self.font = None
        self._init_font()

    def _init_font(self):
        for name in ["Consolas", "Courier New", "Courier", "monospace"]:
            self.font = pygame.font.SysFont(name, 22)
            if self.font:
                break

    def start(self, messages):
        """Inicia una secuencia de mensajes."""
        if isinstance(messages, str):
            messages = [messages]
        self.messages = messages
        self.msg_index = 0
        self.char_index = 0
        self.displayed = ""
        self.active = True
        self.finished_line = False

    def handle_event(self, event):
        """Retorna True cuando el diálogo termina completamente."""
        if not self.active:
            return False
        if event.type != pygame.KEYDOWN:
            return False
        if event.key not in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
            return False

        if self.finished_line:
            self.msg_index += 1
            if self.msg_index >= len(self.messages):
                self.active = False
                return True
            self.char_index = 0
            self.displayed = ""
            self.finished_line = False
        else:
            # Mostrar texto completo de golpe
            self.displayed = self.messages[self.msg_index]
            self.char_index = len(self.displayed)
            self.finished_line = True
        return False

    def update(self, dt):
        if not self.active or self.finished_line:
            return
        self.timer += dt
        if self.timer >= self.char_delay:
            self.timer = 0
            msg = self.messages[self.msg_index]
            if self.char_index < len(msg):
                ch = msg[self.char_index]
                self.displayed += ch
                self.char_index += 1
                if ch not in (' ', '\n', '*'):
                    self.sound_manager.play("text")
            if self.char_index >= len(msg):
                self.finished_line = True

    def draw(self, surface, x=32, y=340, w=576, h=130):
        if not self.active:
            return
        # Caja negra con borde blanco
        pygame.draw.rect(surface, BLACK, (x, y, w, h))
        pygame.draw.rect(surface, WHITE, (x, y, w, h), 3)
        # Texto con word-wrap
        self._draw_wrapped(surface, self.displayed, x + 22, y + 18, w - 44)
        # Indicador de continuar
        if self.finished_line:
            t = pygame.time.get_ticks() / 400.0
            oy = int(math.sin(t * math.pi) * 3)
            cx = x + w - 28
            cy = y + h - 22 + oy
            pts = [(cx, cy), (cx + 10, cy), (cx + 5, cy + 7)]
            pygame.draw.polygon(surface, WHITE, pts)

    def _draw_wrapped(self, surface, text, x, y, max_w):
        lines = text.split('\n')
        row = 0
        for line in lines:
            words = line.split(' ')
            current = ""
            for word in words:
                test = (current + " " + word) if current else word
                if self.font.size(test)[0] <= max_w:
                    current = test
                else:
                    if current:
                        surf = self.font.render(current, True, WHITE)
                        surface.blit(surf, (x, y + row * 26))
                        row += 1
                    current = word
            if current:
                surf = self.font.render(current, True, WHITE)
                surface.blit(surf, (x, y + row * 26))
                row += 1
