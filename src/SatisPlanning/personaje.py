import pygame
from SatisPlanning.objeto import Objeto
import SatisPlanning.constantes as ct
from SatisPlanning.inventario import Inventario
from SatisPlanning.camara import Camara
from SatisPlanning.utilidades import obtener_ruta_asset
from SatisPlanning.componente_mover import ComponenteMover
from SatisPlanning.componente_animacion import ComponenteAnimacion
from SatisPlanning.componente_agregar_objeto import ComponenteAgregarObjeto

class Personaje(Objeto):
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el personaje con posición, sprites y un inventario.

        :param x: Posición X inicial.
        :param y: Posición Y inicial.
        :param ancho: Ancho del personaje.
        :param alto: Altura del personaje.
        """
        super().__init__(x, y, ancho, alto, obtener_ruta_asset("p3.png"), dinamico=True, tangible=True)
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = 1  # 1 para derecha, -1 para izquierda

        # Cargar los sprites del personaje
        self.sprites = [
            pygame.image.load(obtener_ruta_asset(f"p{i}.png")) for i in range(1, 8)
        ]
        self.sprites = [pygame.transform.scale(sprite, (ancho, alto)) for sprite in self.sprites]

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

    def actualizar(self, teclas, mundo):
        """
        Actualiza el estado del personaje, delegando el movimiento y la animación a los componentes.
        """
        self.componente_mover.actualizar(teclas, mundo)
        self.componente_animacion.actualizar()

    def dibujar(self, pantalla, fuente, camara):
        """
        Dibuja el personaje y delega el dibujo del inventario y barra rápida al inventario.
        """
        personaje_centrado_x = (camara.ancho_pantalla // 2) - (self.ancho // 2)
        personaje_centrado_y = (camara.alto_pantalla // 2) - (self.alto // 2)

        pantalla.blit(self.componente_animacion.imagen_actual, (personaje_centrado_x, personaje_centrado_y))
        self.inventario.dibujar(pantalla, fuente)

#el manejo de coliciones y manejo de movimientos o ataques o demas, estaria bueno hacerlo como compoonentes , como usando el patron stratagy,  ya que hay muchos objetos u personajes que van a tener las mismas fisicas de movimiento pero con variables como la gravedad , entre otras diferentes, entonces seria hacer clases que se encarguen de dichos comportamientos, de las cuales los objetos puedan o no hacer uso, mandandole sus caracteristicas, y queda mucho mas modular y extendible el codigo


