# Documentación del Proyecto: "Subsuelo" (Juego estilo Undertale)

## 1. Introducción
**"Subsuelo"** es un videojuego de rol (RPG) desarrollado en Python utilizando la librería **Pygame**. El juego está fuertemente inspirado en mecánicas clásicas de juegos como *Undertale*, combinando la exploración de un mundo bidimensional (Overworld) con un sistema de combate por turnos que incluye opciones pacíficas, mini-juegos de esquivar (Bullet Hell) y diálogos interactivos.

El objetivo del jugador es explorar el entorno, interactuar con NPCs, sobrevivir a encuentros con enemigos aleatorios y finalmente derrotar o perdonar al jefe final ("Sombra") para escapar del subsuelo.

---

## 2. Origen de las Imágenes y Recursos Gráficos
Una de las características técnicas más importantes y destacables de este proyecto es el **origen de sus gráficos e imágenes**. 

**NO se han utilizado imágenes descargadas de internet, ni archivos `.png`, `.jpg` o recursos externos.**
Absolutamente **todos los elementos visuales del juego están generados procedimentalmente mediante código matemático y geométrico** usando las funciones de dibujo de la librería `pygame.draw`.

- **Personajes y Enemigos:** El jugador, los NPCs y los enemigos (como la flor *Florín*, el esqueleto *Huesitos* y el fantasma *Sombra*) están construidos uniendo rectángulos, círculos, elipses, polígonos y líneas directamente en el código (por ejemplo, los métodos `_draw_flower`, `_draw_skeleton` y `_draw_ghost` en el archivo `battle.py`).
- **Animaciones:** Las animaciones, como el pulso del corazón en la pantalla de inicio, la hierba moviéndose o el fantasma flotando, se logran utilizando funciones trigonométricas (`math.sin` y `math.cos`) aplicadas a las coordenadas a lo largo del tiempo.
- **Entorno (Tiles):** El suelo, las paredes, la hierba y los puntos de guardado se renderizan creando superficies de colores sólidos con patrones matemáticos superpuestos para simular texturas (definido en el método `_build_tile_surfaces` de `overworld.py`).
- **Interfaz de Usuario (HUD):** Las barras de vida, cajas de diálogo, el menú de combate y el HUD general son dibujados mediante primitivas geométricas simples.

Esta decisión de diseño asegura que el juego sea extremadamente ligero, independiente de archivos externos y demuestre un control avanzado sobre la renderización por código.

---

## 3. Arquitectura y Estructura del Código
El proyecto está dividido en múltiples módulos (archivos `.py`) siguiendo los principios de la programación orientada a objetos (POO) para mantener un código limpio, escalable y organizado. A continuación, se detalla para qué funciona cada archivo:

### `main.py` (Bucle Principal y Gestor de Estados)
Es el punto de entrada del juego. Contiene la clase `Game` que se encarga de:
- Iniciar la ventana de Pygame y el reloj (control de FPS).
- Manejar los datos globales del jugador (Nombre, HP, Ataque, Defensa, Nivel, Experiencia, Oro y Objetos).
- Controlar la **Máquina de Estados** del juego. Se encarga de cambiar fluidamente entre la pantalla de Título (`STATE_TITLE`), la exploración (`STATE_OVERWORLD`), las peleas (`STATE_BATTLE`), el Game Over (`STATE_GAME_OVER`) y la pantalla de Victoria (`STATE_VICTORY_SCREEN`).
- Gestionar las transiciones visuales (fade in y fade out) entre estos estados.

### `settings.py` (Configuración Global)
Almacena todas las constantes y configuraciones que se usan en todo el juego. Aquí se define la resolución de la pantalla, los FPS, los colores base en formato RGB (Blanco, Negro, Rojo, etc.), las dimensiones de la caja de batalla y las estadísticas iniciales del jugador.

### `overworld.py` (Mundo y Exploración)
Controla la fase en la que el jugador se mueve por el mapa.
- Carga el mapa de cuadrículas (tiles) y gestiona qué áreas son transitables y cuáles son colisiones (paredes).
- Sigue al jugador con una cámara dinámica que se desplaza suavizadamente.
- Calcula la probabilidad de **encuentros aleatorios**. Si el jugador camina sobre el tile de "hierba", hay un porcentaje de probabilidad en cada paso de activar un combate con un enemigo aleatorio.
- Gestiona las interacciones con los puntos de guardado y NPCs adyacentes al presionar la tecla de acción `[Z]`.

### `player.py` y `npc.py` (Entidades del Mundo)
- **`player.py`**: Define la posición del jugador, interpreta los controles del teclado (Flechas o WASD) y gestiona la animación de movimiento en el mundo calculando la interpolación entre las casillas para un movimiento fluido.
- **`npc.py`**: Entidades pasivas con las que el jugador puede interactuar para leer diálogos.

### `battle.py` (Sistema de Combate)
Es uno de los módulos más complejos. Maneja por completo la escena de combate por turnos:
- **Estado Intro/Textos:** Cajas de diálogo con el sistema de escritura progresiva (efecto de máquina de escribir).
- **Menú de Jugador:** Permite elegir entre cuatro opciones fundamentales:
  1. **Luchar:** Activa un mini-juego rítmico (`FightBar`) para determinar el daño infligido.
  2. **Actuar:** Permite interactuar con el enemigo (ej. Hablar, Acariciar, Contar un chiste). Esto suma puntos de "piedad".
  3. **Objeto:** Abre el inventario para consumir ítems y recuperar HP (Vida).
  4. **Piedad:** Permite perdonar al enemigo y acabar el combate pacíficamente si se ha interactuado lo suficiente con él.
- **Turno del Enemigo:** Llama al módulo de "Bullet Hell" donde el jugador debe esquivar ataques moviendo su "alma" (un pequeño corazón) dentro de un cuadro limitado.

### `bullet_hell.py` (Mini-juego de Defensa)
Se activa en el turno del enemigo. Cambia el control del jugador a un pequeño corazón rojo que se mueve dentro de la "Caja de Batalla". El jugador debe esquivar proyectiles que se generan basados en los patrones de ataque del enemigo actual durante una cantidad determinada de segundos. Si un proyectil impacta, se resta HP.

### `enemies.py` (Datos de Enemigos)
Actúa como una base de datos de los contrincantes. Define las características únicas de cada uno (HP, Ataque, Recompensas), así como sus textos de presentación, opciones de "Actuar" personalizadas y cuántos turnos de interacción se requieren para poder ser perdonados.

### `ui.py` y `dialogue.py` (Interfaz Gráfica)
- **`ui.py`**: Dibuja elementos visuales estáticos o de información, como las barras de vida (HP) que se animan suavemente al recibir daño, y los menús de selección.
- **`dialogue.py`**: Administra la caja de texto inferior, renderizando las letras una a una con su respectivo sonido de "voz" y procesando los saltos de línea para que los textos encajen perfectamente en pantalla.

### `map_data.py` (Diseño de Niveles)
Contiene una matriz (array bidimensional) que dibuja literalmente el mapa del juego utilizando números (0 = vacío, 1 = suelo, 2 = pared, 3 = hierba de combates, 5 = punto de guardado, 6 = jefe final). 

---

## 4. Conclusión Técnica
El proyecto demuestra una sólida aplicación de la lógica de programación en Python. Al prescindir de motores gráficos modernos (como Unity o Godot) e imágenes pre-renderizadas, el juego evidencia un control matemático total sobre cada píxel dibujado en la pantalla y una excelente gestión de estados y eventos usando puramente código nativo y la librería estándar de `pygame`.
