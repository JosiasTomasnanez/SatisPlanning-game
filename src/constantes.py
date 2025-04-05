import pygame

ANCHO = 1280
ALTO = 720
TILE_SIZE = 32 # tamaño de cada bloque
FPS = 60  # Frames por segundo
FILAS = ALTO // TILE_SIZE
COLUMNAS = ANCHO // TILE_SIZE
COlOR_FONDO = (0, 0, 0)  # Color de fondo de la pantalla
# Font for rendering text
pygame.init()  # Ensure pygame is initialized before creating the font
FONT = pygame.font.Font(None, 24)  # Default font with size 24

# Sistema de física
GRAVEDAD = 0.5
FUERZA_SALTO = 12
VELOCIDAD_PERSONAJE = 4

# Colores de bloques (ampliados para futuros minerales)
COLORES = {
    0: (86, 222, 255),   # Aire/Cielo
    1: (120, 58, 0),     # Tierra
    2: (131, 153, 171),  # Piedra
    3: (34, 177, 76),    # Pasto
    4: (232, 144, 37),   # Hierro (para futuro)
    5: (45, 45, 45)      # Carbón (para futuro)
}

# texturas
TEXTURA_TIERRA = "src\\assets\\tierra.png"
TEXTURA_PIEDRA = "src\\assets\\piedra.png"
TEXTURA_PASTO = "src\\assets\\pasto.png"  

# Tipos de bloques sólidos
BLOQUES_SOLIDOS = {1, 2, 3}  # Tierra, Piedra, Pasto

# Herramientas
HERRAMIENTAS = {
    "mano": {"color": (200, 200, 200), "durabilidad": float('inf'), "bloques_efectivos": []},
    "pico": {"color": (139, 69, 19), "durabilidad": 100, "bloques_efectivos": [2, 4, 5]},
    "pala": {"color": (160, 82, 45), "durabilidad": 100, "bloques_efectivos": [1, 3]}
}

CATEGORIAS = ["Bloques", "Herramientas"]