import pygame

class ComponenteAnimacion:
    def __init__(self, personaje, sprites):
        """
        Inicializa el componente de animación.

        :param personaje: Instancia del personaje que usará este componente.
        :param sprites: Lista de sprites para la animación.
        """
        self.personaje = personaje
        self.sprites = sprites
        self.sprite_actual = 2  # Índice del sprite inicial
        self.contador_animacion = 0
        self.imagen_actual = sprites[self.sprite_actual]

    def notificar_movimiento(self):
        """
        Notifica al componente de animación que el personaje se está moviendo.
        """
        self.contador_animacion += 1
        if self.contador_animacion >= 10:
            self.sprite_actual = (self.sprite_actual + 1) % len(self.sprites)
            self.contador_animacion = 0

        # Actualizar la imagen del sprite actual según la dirección
        self.imagen_actual = self.sprites[self.sprite_actual]
        if self.personaje.direccion == -1:
            self.imagen_actual = pygame.transform.flip(self.imagen_actual, True, False)

    def actualizar(self):
        """
        Actualiza el estado del componente de animación.
        """
        # Puede incluir lógica adicional si es necesario
        pass


#hacer este componente generico para que pueda ser usado por cualquier objeto