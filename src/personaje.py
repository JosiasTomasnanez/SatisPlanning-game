import pygame
from Objeto import Objeto
import constantes as ct
from inventario import Inventario  # Import the Inventario class

class Personaje(Objeto):
    def __init__(self, x, y, width, height):
        # Inicializar con el sprite p3 como predeterminado
        super().__init__(x, y, width, height, "assets/p3.png", dinamico=True)
        self.vel_x = self.vel_y = 0
        self.en_el_suelo = False
        self.direccion = 1  # 1 para derecha, -1 para izquierda

        # Cargar los sprites del personaje
        self.sprites = [
            pygame.image.load(f"assets/p{i}.png") for i in range(1, 8)
        ]
        self.sprites = [pygame.transform.scale(sprite, (width, height)) for sprite in self.sprites]
        self.sprite_actual = 2  # Índice del sprite inicial (p3)

        # Contador para animación
        self.contador_animacion = 0

        self.inventario = Inventario()  # Add an inventory to the character
        self.inventario.visible = False  # Start with the inventory hidden

    def mover(self, teclas, world):
        """
        Mueve el personaje basado en las teclas presionadas y verifica colisiones con el mundo.
        """
        # Movimiento horizontal
        self.vel_x = (teclas[pygame.K_d] - teclas[pygame.K_a]) * ct.VELOCIDAD_PERSONAJE
        nueva_hitbox = self.hitbox.move(self.vel_x, 0)  # Nueva posición horizontal
        if not world.colisiona(nueva_hitbox):  # Verificar colisión horizontal
            self.hitbox = nueva_hitbox

        # Actualizar la dirección del personaje
        if self.vel_x > 0:
            self.direccion = 1  # Derecha
        elif self.vel_x < 0:
            self.direccion = -1  # Izquierda

        # Gravedad y salto
        if not self.en_el_suelo:
            self.vel_y += ct.GRAVEDAD  # Aplicar gravedad si no está en el suelo
        if (teclas[pygame.K_w] or teclas[pygame.K_SPACE]) and self.en_el_suelo:
            self.vel_y = -ct.FUERZA_SALTO  # Aplicar fuerza de salto
            self.en_el_suelo = False  # Ya no está en el suelo después de saltar

        # Movimiento vertical
        nueva_hitbox = self.hitbox.move(0, self.vel_y)  # Nueva posición vertical
        if not world.colisiona(nueva_hitbox):  # Verificar colisión vertical
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

    def _actualizar_animacion(self):
        """
        Actualiza el sprite del personaje para animar el movimiento.
        """
        self.contador_animacion += 1
        if self.contador_animacion >= 10:  # Cambiar sprite cada 10 frames (más lento)
            self.sprite_actual = (self.sprite_actual + 1) % len(self.sprites)
            self.contador_animacion = 0

        # Actualizar la imagen del sprite actual según la dirección
        self.image = self.sprites[self.sprite_actual]
        if self.direccion == -1:  # Si va a la izquierda, voltear horizontalmente
            self.image = pygame.transform.flip(self.image, True, False)

    def notificar_colision(self, objeto):
        """
        Maneja la colisión con un objeto estático, diferenciando entre colisiones horizontales y verticales.
        """
        # Determinar si la colisión es horizontal o vertical
        colision_horizontal = (
            self.hitbox.right > objeto.hitbox.left and self.hitbox.left < objeto.hitbox.right
        )
        colision_vertical = (
            self.hitbox.bottom > objeto.hitbox.top and self.hitbox.top < objeto.hitbox.bottom
        )

        # Manejar colisión vertical
        if colision_vertical:
            if self.vel_y > 0:  # Cayendo
                self.vel_y = 0  # Detener movimiento vertical
                self.en_el_suelo = True  # Ahora está en el suelo
                self.y = objeto.hitbox.top - self.height  # Ajustar posición para estar justo encima del objeto
            elif self.vel_y < 0:  # Saltando
                self.vel_y = 0  # Detener movimiento vertical
                self.y = objeto.hitbox.bottom  # Ajustar posición para estar justo debajo del objeto

        # Manejar colisión horizontal
        if colision_horizontal:
            if self.vel_x > 0:  # Moviéndose a la derecha
                self.vel_x = 0  # Detener movimiento horizontal
                self.x = objeto.hitbox.left - self.width  # Ajustar posición para estar justo a la izquierda del objeto
            elif self.vel_x < 0:  # Moviéndose a la izquierda
                self.vel_x = 0  # Detener movimiento horizontal
                self.x = objeto.hitbox.right  # Ajustar posición para estar justo a la derecha del objeto

        # Actualizar la hitbox
        self.hitbox.topleft = (self.x, self.y)

    def manejar_evento(self, evento, mundo):
        """
        Maneja eventos relacionados con el personaje, como abrir/cerrar el inventario y seleccionar elementos de la hotbar.
        """
        if evento.type == pygame.KEYDOWN:
            # Alternar la visibilidad del inventario con la tecla "I"
            if evento.key == pygame.K_i:
                self.inventario.visible = not self.inventario.visible

            # Seleccionar elementos de la hotbar con las teclas del 1 al 9
            if pygame.K_1 <= evento.key <= pygame.K_9:
                indice_hotbar = evento.key - pygame.K_1  # Convertir la tecla en índice (0-8)
                self.inventario.seleccionar_hotbar(indice_hotbar)

            # Soltar el elemento seleccionado con la tecla "G"
            if evento.key == pygame.K_g:
                item_soltado = self.inventario.soltar_item_seleccionado()  # Obtener el elemento soltado
                if item_soltado:
                    # Actualizar la posición del objeto soltado a la posición del personaje (20 píxeles más arriba)
                    item_soltado.update_position(self.x, self.y - 10)
                    mundo.agregar_objeto(item_soltado)  # Agregar el objeto al mundo

    def update(self, teclas, world):
        """
        Actualiza el estado del personaje, manejando movimiento.
        """
        # Manejar movimiento
        self.mover(teclas, world)

    def draw(self, pantalla, font, camera):
        """
        Dibuja el personaje y delega el dibujo del inventario y hotbar al inventario.
        """
        # Calcular la posición centrada del personaje
        personaje_centrado_x = (camera.screen_width // 2) - (self.width // 2)
        personaje_centrado_y = (camera.screen_height // 2) - (self.height // 2)

        # Dibujar el personaje centrado
        pantalla.blit(self.image, (personaje_centrado_x, personaje_centrado_y))

        # Delegar el dibujo del inventario y hotbar al inventario
        self.inventario.draw(pantalla, font)



