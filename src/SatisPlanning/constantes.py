import pygame
from SatisPlanning.utilidades import obtener_ruta_asset, scale_keep_aspect

ANCHO = 1280  # Ancho de la pantalla
ALTO = 720  # Alto de la pantalla
TAMANIO_BLOQUE = 32  # Tamaño de cada bloque
FPS = 60  # Cuadros por segundo
FILAS = (ALTO // TAMANIO_BLOQUE)+6
COLUMNAS = ANCHO // TAMANIO_BLOQUE
COLOR_FONDO = (0, 0, 0)  # Color de fondo de la pantalla

# Fuente para renderizar texto
pygame.init()  # Asegura que pygame esté inicializado antes de crear la fuente
FUENTE = pygame.font.Font(None, 24)  # Fuente predeterminada con tamaño 24

# Sistema de física
GRAVEDAD = 0.5

# Colores de bloques (ampliados para futuros minerales)
COLORES = {
    0: (65, 200, 230),   # Aire/Cielo
}

# Texturas
TEXTURA_TIERRA = obtener_ruta_asset("tierra.png")
TEXTURA_PIEDRA = obtener_ruta_asset("piedra.png")
TEXTURA_PASTO = obtener_ruta_asset("pasto.png")   

# Tipos de bloques sólidos
BLOQUES_SOLIDOS = {1, 2, 3}  # Tierra, Piedra, Pasto

# Sprite principal del jugador
SPRITE_JUGADOR = obtener_ruta_asset("pf.png")

# Sprites animados del jugador (p1.png a p7.png, escalados con aspect ratio)
SPRITES_JUGADOR = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"p{i}.png")),
        (40, 40), 
        True
    )
    for i in range(1, 6)
]
SPRITES_ENEMIGO = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"enemigo{i}.png")),
        (40, 40),
        False
    )
    for i in range(1, 9)
]
# Enemigo nivel 2: ea1.png a ea8.png
SPRITES_ENEMIGO_2 = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"ea{i}.png")),
        (40, 40),
        False
    )
    for i in range(1, 9)
]

# Enemigo nivel 3: ev1.png a ev8.png
SPRITES_ENEMIGO_3 = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"ev{i}.png")),
        (40, 40),
        False
    )
    for i in range(1, 9)
]

# Boss 1: bma1.png a bma8.png
SPRITES_BOSS_1 = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"bma{i}.png")),
        (70, 70),
        False
    )
    for i in range(1, 9)
]

# Boss 2: bv1.png a bv8.png
SPRITES_BOSS_2 = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"bv{i}.png")),
        (70, 70),
        False
    )
    for i in range(1, 9)
]

# Boss 3: bm1.png a bm8.png
SPRITES_BOSS_3 = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"bm{i}.png")),
        (70, 70),
        False
    )
    for i in range(1, 9)
]
# Ruta de la imagen de la mano
RUTA_MANO = obtener_ruta_asset("mano.png")
RUTA_CORAZON = obtener_ruta_asset("mana_vida/sprite_0.png")

# Categorías
CATEGORIAS = ["Bloques", "Herramientas"]

# Sprites de la espada (ejemplo: espada1.png a espada4.png)
SPRITES_ESPADA = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"espada/e{i}.png")),
        (40, 40),
        True
    )
    for i in range(1, 6)
]
SPRITES_MANO = [
    scale_keep_aspect(
        pygame.image.load(obtener_ruta_asset(f"mano/mano{i}.png")),
        (40, 40),
        True
    )
    for i in range(1, 5)
]

# Items (ahora usando obtener_ruta_asset como el resto)
ITEM_POCIONES = [
    obtener_ruta_asset(f"pociones/sprite_{i}.png") for i in range(5)
]
# ITEM_HACHA = [obtener_ruta_asset(f"hacha/sprite_{i}.png") for i in range(3)]
# ITEM_ESPADA = [obtener_ruta_asset(f"espada/sprite_{i}.png") for i in range(5)]
ITEM_ARMADURA = [
    obtener_ruta_asset(f"armadura/sprite_{i}.png") for i in range(3)
]
ITEM_MINERALES = [
    obtener_ruta_asset(f"minerales/sprite_{i}.png") for i in range(13, 20)
]
