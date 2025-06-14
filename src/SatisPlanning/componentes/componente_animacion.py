import pygame
from .componente import Componente

class ComponenteAnimacion(Componente):
    def __init__(self, objeto, sprites):
        """
        Inicializa el componente de animación.

        :param objeto: Instancia del objeto que usará este componente.
        :param sprites: Lista de sprites para la animación.
        """
        super().__init__(objeto)
        self.objeto = objeto  # Asegura que el atributo exista
        self.sprites = sprites
        self.sprite_actual = 2  # Índice del sprite inicial
        self.contador_animacion = 0
        self.imagen_actual = sprites[self.sprite_actual]

    def notificar_movimiento(self):
        """
        Notifica al componente de animación que el objeto se está moviendo.
        """
        self.contador_animacion += 1
        if self.contador_animacion >= 10:
            self.sprite_actual = (self.sprite_actual + 1) % len(self.sprites)
            self.contador_animacion = 0

        # Actualizar la imagen del sprite actual según la dirección (si existe)
        self.imagen_actual = self.sprites[self.sprite_actual]
        # Solo voltear si el objeto tiene el atributo 'direccion'
        if hasattr(self.objeto, "direccion") and self.objeto.direccion == -1:
            self.imagen_actual = pygame.transform.flip(self.imagen_actual, True, False)

    def actualizar(self):
        """
        Actualiza el estado del componente de animación.
        """
        # Puede incluir lógica adicional si es necesario
        pass


#hacer este componente generico para que pueda ser usado por cualquier objeto