import pygame
import SatisPlanning.constantes as ct
from .componente import Componente

class ComponenteMover(Componente):
    def __init__(self, personaje, componente_animacion):
        """
        Inicializa el componente de movimiento.

        :param personaje: Instancia del personaje que usará este componente.
        :param componente_animacion: Instancia del componente de animación asociado.
        :param mundo: Instancia del mundo donde se mueve el personaje.
        """
        super().__init__(personaje)
        self.componente_animacion = componente_animacion
        self.mundo = None

    def set_mundo(self, mundo):
        self.mundo = mundo

    def mover(self, teclas):
        """
        Maneja el movimiento del personaje, incluyendo gravedad, salto y colisiones.
        """
        personaje = self.propietario
        mundo = self.mundo

        # Movimiento horizontal
        personaje.vel_x = (teclas[pygame.K_d] - teclas[pygame.K_a]) * ct.VELOCIDAD_PERSONAJE
        nueva_hitbox = personaje.hitbox.move(personaje.vel_x, 0)
        if not mundo.colisiona(nueva_hitbox, personaje):
            personaje.hitbox = nueva_hitbox

        # Actualizar la dirección del personaje
        if personaje.vel_x > 0:
            personaje.direccion = 1
        elif personaje.vel_x < 0:
            personaje.direccion = -1

        # Gravedad y salto
        if not personaje.en_el_suelo:
            personaje.vel_y += ct.GRAVEDAD
        if (teclas[pygame.K_w] or teclas[pygame.K_SPACE]) and personaje.en_el_suelo:
            personaje.vel_y = -ct.FUERZA_SALTO
            personaje.en_el_suelo = False

        # Movimiento vertical
        nueva_hitbox = personaje.hitbox.move(0, personaje.vel_y)
        if not mundo.colisiona(nueva_hitbox, personaje):
            personaje.hitbox = nueva_hitbox
            personaje.en_el_suelo = False
        else:
            personaje.vel_y = 0
            personaje.en_el_suelo = True

        # Actualizar la posición del personaje
        personaje.x, personaje.y = personaje.hitbox.topleft

        # Notificar al componente de animación si el personaje se mueve
        if personaje.vel_x != 0:
            self.componente_animacion.notificar_movimiento()

    def actualizar(self, teclas):
        """
        Interfaz para modificar el estado del personaje ante eventos de movimiento.
        Actualiza el estado del componente de movimiento según las teclas recibidas.
        :param teclas: diccionario de teclas presionadas
        """
        self.mover(teclas)


