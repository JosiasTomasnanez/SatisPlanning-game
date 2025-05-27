from SatisPlanning.entidades.personaje import Personaje
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
import random
import pygame

class PersonajeEnemigo(Personaje):
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el personaje enemigo con posición y sprites.

        :param x: Posición X inicial.
        :param y: Posición Y inicial.
        :param ancho: Ancho del personaje.
        :param alto: Altura del personaje.
        """
        super().__init__(x, y, ancho, alto, obtener_ruta_asset("enemigo.png"), dinamico=True, tangible=True)
        # Sobrescribir los sprites para que solo use el sprite de enemigo
        self.sprites = [pygame.image.load(obtener_ruta_asset("enemigo.png"))]
        self.sprites = [pygame.transform.scale(sprite, (ancho, alto)) for sprite in self.sprites]
        # Posición y estado inicial del enemigo
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = -1  # Por defecto, los enemigos pueden mirar a la izquierda
        # Componente para manejar la animación
        self.componente_animacion = ComponenteAnimacion(self, self.sprites)
        # Componente para manejar el movimiento
        self.componente_mover = ComponenteMover(self, self.componente_animacion)
        self.tiempo_cambio_direccion = 0
        self.duracion_direccion = random.randint(30, 90)  # frames
        self.direccion_aleatoria = random.choice([-1, 0, 1])  # -1: izquierda, 0: quieto, 1: derecha

    def set_mundo(self, mundo):
        self.componente_mover.set_mundo(mundo)
        super().set_mundo(mundo)

    def actualizar(self, *args, **kwargs):
        # Movimiento aleatorio simple 
        self.tiempo_cambio_direccion += 1
        if self.tiempo_cambio_direccion > self.duracion_direccion:
            self.direccion_aleatoria = random.choice([-1, 0, 1])
            self.duracion_direccion = random.randint(30, 90)
            self.tiempo_cambio_direccion = 0
        self.vel_x = self.direccion_aleatoria * 2  # velocidad constante
        # Simular teclas presionadas para el movimiento del enemigo
        teclas_falsas = {
            100: self.direccion_aleatoria == 1,  # pygame.K_d
            97: self.direccion_aleatoria == -1, # pygame.K_a
            119: False, # pygame.K_w
            32: False   # pygame.K_SPACE
        }
        self.componente_mover.actualizar(teclas_falsas)
        self.componente_animacion.actualizar()

    # Puedes agregar más métodos específicos para enemigos aquí
