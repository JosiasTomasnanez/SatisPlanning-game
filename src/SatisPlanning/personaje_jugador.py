import pygame
from .personaje import Personaje  
from SatisPlanning.inventario import Inventario
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componente_mover import ComponenteMover
from SatisPlanning.componente_animacion import ComponenteAnimacion
from SatisPlanning.componente_agregar_objeto import ComponenteAgregarObjeto

class personaje_jugador(Personaje):
    def _init_(self, x, y, ancho, alto):
        """
        Inicializa el personaje jugador con posición, sprites y un inventario.

        :param x: Posición X inicial.
        :param y: Posición Y inicial.
        :param ancho: Ancho del personaje.
        :param alto: Altura del personaje.
        """
        super().__init__(x, y, ancho, alto, obtener_ruta_asset("p3"), dinamico=True, tangible=True)
        
        # Posicion inicial
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = 1  # 1 para derecha, -1 para izquierda

        # Inventario del personaje
        self.inventario = Inventario()
        self.inventario.visible = False

        # Componente para manejar la animación
        self.componente_animacion = ComponenteAnimacion(self, self.sprites)

        # Componente para manejar el movimiento
        self.componente_mover = ComponenteMover(self, self.componente_animacion)

        # Componente para agregar objetos al mundo
        self.componente_agregar_objeto = ComponenteAgregarObjeto(self)


    def manejar_evento(self, evento, mundo):
        """
        Maneja eventos relacionados con el personaje, como abrir/cerrar el inventario y seleccionar elementos de la barra rápida.
        """
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_i:
                self.inventario.visible = not self.inventario.visible

            if pygame.K_1 <= evento.key <= pygame.K_9:
                indice_barra = evento.key - pygame.K_1
                self.inventario.seleccionar_barra_rapida(indice_barra)

            if evento.key == pygame.K_g:
                item_soltado = self.inventario.soltar_item_seleccionado()
                if item_soltado:
                    if(self.direccion == 1):
                        item_soltado.actualizar_posicion(self.x + 45, self.y - 10)
                    else:
                        item_soltado.actualizar_posicion(self.x - 60, self.y - 10)
                    self.componente_agregar_objeto.agregar_objeto(item_soltado, mundo,True)