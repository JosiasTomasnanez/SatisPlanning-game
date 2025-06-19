import pygame
import SatisPlanning.constantes as ct

class VistaJuego:
    QUIT = pygame.QUIT  # Para que el presentador pueda comparar sin importar pygame

    def __init__(self, camara, pantalla):
        self.pantalla = pantalla
        self.camara = camara
        self.pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO))
        # Cargar y escalar la imagen del corazón solo una vez (más grande)
        self.corazon_img = pygame.image.load(ct.RUTA_CORAZON).convert_alpha()
        self.corazon_img = pygame.transform.scale(self.corazon_img, (48, 48))  # Tamaño más grande

    def dibujar(self, objetos, personaje,enemigos):
        self.camara.actualizar(personaje.x, personaje.y)
        self.pantalla.fill(ct.COLOR_FONDO)
        self.pantalla.fill(ct.COLORES[0])

        self.dibujar_objetos_mapa(objetos)
        self.dibujar_personaje_centrado(personaje)
        self.dibujar_inventario(personaje.obtener_inventario())
        self.dibujar_enemigos(enemigos, personaje)
        self.dibujar_display_vidas(personaje.display_vidas)  # NUEVO
        self.dibujar_arma_personaje(personaje)  # NUEVO

        pygame.display.flip()

    def dibujar_objetos_mapa(self, objetos):
        for objeto in objetos:
            objeto_x, objeto_y = self.camara.aplicar(objeto.x, objeto.y)
            objeto.dibujar_con_desplazamiento(self.pantalla, objeto_x, objeto_y)

    def dibujar_personaje_centrado(self, personaje):
        personaje_centrado_x = (self.camara.ancho_pantalla // 2) - (personaje.ancho // 2)
        personaje_centrado_y = (self.camara.alto_pantalla // 2) - (personaje.alto // 2)
        self.pantalla.blit(personaje.componente_animacion.imagen_actual, (personaje_centrado_x, personaje_centrado_y))
        # Efecto visual de ataque: mostrar sprite animado del arma si está atacando
        if getattr(personaje, "atacando", False):
            arma = getattr(personaje, "arma", None)
            if arma and hasattr(arma, "componente_animacion"):
                sprite_arma = arma.componente_animacion.imagen_actual
            elif arma and hasattr(arma, "imagen"):
                sprite_arma = arma.imagen
            else:
                sprite_arma = None

            if sprite_arma:
                ataque_ancho = arma.ancho
                ataque_alto = arma.alto
                mitad_pj_x = personaje_centrado_x + personaje.ancho // 2
                if personaje.direccion == 1:
                    ataque_x = mitad_pj_x
                else:
                    ataque_x = mitad_pj_x - ataque_ancho
                ataque_y = personaje_centrado_y + (personaje.alto - ataque_alto) // 2
                self.pantalla.blit(sprite_arma, (ataque_x, ataque_y))

    def dibujar_enemigos(self, enemigos, personaje):
        # Dibuja cada enemigo en pantalla, evitando que aparezcan demasiado cerca del personaje jugador
        for enemigo in enemigos:
            # Calcular posición en pantalla del enemigo según la cámara
            enemigo_x, enemigo_y = self.camara.aplicar(enemigo.x, enemigo.y)
            # Desplazar la imagen algunos píxeles hacia arriba para alinear con la hitbox
            enemigo_y -= 20  # Ajusta este valor según lo que necesites
            enemigo_x -= 20
            # Calcular distancia al personaje jugador (centrado en pantalla)
            pj_centro_x = (self.camara.ancho_pantalla // 2)
            pj_centro_y = (self.camara.alto_pantalla // 2)
            dist = ((enemigo_x - pj_centro_x) ** 2 + (enemigo_y - pj_centro_y) ** 2) ** 0.5
            # if dist < 100:  # Si está muy cerca, lo desplazamos más lejos
            #     # Desplazar enemigo a la derecha o izquierda según su posición relativa
            #     if enemigo_x < pj_centro_x:
            #         enemigo_x = pj_centro_x - 120
            #     else:
            #         enemigo_x = pj_centro_x + 120
            self.pantalla.blit(enemigo.componente_animacion.imagen_actual, (enemigo_x, enemigo_y))

    def dibujar_inventario(self, inventario):
        fuente = pygame.font.SysFont("Arial", 20)
        fuente_cantidad = pygame.font.SysFont("Arial", 14, bold=True)
        # Dibuja la barra rápida
        self._dibujar_barra_rapida(inventario, fuente)
        # Dibuja el inventario completo si está visible
        if not getattr(inventario, "visible", False):
            return
        fondo = pygame.Surface((inventario.ancho, inventario.altura_total))
        fondo.set_alpha(200)
        fondo.fill((40, 40, 50))

        posicion_fondo = (
            inventario.posicion[0] - inventario.margen,
            inventario.posicion[1] - inventario.margen
        )
        self.pantalla.blit(fondo, posicion_fondo)

        filas = inventario.tamanio_filas
        columnas = inventario.tamanio_col
        tamanio_icono = inventario.tamanio_icono
        margen = 4

        for i in range(filas):
            for j in range(columnas):
                grupo = inventario.matrix[i][j]
                pos_x = inventario.posicion[0] + j * (tamanio_icono[0] + margen)
                pos_y = inventario.posicion[1] + i * (tamanio_icono[1] + margen)

                if grupo:  # si hay al menos un item en esa celda
                    item = grupo[0]
                    self._dibujar_icono_item(item, pos_x, pos_y, inventario)

                    # Dibujar la cantidad de objetos con efecto 3D
                    cantidad = len(grupo)
                    texto_str = str(cantidad)

                    # Sombra (negra, desplazada)
                    sombra = fuente_cantidad.render(texto_str, True, (0, 0, 0))
                    rect_sombra = sombra.get_rect(topright=(pos_x + tamanio_icono[0] - 1, pos_y + 3))
                    self.pantalla.blit(sombra, rect_sombra)

                    # Texto principal (amarillo)
                    texto = fuente_cantidad.render(texto_str, True, (255, 255, 0))
                    rect_texto = texto.get_rect(topright=(pos_x + tamanio_icono[0] - 2, pos_y + 2))
                    self.pantalla.blit(texto, rect_texto)

                # Dibujar selección actual
                if (i, j) == inventario.posicion_inventario_actual:
                    ancho = inventario.tamanio_icono[0] + 4
                    alto = inventario.tamanio_icono[1] + 4
                    pygame.draw.rect(self.pantalla, (255, 255, 0), (pos_x - 2, pos_y - 2, ancho, alto), 3)

    def _dibujar_icono_item(self, item, x, y, inventario):
        # Redimensiona el ítem para el inventario SIEMPRE al tamaño del icono
        imagen_redimensionada = pygame.transform.scale(item.imagen, inventario.tamanio_icono)
        self.pantalla.blit(imagen_redimensionada, (x, y))

    def _dibujar_categorias(self, inventario, fuente):
        x_pos = inventario.posicion[0]
        ancho_cat = inventario.ancho // len(ct.CATEGORIAS)
        for i, categoria in enumerate(ct.CATEGORIAS):
            color = (100, 100, 200) if categoria == inventario.categoria_actual else (70, 70, 80)
            pygame.draw.rect(self.pantalla, color, (x_pos + i * ancho_cat, inventario.posicion[1], ancho_cat, inventario.alto_categoria))
            texto = fuente.render(categoria, True, (255, 255, 255))
            texto_rect = texto.get_rect(center=(x_pos + i * ancho_cat + ancho_cat // 2, inventario.posicion[1] + inventario.alto_categoria // 2))
            self.pantalla.blit(texto, texto_rect)

    def _dibujar_item(self, inventario, fuente, item, y_pos, index):
        seleccionado = (inventario.item_seleccionado_barra == index)
        if seleccionado:
            pygame.draw.rect(self.pantalla, (100, 100, 200), (inventario.posicion[0], y_pos, inventario.ancho, inventario.alto_item))
        self.pantalla.blit(item.imagen, (inventario.posicion[0] + 5, y_pos + 5))
        texto = fuente.render(item.__class__.__name__, True, (255, 255, 255))
        self.pantalla.blit(texto, (inventario.posicion[0] + 40, y_pos + 10))        

    def _dibujar_barra_rapida(self, inventario, fuente):
        fuente_cantidad = pygame.font.SysFont("Arial", 14, bold=True)
        barra_x = inventario.posicion_barra[0]
        barra_y = inventario.posicion_barra[1]

        for i in range(inventario.num_slots_barra):
            x = barra_x + i * 55
            y = barra_y
            pygame.draw.rect(self.pantalla, (60, 60, 70), (x, y, 50, 50))

            if inventario.item_seleccionado_barra == i:
                pygame.draw.rect(self.pantalla, (255, 255, 0), (x - 2, y - 2, 54, 54), 3)

            if i >= 0 and i < len(inventario.barra_rapida) and inventario.barra_rapida[i]:
                grupo = inventario.barra_rapida[i]
                item = grupo[0]
                # Dibuja el ítem de la barra rápida SIEMPRE redimensionado al tamaño del icono
                imagen_redimensionada = pygame.transform.scale(item.imagen, inventario.tamanio_icono)
                self.pantalla.blit(imagen_redimensionada, (x + 10, y + 10))

                # Mostrar cantidad si hay más de uno
                cantidad = len(grupo)
                if cantidad > 1:
                    texto_str = str(cantidad)

                    # Sombra
                    sombra = fuente_cantidad.render(texto_str, True, (0, 0, 0))
                    rect_sombra = sombra.get_rect(topright=(x + 48, y + 3))
                    self.pantalla.blit(sombra, rect_sombra)

                    # Texto principal
                    texto = fuente_cantidad.render(texto_str, True, (255, 255, 0))
                    rect_texto = texto.get_rect(topright=(x + 47, y + 2))
                    self.pantalla.blit(texto, rect_texto)
                
    def dibujar_display_vidas(self, display_vidas):
        """
        Dibuja los corazones de vida en la pantalla (alineados a la derecha, más grandes).
        """
        corazon_ancho = self.corazon_img.get_width()
        corazon_espaciado = 52  # Espaciado entre corazones
        total_ancho = display_vidas.corazones * corazon_espaciado
        x_inicio = self.pantalla.get_width() - total_ancho - 20  # 20px de margen derecho
        y = 10
        for i in range(display_vidas.corazones):
            self.pantalla.blit(self.corazon_img, (x_inicio + i * corazon_espaciado, y))

    def dibujar_arma_personaje(self, personaje):
        """
        Dibuja el arma equipada del personaje en la pantalla.
        """
        if personaje.arma and hasattr(personaje.arma, "imagen"):
            self.pantalla.blit(personaje.arma.imagen, (20, 20))
            fuente = pygame.font.SysFont("Arial", 18, bold=True)
            texto = fuente.render(personaje.arma.__class__.__name__, True, (255, 255, 255))
            self.pantalla.blit(texto, (25 + personaje.arma.ancho, 25))

    def obtener_eventos(self):
        """
        Captura los eventos de pygame y los retorna.
        """
        return pygame.event.get()
