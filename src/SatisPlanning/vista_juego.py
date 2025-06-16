import pygame
import SatisPlanning.constantes as ct

class VistaJuego:
    QUIT = pygame.QUIT  # Para que el presentador pueda comparar sin importar pygame

    def __init__(self, camara, pantalla):
        self.pantalla = pantalla
        self.camara = camara
        self.pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO))

    def dibujar(self, objetos, personaje,enemigos):
        self.camara.actualizar(personaje.x, personaje.y)
        self.pantalla.fill(ct.COLOR_FONDO)
        self.pantalla.fill(ct.COLORES[0])

        self.dibujar_objetos_mapa(objetos)
        self.dibujar_personaje_centrado(personaje)
        self.dibujar_inventario(personaje.obtener_inventario())
        self.dibujar_enemigos(enemigos, personaje)

        pygame.display.flip()

    def dibujar_objetos_mapa(self, objetos):
        for objeto in objetos:
            objeto_x, objeto_y = self.camara.aplicar(objeto.x, objeto.y)
            objeto.dibujar_con_desplazamiento(self.pantalla, objeto_x, objeto_y)

    def dibujar_personaje_centrado(self, personaje):
        personaje_centrado_x = (self.camara.ancho_pantalla // 2) - (personaje.ancho // 2)
        personaje_centrado_y = (self.camara.alto_pantalla // 2) - (personaje.alto // 2)
        self.pantalla.blit(personaje.componente_animacion.imagen_actual, (personaje_centrado_x, personaje_centrado_y))
    
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
        # Dibuja la barra rápida
        self._dibujar_barra_rapida(inventario, fuente)
        # Dibuja el inventario completo si está visible
        if not getattr(inventario, "visible", False):
            return
        altura_total = len(inventario.items) * (inventario.alto_item + inventario.margen) + inventario.alto_categoria + 20
        fondo = pygame.Surface((inventario.ancho, altura_total))
        fondo.set_alpha(220)
        fondo.fill((60, 60, 70))
        self.pantalla.blit(fondo, inventario.posicion)
        self._dibujar_categorias(inventario, fuente)
        y_pos = inventario.posicion[1] + inventario.alto_categoria + 10
        for index, item in enumerate(inventario.items):
            self._dibujar_item(inventario, fuente, item, y_pos, index)
            y_pos += inventario.alto_item + inventario.margen

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
        seleccionado = (inventario.item_seleccionado == index)
        if seleccionado:
            pygame.draw.rect(self.pantalla, (100, 100, 200), (inventario.posicion[0], y_pos, inventario.ancho, inventario.alto_item))
        self.pantalla.blit(item.imagen, (inventario.posicion[0] + 5, y_pos + 5))
        texto = fuente.render(item.__class__.__name__, True, (255, 255, 255))
        self.pantalla.blit(texto, (inventario.posicion[0] + 40, y_pos + 10))

    def _dibujar_barra_rapida(self, inventario, fuente):
        num_slots = 9
        ancho_barra = num_slots * 50 + (num_slots - 1) * 5
        barra_x = (ct.ANCHO - ancho_barra) // 2
        barra_y = ct.ALTO - 60
        for i in range(num_slots):
            x = barra_x + i * 55
            y = barra_y
            pygame.draw.rect(self.pantalla, (60, 60, 70), (x, y, 50, 50))
            if inventario.item_seleccionado == i:
                pygame.draw.rect(self.pantalla, (255, 255, 0), (x - 2, y - 2, 54, 54), 3)
            if i < len(inventario.items):
                item = inventario.items[i]
                self.pantalla.blit(item.imagen, (x + 10, y + 10))

    def obtener_eventos(self):
        """
        Captura los eventos de pygame y los retorna.
        """
        return pygame.event.get()
