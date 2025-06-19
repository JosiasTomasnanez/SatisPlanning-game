import pygame
from SatisPlanning.componentes.componente import Componente

class ComponenteAnimacion(Componente):
    def __init__(self, propietario, sprites, indice_inicial=0, sprite_idle=None, frames_idle=20):
        """
        Inicializa el componente de animación.

        :param propietario: Objeto que usará este componente.
        :param sprites: Lista de sprites para la animación.
        :param indice_inicial: Índice inicial del sprite.
        :param sprite_idle: Sprite a mostrar cuando está quieto (por defecto, sprites[0]).
        :param frames_idle: Frames sin movimiento para activar idle.
        """
        super().__init__(propietario)
        self.sprites = sprites
        self.sprite_actual = indice_inicial
        self.contador_animacion = 0
        self.imagen_actual = sprites[self.sprite_actual]
        self.sprite_idle = sprite_idle if sprite_idle is not None else sprites[0]
        self.frames_idle = frames_idle
        self.contador_idle = 0
        self.esta_idle = False

    def set_sprites(self, sprites):
        """
        Permite actualizar la lista de sprites y el sprite idle cuando cambian de tamaño o paquete.
        """
        self.sprites = sprites
        self.sprite_idle = sprites[0]
        # Si está en idle, actualizar la imagen actual también
        if self.esta_idle:
            self.imagen_actual = self.sprite_idle

    def notificar_movimiento(self):
        """
        Notifica al componente de animación que el objeto se está moviendo.
        """
        self.contador_animacion += 1
        self.contador_idle = 0
        self.esta_idle = False
        if self.contador_animacion >= 10:
            self.sprite_actual = (self.sprite_actual + 1) % len(self.sprites)
            self.contador_animacion = 0

        # Actualizar la imagen del sprite actual, considerando dirección si existe
        self.imagen_actual = self.sprites[self.sprite_actual]
        if hasattr(self.propietario, "direccion") and getattr(self.propietario, "direccion") == -1:
            self.imagen_actual = pygame.transform.flip(self.imagen_actual, True, False)

    def actualizar(self, dt=None):
        """
        Actualiza el estado del componente de animación.
        Si no hubo movimiento por varios frames, muestra el sprite idle.
        """
        self.contador_idle += 1
        if self.contador_idle >= self.frames_idle:
            self.esta_idle = True
        if self.esta_idle:
            self.imagen_actual = self.sprite_idle
            if hasattr(self.propietario, "direccion") and getattr(self.propietario, "direccion") == -1:
                self.imagen_actual = pygame.transform.flip(self.sprite_idle, True, False)