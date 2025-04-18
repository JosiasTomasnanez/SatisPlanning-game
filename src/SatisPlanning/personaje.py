import pygame
from SatisPlanning.objeto import Objeto
import SatisPlanning.constantes as ct
from SatisPlanning.inventario import Inventario
from SatisPlanning.camara import Camara
from SatisPlanning.utilidades import obtener_ruta_asset

class Personaje(Objeto):
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el personaje con posición, sprites y un inventario.

        :param x: Posición X inicial.
        :param y: Posición Y inicial.
        :param ancho: Ancho del personaje.
        :param alto: Altura del personaje.
        """
        super().__init__(x, y, ancho, alto, obtener_ruta_asset("p3.png"), dinamico=True)
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = 1  # 1 para derecha, -1 para izquierda

        # Cargar los sprites del personaje
        self.sprites = [
            pygame.image.load(obtener_ruta_asset(f"p{i}.png")) for i in range(1, 8)
        ]
        self.sprites = [pygame.transform.scale(sprite, (ancho, alto)) for sprite in self.sprites]
        self.sprite_actual = 2  # Índice del sprite inicial (p3)

        # Contador para animación
        self.contador_animacion = 0

        # Inventario del personaje
        self.inventario = Inventario()
        self.inventario.visible = False

    def mover(self, teclas, mundo):
        """
        Mueve el personaje basado en las teclas presionadas y verifica colisiones con el mundo.
        """
        # Movimiento horizontal
        self.vel_x = (teclas[pygame.K_d] - teclas[pygame.K_a]) * ct.VELOCIDAD_PERSONAJE
        nueva_hitbox = self.hitbox.move(self.vel_x, 0)
        if not mundo.colisiona(nueva_hitbox):
            self.hitbox = nueva_hitbox

        # Actualizar la dirección del personaje
        if self.vel_x > 0:
            self.direccion = 1
        elif self.vel_x < 0:
            self.direccion = -1

        # Gravedad y salto
        if not self.en_el_suelo:
            self.vel_y += ct.GRAVEDAD
        if (teclas[pygame.K_w] or teclas[pygame.K_SPACE]) and self.en_el_suelo:
            self.vel_y = -ct.FUERZA_SALTO
            self.en_el_suelo = False

        # Movimiento vertical
        nueva_hitbox = self.hitbox.move(0, self.vel_y)
        if not mundo.colisiona(nueva_hitbox):
            self.hitbox = nueva_hitbox
            self.en_el_suelo = False
        else:
            self.vel_y = 0
            self.en_el_suelo = True

        # Actualizar la posición del personaje
        self.x, self.y = self.hitbox.topleft

        # Actualizar la animación si el personaje se mueve
        if self.vel_x != 0:
            self._actualizar_animacion()
        """IMPORTANTE:no deberiamos usar la constante gravedad, ni fuerza, sino que pueda
        ser variables modificables desde otras clases, por ejemplo desde una pocion""" 
        
    def _actualizar_animacion(self):
        """
        Actualiza el sprite del personaje para animar el movimiento.
        """
        self.contador_animacion += 1
        if self.contador_animacion >= 10:
            self.sprite_actual = (self.sprite_actual + 1) % len(self.sprites)
            self.contador_animacion = 0

        # Actualizar la imagen del sprite actual según la dirección
        self.imagen = self.sprites[self.sprite_actual]
        if self.direccion == -1:
            self.imagen = pygame.transform.flip(self.imagen, True, False)

    def notificar_colision(self, objeto):
        """
        Maneja la colisión con un objeto estático, diferenciando entre colisiones horizontales y verticales.
        """
        colision_horizontal = (
            self.hitbox.right > objeto.hitbox.left and self.hitbox.left < objeto.hitbox.right
        )
        colision_vertical = (
            self.hitbox.bottom > objeto.hitbox.top and self.hitbox.top < objeto.hitbox.bottom
        )

        # Manejar colisión vertical
        if colision_vertical:
            if self.vel_y > 0:
                self.vel_y = 0
                self.en_el_suelo = True
                self.y = objeto.hitbox.top - self.alto
            elif self.vel_y < 0:
                self.vel_y = 0
                self.y = objeto.hitbox.bottom

        # Manejar colisión horizontal
        if colision_horizontal:
            if self.vel_x > 0:
                self.vel_x = 0
                self.x = objeto.hitbox.left - self.ancho
            elif self.vel_x < 0:
                self.vel_x = 0
                self.x = objeto.hitbox.right

        self.hitbox.topleft = (self.x, self.y)

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
                    item_soltado.actualizar_posicion(self.x, self.y - 10)
                    mundo.agregar_objeto(item_soltado)

    def actualizar(self, teclas, mundo):
        """
        Actualiza el estado del personaje, manejando movimiento y colisiones.
        """
        self.mover(teclas, mundo)

    def dibujar(self, pantalla, fuente, camara):
        """
        Dibuja el personaje y delega el dibujo del inventario y barra rápida al inventario.
        """
        personaje_centrado_x = (camara.ancho_pantalla // 2) - (self.ancho // 2)
        personaje_centrado_y = (camara.alto_pantalla // 2) - (self.alto // 2)

        pantalla.blit(self.imagen, (personaje_centrado_x, personaje_centrado_y))
        self.inventario.dibujar(pantalla, fuente)

#el manejo de coliciones y manejo de movimientos o ataques o demas, estaria bueno hacerlo como compoonentes , como usando el patron stratagy,  ya que hay muchos objetos u personajes que van a tener las mismas fisicas de movimiento pero con variables como la gravedad , entre otras diferentes, entonces seria hacer clases que se encarguen de dichos comportamientos, de las cuales los objetos puedan o no hacer uso, mandandole sus caracteristicas, y queda mucho mas modular y extendible el codigo


