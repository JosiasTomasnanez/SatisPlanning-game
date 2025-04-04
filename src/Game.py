from World import World
from Graphics import Graphics
from camara import Camera

class Game:
    def __init__(self):
        self.camara = Camera()
        self.world = World(self.camara)
        self.graphics = Graphics(self.world)

    def handle_events(self):
        import pygame
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                return None  # Indica que el juego debe cerrarse
        return eventos  # Devuelve la lista de eventos

    def update(self, dt, eventos):       
        self.world.update(dt, eventos)  # Actualiza el mundo con los eventos

    def render(self):        
        self.graphics.render()