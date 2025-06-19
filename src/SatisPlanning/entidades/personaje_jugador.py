from SatisPlanning.entidades.personaje import Personaje  
from SatisPlanning.inventario import Inventario
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
from SatisPlanning.componentes.componente_inventario import ComponenteInventario
from SatisPlanning.componentes.componente_atacar import ComponenteAtacar
from SatisPlanning.entidades.mano import Mano
from SatisPlanning.entidades.espada import Espada
from SatisPlanning.patron_observer import Observable
from SatisPlanning.display_vidas import DisplayVidas
import pygame
import time
import SatisPlanning.constantes as ct

class PersonajeJugador(Personaje, Observable):
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
        # Componente para manejar el ataque
        # self.componente_atacar = ComponenteAtacar(self)  # ELIMINADO, ahora lo tiene el arma
        # Vida y cooldown de daño
        self.vida = 100
        self._ultimo_danio = 0  # timestamp del último daño recibido
        self.cooldown_danio = 2.0  # segundos
        self.es_jugador = True
        self.arma = Mano()  # Siempre tiene Mano por defecto
        self.atacando = False  # Nuevo: indica si está atacando
        self.tiempo_ataque = 0  # Nuevo: duración de la animación de ataque
        Observable.__init__(self)  # Inicializa Observable
        self.display_vidas = DisplayVidas(self.vida)
        self.agregar_observer(self.display_vidas)
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
        if self.atacando:
            self.arma.actualizar_animacion_ataque()
            self.tiempo_ataque -= 1
            if self.tiempo_ataque <= 0:
                self.atacando = False

    def manejar_evento(self, evento):
        # Actualiza el inventario según eventos individuales
        self.componente_inventario.actualizar(evento)
        # Atacar con la tecla J o con el click izquierdo del mouse
        if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_j) or \
           (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1):
           self.arma.atacar(self)
        # Puedes agregar aquí otros componentes que reaccionen a eventos
    
    def recibir_danio(self, cantidad):
        ahora = time.time()
        if ahora - self._ultimo_danio >= self.cooldown_danio:
            self.vida -= cantidad
            self._ultimo_danio = ahora
            if self.vida < 0:
                self.vida = 0
            self.notificar_observers(self.vida)  # Notifica a los observers del cambio de vida

    def curar(self, cantidad):
        self.vida += cantidad
        if self.vida > 100:
            self.vida = 100
        self.notificar_observers(self.vida)

    def notificar_colision(self, objeto):
        # Si colisiona con un enemigo, recibe daño
        if hasattr(objeto, 'es_enemigo') and getattr(objeto, 'es_enemigo', False):
            self.recibir_danio(objeto.danio)

    def equipar_arma(self, arma):
        self.arma = arma if arma else Mano()

