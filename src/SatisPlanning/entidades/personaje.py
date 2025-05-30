import pygame
from SatisPlanning.entidades.objeto import Objeto
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componentes.componente_mover import ComponenteMover
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
class Personaje(Objeto):
    def __init__(self, x, y, ancho, alto, sprite, dinamico=True, tangible=True):
        super().__init__(x, y, ancho, alto, sprite, dinamico=dinamico, tangible=tangible)
        """
        Inicializa el personaje con posición, sprites y un inventario.

        :param x: Posición X inicial.
        :param y: Posición Y inicial.
        :param ancho: Ancho del personaje.
        :param alto: Altura del personaje.
        """
        '''
        Esto deberia inciarce en cada sublclase ya que es particular de cada personaje.

        super().__init__(x, y, ancho, alto, obtener_ruta_asset("p3.png"), dinamico=True, tangible=True)
        
        Esto deberia iniciarce en cada subclase, ya que cada personaje tiene 
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = 1  # 1 para derecha, -1 para izquierda
        '''

        # Cargar los sprites del personaje, TAL VEZ DEBERIA MODIFICARSE CUANDO SE AGREGUEN TEXTURAS DE ENEMI
        self.sprites = [
            pygame.image.load(obtener_ruta_asset(f"p{i}.png")) for i in range(1, 8)
        ]
        self.sprites = [pygame.transform.scale(sprite, (ancho, alto)) for sprite in self.sprites]

        # Componente para manejar la animación
        self.componente_animacion = ComponenteAnimacion(self, self.sprites)

        # Componente para manejar el movimiento
        self.componente_mover = ComponenteMover(self, self.componente_animacion)
   
    def set_mundo(self, mundo):
        self.mundo = mundo
        self.componente_mover.set_mundo(mundo)
  
    def actualizar(self, teclas):
        """
        Actualiza el estado del personaje, delegando el movimiento y la animación a los componentes.
        """
        self.componente_mover.actualizar(teclas)
        self.componente_animacion.actualizar()

#el manejo de coliciones y manejo de movimientos o ataques o demas, estaria bueno hacerlo como compoonentes , como usando el patron stratagy,  ya que hay muchos objetos u personajes que van a tener las mismas fisicas de movimiento pero con variables como la gravedad , entre otras diferentes, entonces seria hacer clases que se encarguen de dichos comportamientos, de las cuales los objetos puedan o no hacer uso, mandandole sus caracteristicas, y queda mucho mas modular y extendible el codigo


