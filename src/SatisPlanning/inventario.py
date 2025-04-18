import pygame
import SatisPlanning.constantes as ct
from SatisPlanning.objeto import Objeto

class Inventario:
    def __init__(self):
        # Tamaño deseado para las imágenes en el inventario y la barra rápida
        self.tamanio_icono = (30, 30)  # Cambiado de icon_size a tamanio_icono

        # Inventario inicializado con bloques de tierra, piedra y pasto en la barra rápida
        self.items = [
            Objeto(0, 0, 30, 30, ct.TEXTURA_TIERRA, dinamico=False),  # Bloque de tierra
            Objeto(0, 0, 30, 30, ct.TEXTURA_PIEDRA, dinamico=False),  # Bloque de piedra
            Objeto(0, 0, 30, 30, ct.TEXTURA_PASTO, dinamico=False)    # Bloque de pasto
        ]
        self.categoria_actual = "Bloques"
        self.item_seleccionado = 0  # Inicializar con el primer slot seleccionado
        self.visible = False
        self.posicion = (ct.ANCHO - 220, 50)
        self.ancho = 200
        self.alto_item = 40
        self.margen = 5
        self.alto_categoria = 30

    def agregar_objeto(self, objeto):
        """
        Agrega un objeto al inventario.
        :param objeto: Instancia de la clase Objeto.
        """
        self.items.append(objeto)

    def obtener_item_actual(self):
        """
        Devuelve el objeto actualmente seleccionado.
        """
        if self.item_seleccionado is not None and self.item_seleccionado < len(self.items):
            return self.items[self.item_seleccionado]
        return None

    def dibujar(self, pantalla, fuente):
        """
        Dibuja el inventario y la barra rápida en la pantalla.
        """
        # Dibujar la barra rápida (siempre visible)
        self._dibujar_barra_rapida(pantalla, fuente)

        # Dibujar el inventario completo si está visible
        if not self.visible:
            return

        # Calcular altura total
        altura_total = len(self.items) * (self.alto_item + self.margen) + self.alto_categoria + 20

        # Fondo del inventario
        fondo = pygame.Surface((self.ancho, altura_total))
        fondo.set_alpha(220)
        fondo.fill((60, 60, 70))
        pantalla.blit(fondo, self.posicion)

        # Dibujar selector de categorías
        self._dibujar_categorias(pantalla, fuente)

        # Dibujar items
        y_pos = self.posicion[1] + self.alto_categoria + 10
        for index, item in enumerate(self.items):
            self._dibujar_item(pantalla, fuente, item, y_pos, index)
            y_pos += self.alto_item + self.margen

    def _dibujar_categorias(self, pantalla, fuente):
        x_pos = self.posicion[0]
        ancho_cat = self.ancho // len(ct.CATEGORIAS)
        
        for i, categoria in enumerate(ct.CATEGORIAS):
            color = (100, 100, 200) if categoria == self.categoria_actual else (70, 70, 80)
            pygame.draw.rect(pantalla, color, 
                           (x_pos + i * ancho_cat, self.posicion[1], ancho_cat, self.alto_categoria))
            
            texto = fuente.render(categoria, True, (255, 255, 255))
            texto_rect = texto.get_rect(center=(x_pos + i * ancho_cat + ancho_cat // 2, 
                                              self.posicion[1] + self.alto_categoria // 2))
            pantalla.blit(texto, texto_rect)

    def _dibujar_item(self, pantalla, fuente, item, y_pos, index):
        """
        Dibuja un item individual del inventario.
        :param item: Instancia de la clase Objeto.
        :param y_pos: Posición Y para dibujar el item.
        :param index: Índice del item en la lista.
        """
        # Resaltar item seleccionado
        seleccionado = (self.item_seleccionado == index)
        if seleccionado:
            pygame.draw.rect(pantalla, (100, 100, 200), 
                           (self.posicion[0], y_pos, self.ancho, self.alto_item))
        
        # Dibujar icono del objeto
        pantalla.blit(item.imagen, (self.posicion[0] + 5, y_pos + 5))

        # Dibujar nombre del objeto
        texto = fuente.render(item.__class__.__name__, True, (255, 255, 255))
        pantalla.blit(texto, (self.posicion[0] + 40, y_pos + 10))

    def seleccionar_barra_rapida(self, indice):
        """
        Selecciona un elemento de la barra rápida basado en el índice.
        :param indice: Índice del elemento en la barra rápida (0-8).
        """
        if 0 <= indice < 9:  # Asegurarse de que el índice esté dentro del rango de la barra rápida
            self.item_seleccionado = indice

    def _dibujar_barra_rapida(self, pantalla, fuente):
        """
        Dibuja la barra rápida en la parte inferior de la pantalla.
        """
        num_slots = 9  # Número fijo de slots en la barra rápida
        ancho_barra = num_slots * 50 + (num_slots - 1) * 5
        barra_x = (ct.ANCHO - ancho_barra) // 2
        barra_y = ct.ALTO - 60

        for i in range(num_slots):
            x = barra_x + i * 55
            y = barra_y

            # Dibujar fondo del slot
            pygame.draw.rect(pantalla, (60, 60, 70), (x, y, 50, 50))

            # Resaltar el item seleccionado
            if self.item_seleccionado == i:
                # Dibujar un contorno amarillo para el elemento seleccionado
                pygame.draw.rect(pantalla, (255, 255, 0), (x - 2, y - 2, 54, 54), 3)

            # Dibujar el icono del item si existe
            if i < len(self.items):
                item = self.items[i]
                pantalla.blit(item.imagen, (x + 10, y + 10))

    def manejar_evento(self, evento):
        """
        Maneja eventos relacionados con el inventario.
        """
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_e:
            self.visible = not self.visible
            return None  # No se devuelve ningún elemento

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_g:
            return self.soltar_item_seleccionado()  # Devolver el elemento soltado

        if not self.visible or evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return None  # No se devuelve ningún elemento

        mouse_x, mouse_y = evento.pos
        
        # Verificar clic en items
        y_pos = self.posicion[1] + self.alto_categoria + 10
        for index, item in enumerate(self.items):
            rect = pygame.Rect(
                self.posicion[0],
                y_pos,
                self.ancho,
                self.alto_item
            )
            if rect.collidepoint(mouse_x, mouse_y):
                self.item_seleccionado = index
                return None  # No se devuelve ningún elemento
            y_pos += self.alto_item + self.margen

    def soltar_item_seleccionado(self):
        """
        Elimina el elemento actualmente seleccionado de la barra rápida y lo devuelve.
        :return: El objeto eliminado o None si no hay un objeto seleccionado.
        """
        if self.item_seleccionado is not None and self.item_seleccionado < len(self.items):
            elemento_soltado = self.items.pop(self.item_seleccionado)  # Eliminar y guardar el elemento seleccionado
            # Ajustar el índice seleccionado si es necesario
            if self.item_seleccionado >= len(self.items):
                self.item_seleccionado = max(0, len(self.items) - 1)
            return elemento_soltado  # Devolver el elemento eliminado
        return None  # No hay elemento para soltar

#esta hecho a modo de pueba , pero en un futuro hay que definir como deseamos que sea nuestro inventario , hay que diseñar, y tener otra clase aparte que se relacione a esta para craftear, y agregar funciones para ordenar inventario a nuestro antojo y que la barra rapida no funcione como una pila, tambien poder generar stacks de elementos , los cuales el tamaño del stack es algo definido por el objeto en si y no por el inventario
