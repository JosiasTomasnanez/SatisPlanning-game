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
FUERZA_SALTO = 12
VELOCIDAD_PERSONAJE = 4

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
        (40, 40)
    )
    for i in range(1, 6)
]
# Categorías
CATEGORIAS = ["Bloques", "Herramientas"]