import pygame
import SatisPlanning.constantes as ct

class Graficos:
    def __init__(self, mundo):
        self.mundo = mundo
        self.pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO))
    
    def dibujar(self):
        self.pantalla.fill(ct.COLOR_FONDO)  # Limpia pantalla
        self.pantalla.fill(ct.COLORES[0])  # Fondo cielo
        self.mundo.dibujar(self.pantalla)
        pygame.display.flip()
# En un futuro esta clase va a ser mas compleja manejando capas, con funciones que permitan manejar por capas , hay que analizar como implementar eso
