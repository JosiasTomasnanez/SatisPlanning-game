from World import World
from Graphics import Graphics
from camara import Camera
import pygame

class Game:
    def __init__(self):
        self.camara = Camera() # Inicializa la cámara
        self.world = World(self.camara) # Inicializa el mundo, pasando la cámara
        self.graphics = Graphics(self.world) # Inicializa los gráficos, pasando el mundo

    """
    Manejador de eventos del juego.
    Captura eventos de entrada y verifica si el juego debe cerrarse.
    """
    def handle_events(self):
        eventos = pygame.event.get() # Obtiene la lista de eventos
        for evento in eventos: 
            if evento.type == pygame.QUIT: # Si se recibe un evento de cierre
                return None  # Indica que el juego debe cerrarse
        return eventos  # Devuelve la lista de eventos

    "Actualiza el juego."
    def update(self, dt, eventos):  
        self.world.update(dt, eventos)  # Actualiza el mundo con los eventos

    """Renderiza el juego en pantalla."""
    def render(self):
        self.graphics.render()