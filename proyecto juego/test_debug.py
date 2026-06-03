import pygame
import sys
import traceback

print("[1] Iniciando pygame...")
pygame.init()
print(f"[2] pygame.init() OK - display: {pygame.display.get_init()}, font: {pygame.font.get_init()}")

print("[3] Creando ventana...")
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("TEST")
print("[4] Ventana creada OK")

print("[5] Probando fill rojo...")
screen.fill((255, 0, 0))
pygame.display.flip()
print("[6] Fill + flip OK")

print("[7] Probando fuente...")
try:
    font = pygame.font.SysFont("Consolas", 48, bold=True)
    print(f"[8] Fuente creada: {font}")
    surf = font.render("HOLA MUNDO", True, (255, 255, 255))
    print(f"[9] Texto renderizado: {surf.get_size()}")
    screen.blit(surf, (100, 200))
    pygame.display.flip()
    print("[10] Texto mostrado OK")
except Exception as e:
    print(f"[ERROR FUENTE] {e}")
    traceback.print_exc()

print("[11] Probando mixer...")
try:
    if pygame.mixer.get_init():
        print(f"[12] Mixer ya inicializado: {pygame.mixer.get_init()}")
    else:
        pygame.mixer.init(22050, -16, 1, 512)
        print("[12] Mixer inicializado OK")
except Exception as e:
    print(f"[ERROR MIXER] {e}")

print("[13] Probando sonido generado...")
try:
    import array, math
    n = int(22050 * 0.05)
    buf = array.array('h', [0] * n)
    for i in range(n):
        buf[i] = int(3000 * math.sin(2 * 3.14159 * 440 * i / 22050))
    snd = pygame.mixer.Sound(buffer=buf)
    print(f"[14] Sonido creado OK: {snd}")
except Exception as e:
    print(f"[ERROR SONIDO] {e}")
    traceback.print_exc()

print("[15] Probando import de módulos del juego...")
try:
    from settings import *
    print("[16] settings OK")
except Exception as e:
    print(f"[ERROR settings] {e}")
    traceback.print_exc()

try:
    from sounds import SoundManager
    sm = SoundManager()
    print("[17] SoundManager OK")
except Exception as e:
    print(f"[ERROR SoundManager] {e}")
    traceback.print_exc()

try:
    from dialogue import DialogueBox
    db = DialogueBox(sm)
    print("[18] DialogueBox OK")
except Exception as e:
    print(f"[ERROR DialogueBox] {e}")
    traceback.print_exc()

try:
    from ui import HPBar, FightBar
    print("[19] UI OK")
except Exception as e:
    print(f"[ERROR UI] {e}")
    traceback.print_exc()

try:
    from enemies import create_florin
    e = create_florin()
    print(f"[20] Enemies OK: {e.name}")
except Exception as e:
    print(f"[ERROR Enemies] {e}")
    traceback.print_exc()

try:
    from bullet_hell import BulletHell
    bh = BulletHell(sm)
    print("[21] BulletHell OK")
except Exception as e:
    print(f"[ERROR BulletHell] {e}")
    traceback.print_exc()

try:
    from battle import Battle
    print("[22] Battle import OK")
except Exception as e:
    print(f"[ERROR Battle] {e}")
    traceback.print_exc()

try:
    from overworld import Overworld
    print("[23] Overworld import OK")
except Exception as e:
    print(f"[ERROR Overworld] {e}")
    traceback.print_exc()

# Test render loop
print("[24] Probando game loop de 3 segundos...")
clock = pygame.time.Clock()
font2 = pygame.font.SysFont("Consolas", 30)
frames = 0
try:
    for _ in range(180):  # 3 seconds at 60fps
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        screen.fill((0, 0, 0))
        txt = font2.render(f"Frame: {frames} - TODO OK!", True, (255, 255, 0))
        screen.blit(txt, (100, 220))
        pygame.display.flip()
        clock.tick(60)
        frames += 1
    print(f"[25] Game loop completado: {frames} frames renderizados")
except Exception as e:
    print(f"[ERROR LOOP] {e}")
    traceback.print_exc()

pygame.quit()
print("[FIN] Test completado sin errores fatales.")
