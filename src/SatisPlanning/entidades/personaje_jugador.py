from .personaje import Personaje  
from SatisPlanning.inventario import Inventario
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
from SatisPlanning.componentes.componente_inventario import ComponenteInventario
import pygame
import SatisPlanning.constantes as ct

class PersonajeJugador(Personaje):
    _instancia = None

    def __new__(cls, x, y, ancho, alto):
        if cls._instancia is None:
            cls._instancia = super(PersonajeJugador, cls).__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self, x, y, ancho, alto):
        if getattr(self, "_inicializado", False):
            return
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

        self._inicializado = True

    @classmethod
    def reset(cls):
        """Resetea la instancia singleton del jugador."""
        if cls._instancia is not None:
            cls._instancia = None

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
