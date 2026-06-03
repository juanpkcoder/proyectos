# sounds.py — Generación de efectos de sonido por código
import pygame
import math
import array


def _generate_tone(frequency, duration_ms, volume=0.3, sample_rate=22050):
    """Genera un tono sinusoidal simple."""
    n = int(sample_rate * duration_ms / 1000)
    buf = array.array('h', [0] * n)
    max_val = int(32767 * volume)
    for i in range(n):
        t = i / sample_rate
        buf[i] = int(max_val * math.sin(2 * math.pi * frequency * t))
    return pygame.mixer.Sound(buffer=buf)


def _generate_noise(duration_ms, volume=0.2, sample_rate=22050):
    """Genera ruido para efecto de daño."""
    import random
    n = int(sample_rate * duration_ms / 1000)
    buf = array.array('h', [0] * n)
    max_val = int(32767 * volume)
    for i in range(n):
        buf[i] = int(max_val * (random.random() * 2 - 1))
        # Decay
        buf[i] = int(buf[i] * (1 - i / n))
    return pygame.mixer.Sound(buffer=buf)


class SoundManager:
    """Administra todos los efectos de sonido del juego."""

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(22050, -16, 1, 512)
        self.sounds = {}
        self._create_sounds()

    def _create_sounds(self):
        self.sounds["text"] = _generate_tone(450, 40, 0.08)
        self.sounds["select"] = _generate_tone(700, 60, 0.15)
        self.sounds["confirm"] = _generate_tone(900, 80, 0.15)
        self.sounds["damage"] = _generate_noise(200, 0.25)
        self.sounds["heal"] = _generate_tone(800, 250, 0.15)
        self.sounds["hit"] = _generate_tone(250, 120, 0.2)
        self.sounds["move"] = _generate_tone(550, 35, 0.1)
        self.sounds["save"] = _generate_tone(600, 400, 0.12)
        self.sounds["encounter"] = _generate_tone(350, 300, 0.2)

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()
