from SatisPlanning.entidades.personaje import Personaje
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
from SatisPlanning.componentes.comportamiento_movimiento import EstrategiaMovimientoAleatorio, EstrategiaMovimientoPersecucion
import random
import pygame
import SatisPlanning.constantes as ct
from SatisPlanning.entidades.consumible import PocionCura
from SatisPlanning.entidades.espada import Espada

class Enemigo(Personaje):
    def __init__(self, x, y, ancho, alto, comportamiento_movimiento=None, distancia_persecucion=120, sprites=None):
        velocidad = 2         # Velocidad específica para enemigo
        fuerza_salto = 10     # Fuerza de salto específica para enemigo
        if sprites is None:
            sprites = ct.SPRITES_ENEMIGO
        super().__init__(x, y, ancho, alto, ct.SPRITE_JUGADOR, sprites=sprites, velocidad=velocidad, fuerza_salto=fuerza_salto, dinamico=True, tangible=True)

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
        self.movimiento_aleatorio = EstrategiaMovimientoAleatorio()
        self.movimiento_persecucion = EstrategiaMovimientoPersecucion(distancia_persecucion)
        self.comportamiento_movimiento = self.movimiento_aleatorio

        self.vida = 100  # Puntos de vida del enemigo
        self.danio = 10  # Daño que inflige el enemigo al jugador

        # Si se pasan sprites personalizados, setéalos y luego escala
        if sprites is not None:
            self.set_sprites(sprites)
        self.cambiar_tamano(ancho, alto)

    def set_mundo(self, mundo):
        self.componente_mover.set_mundo(mundo)
        super().set_mundo(mundo)

    def set_comportamiento_movimiento(self, comportamiento):
        """Permite cambiar la estrategia de movimiento en tiempo de ejecución."""
        self.comportamiento_movimiento = comportamiento

    def actualizar(self):
        # Solo ejecuta el comportamiento actual, no cambia la estrategia aquí
        self.comportamiento_movimiento.mover(self)
        self.componente_animacion.actualizar()

    def recibir_danio(self, cantidad, atacante=None):
        self.vida -= cantidad
        if self.vida <= 0:
            self.vida = 0
            self.muerto = True  # Marca al enemigo como muerto
            self.soltar_objeto_al_morir()
            # Si es boss, soltar espada
            if getattr(self, "es_boss", False):
                self.soltar_espada_al_morir()

    def soltar_objeto_al_morir(self):
        """
        Probabilidad de soltar una poción de cura al morir.
        """
        probabilidad = 0.4  # 40% de probabilidad
        if hasattr(self, "mundo") and random.random() < probabilidad:
            pocion = PocionCura(self.x, self.y, 30, 30)
            # Soltar como no tangible
            self.mundo.agregar_objeto(pocion, False)

    def soltar_espada_al_morir(self):
        """
        Suelta una espada de forma intangible al morir (solo para bosses).
        El daño de la espada depende del nivel del boss.
        """
        if hasattr(self, "mundo"):
            nivel_boss = getattr(self, "nivel", 1)
            danio_espada = 35 + 15 * (nivel_boss) 
            espada = Espada(self.x, self.y, 60, 65, danio=danio_espada)
            self.mundo.agregar_objeto(espada, False)

    def notificar_colision(self, objeto):
        # Recibe daño si colisiona con un arma
        if hasattr(objeto, 'es_arma') and getattr(objeto, 'es_arma', False):
            self.recibir_danio(objeto.danio)