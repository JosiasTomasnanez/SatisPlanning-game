import pygame
from .objeto import Objeto
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
from abc import abstractmethod
class Personaje(Objeto):
    def __init__(self, x, y, ancho, alto, sprite, sprites, velocidad, fuerza_salto, dinamico=True, tangible=True):
        super().__init__(x, y, ancho, alto, sprite, dinamico=dinamico, tangible=tangible)
        """
        Inicializa el personaje con posición, sprites y un inventario.

        :param x: Posición X inicial.
        :param y: Posición Y inicial.
        :param ancho: Ancho del personaje.
        :param alto: Altura del personaje.
        :param sprite: Sprite principal.
        :param sprites: Lista de sprites para animación.
        :param velocidad: Velocidad de movimiento.
        :param fuerza_salto: Fuerza de salto.
        """
        self.sprites = sprites
        self.velocidad = velocidad
        self.fuerza_salto = fuerza_salto
        # Componente para manejar la animación
        self.componente_animacion = ComponenteAnimacion(self, self.sprites)

        # Componente para manejar el movimiento
        self.componente_mover = ComponenteMover(self, self.componente_animacion)
    @abstractmethod
    def set_mundo(self, mundo):
        self.mundo = mundo
        self.componente_mover.set_mundo(mundo)
        
    @abstractmethod
    def actualizar(self, teclas):
        """
        Actualiza el estado del personaje, delegando el movimiento y la animación a los componentes.
        """
        self.componente_mover.actualizar(teclas)
        self.componente_animacion.actualizar()