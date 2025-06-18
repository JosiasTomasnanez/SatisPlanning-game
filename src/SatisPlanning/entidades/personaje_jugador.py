from .personaje import Personaje  
from SatisPlanning.inventario import Inventario
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
from SatisPlanning.componentes.componente_inventario import ComponenteInventario
import pygame
import SatisPlanning.constantes as ct
import time

class PersonajeJugador(Personaje):
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el personaje jugador con posición, sprites y un inventario.

        :param x: Posición X inicial.
        :param y: Posición Y inicial.
        :param ancho: Ancho del personaje.
        :param alto: Altura del personaje.
        """
        velocidad = 4         # Velocidad específica para el jugador
        fuerza_salto = 11     # Fuerza de salto específica para el jugador
        super().__init__(x, y, ancho, alto, ct.SPRITE_JUGADOR, sprites=ct.SPRITES_JUGADOR, velocidad=velocidad, fuerza_salto=fuerza_salto, dinamico=True, tangible=True)
        
        # Posicion inicial
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = 1  # 1 para derecha, -1 para izquierda

        # Inventario del personaje
        self.componente_inventario = ComponenteInventario(self,Inventario())

        # Componente para manejar la animación
        self.componente_animacion = ComponenteAnimacion(self, self.sprites)

        # Componente para manejar el movimiento
        self.componente_mover = ComponenteMover(self, self.componente_animacion)

        # Vida y cooldown de daño
        self.vida = 100
        self._ultimo_danio = 0  # timestamp del último daño recibido
        self.cooldown_danio = 2.0  # segundos
        self.es_jugador = True

    def obtener_inventario(self):
        return self.componente_inventario.inventario
    
    def set_mundo(self, mundo):
       self.componente_inventario.set_mundo(mundo)
       super().set_mundo(mundo)

    def actualizar(self, teclas):
        # Actualiza el movimiento según teclas presionadas
        super().actualizar(teclas)

    def manejar_evento(self, evento):
        # Actualiza el inventario según eventos individuales
        self.componente_inventario.actualizar(evento)
        # Puedes agregar aquí otros componentes que reaccionen a eventos

    def recibir_danio(self, cantidad):
        ahora = time.time()
        if ahora - self._ultimo_danio >= self.cooldown_danio:
            self.vida -= cantidad
            self._ultimo_danio = ahora
            if self.vida < 0:
                self.vida = 0
            print(f"¡Jugador recibió {cantidad} de daño! Vida restante: {self.vida}")

    def notificar_colision(self, objeto):
        # Si colisiona con un enemigo, recibe daño
        if hasattr(objeto, 'es_enemigo') and getattr(objeto, 'es_enemigo', False):
            self.recibir_danio(10)
