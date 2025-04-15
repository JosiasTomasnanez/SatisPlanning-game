import pygame
import SatisPlanning.constantes as ct

class Graphics:
    def __init__(self, world):
        self.world = world
        self.screen = pygame.display.set_mode((ct.ANCHO, ct.ALTO)) # Inicializa la pantalla
    
    def render(self):
        self.screen.fill(ct.COlOR_FONDO)  # Limpia pantalla
        self.screen.fill(ct.COLORES[0])  # Fondo cielo
        self.world.draw(self.screen)  # Dibuja el mundo
        pygame.display.flip()
