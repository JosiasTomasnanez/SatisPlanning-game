from SatisPlanning.entidades.personaje import Personaje
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
from SatisPlanning.componentes.comportamiento_movimiento import MovimientoAleatorio, MovimientoPersecucion
import random
import pygame

class Zombie(Personaje):
    def __init__(self, x, y, ancho, alto, comportamiento_movimiento=None):

        super().__init__(x, y, ancho, alto, obtener_ruta_asset("enemigo.png"), dinamico=True, tangible=True)
        # Sobrescribir los sprites para que solo use el sprite de enemigo
        self.sprites = [pygame.image.load(obtener_ruta_asset("enemigo.png"))]
        self.sprites = [pygame.transform.scale(sprite, (ancho, alto)) for sprite in self.sprites]

        # Posición y estado inicial del enemigo
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = -1  

        # Componente para manejar la animación
        self.componente_animacion = ComponenteAnimacion(self, self.sprites)

        # Componente para manejar el movimiento
        self.componente_mover = ComponenteMover(self, self.componente_animacion)
        self.es_enemigo = True
        
        # Estrategias de movimiento (Strategy)
        self.movimiento_aleatorio = MovimientoAleatorio()
        self.movimiento_persecucion = MovimientoPersecucion()
        self.comportamiento_movimiento = self.movimiento_aleatorio

        self.vida = 100  # Puntos de vida del zombie

    def set_mundo(self, mundo):
        self.componente_mover.set_mundo(mundo)
        super().set_mundo(mundo)

    def actualizar(self):
        # Cambia a persecución si el jugador está cerca, si no, usa aleatorio
        jugador = self.mundo.personaje
        dx = jugador.x - self.x
        if abs(dx) < 120:
            self.comportamiento_movimiento = self.movimiento_persecucion
        else:
            self.comportamiento_movimiento = self.movimiento_aleatorio
        self.comportamiento_movimiento.mover(self)
        self.componente_animacion.actualizar()

    def recibir_danio(self, cantidad):
        """
        Resta puntos de vida al zombie. Si la vida llega a 0, puedes manejar la muerte aquí.
        """
        self.vida -= cantidad
        if self.vida <= 0:
            self.vida = 0
            # Aquí podrías poner lógica de muerte, eliminar el zombie, etc.
            print('¡Zombie derrotado!')