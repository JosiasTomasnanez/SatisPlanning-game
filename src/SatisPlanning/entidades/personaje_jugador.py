from SatisPlanning.entidades.personaje import Personaje  
from SatisPlanning.inventario import Inventario
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
from SatisPlanning.componentes.componente_inventario import ComponenteInventario
import pygame

class PersonajeJugador(Personaje):
    def __init__(self, x, y, ancho, alto):

        super().__init__(x, y, ancho, alto, obtener_ruta_asset("p3.png"), dinamico=True, tangible=True)
        
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

        # Atributo para identificar si es un jugador
        self.es_jugador = True

        # Puntos de vida del jugador
        self.vida = 100  

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

    def notificar_colision(self, otro):
        """
        Lógica de reacción cuando el jugador colisiona con otro objeto o enemigo.
        """
        if hasattr(otro, 'es_enemigo') and otro.es_enemigo:
            # Ejemplo: reducir vida, empujar, etc.
            print('¡El jugador colisionó con un enemigo!')
        # Aquí puedes agregar más lógica según el tipo de colisión

    def recibir_danio(self, cantidad):
        """
        Resta puntos de vida al jugador. Si la vida llega a 0, puedes manejar la muerte aquí.
        """
        self.vida -= cantidad
        if self.vida <= 0:
            self.vida = 0
            # Aquí podrías poner lógica de muerte, reinicio, etc.
            print('¡Jugador derrotado!')
