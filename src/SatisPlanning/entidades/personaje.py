import pygame
from SatisPlanning.entidades.objeto import Objeto
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

    def cambiar_tamano(self, ancho, alto):
        """
        Cambia el tamaño de los sprites y la hitbox del personaje.
        """
        # Redimensionar sprites
        self.sprites = [
            pygame.transform.scale(sprite, (ancho, alto))
            for sprite in self.sprites
        ]
        self.componente_animacion.set_sprites(self.sprites)
        # Cambiar tamaño de la imagen principal si existe
        if hasattr(self, 'imagen') and self.imagen:
            self.imagen = pygame.transform.scale(self.imagen, (ancho, alto))
        # Actualizar hitbox
        self.ancho = ancho
        self.alto = alto
        self.hitbox.width = ancho - 4
        self.hitbox.height = alto
        # Opcional: ajustar la posición de la hitbox si es necesario
        self.hitbox.topleft = (self.x + 17, self.y + 20)
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

    def set_sprites(self, sprites):
        """
        Cambia el paquete de sprites del personaje y actualiza el componente de animación.
        :param sprites: Lista de imágenes (superficies pygame) para animación.
        """
        self.sprites = sprites
        self.componente_animacion.set_sprites(sprites)
