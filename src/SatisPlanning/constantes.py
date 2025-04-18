import pygame
from SatisPlanning.utilidades import obtener_ruta_asset

ANCHO = 1280  # Ancho de la pantalla
ALTO = 720  # Alto de la pantalla
TAMANIO_BLOQUE = 32  # Tamaño de cada bloque
FPS = 60  # Cuadros por segundo
FILAS = ALTO // TAMANIO_BLOQUE
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
    0: (86, 222, 255),   # Aire/Cielo
    1: (120, 58, 0),     # Tierra
    2: (131, 153, 171),  # Piedra
    3: (34, 177, 76),    # Pasto
    4: (232, 144, 37),   # Hierro (para futuro)
    5: (45, 45, 45)      # Carbón (para futuro)
}

# Texturas
TEXTURA_TIERRA = obtener_ruta_asset("tierra.png")
TEXTURA_PIEDRA = obtener_ruta_asset("piedra.png")
TEXTURA_PASTO = obtener_ruta_asset("pasto.png")   

# Tipos de bloques sólidos
BLOQUES_SOLIDOS = {1, 2, 3}  # Tierra, Piedra, Pasto

# Herramientas
HERRAMIENTAS = {
    "mano": {"color": (200, 200, 200), "durabilidad": float('inf'), "bloques_efectivos": []},
    "pico": {"color": (139, 69, 19), "durabilidad": 100, "bloques_efectivos": [2, 4, 5]},
    "pala": {"color": (160, 82, 45), "durabilidad": 100, "bloques_efectivos": [1, 3]}
}

# Categorías
CATEGORIAS = ["Bloques", "Herramientas"]

#hay que modificar por que va a quedar un poco obsoleto muchas de estas variables, ya que tenemos que pensar que de verdad queremos que sea constante y que deseamos que sea modificable, la gravedad, salto, velocidad del personaje, son cosas que no deberian ir por que son modificables desde otros lados, por lo tanto solo usar esta clase cuando realmente lo amerite y para cosas inmovibles
