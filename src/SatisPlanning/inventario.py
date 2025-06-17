import pygame
import SatisPlanning.constantes as ct
from .entidades.objeto import Objeto

class Inventario:
    def __init__(self):
        # Tamaño deseado para las imágenes en el inventario y la barra rápida
        self.tamanio_icono = (30, 30)  # Cambiado de icon_size a tamanio_icono

        # Inventario inicializado con bloques de tierra, piedra y pasto en la barra rápida
        self.items = [
            Objeto(0, 0, 30, 30, ct.TEXTURA_TIERRA, dinamico=False,tangible=True),  # Bloque de tierra
            Objeto(0, 0, 30, 30, ct.TEXTURA_PIEDRA, dinamico=False, tangible=True),  # Bloque de piedra
            Objeto(0, 0, 30, 30, ct.TEXTURA_PASTO, dinamico=False,tangible=True)    # Bloque de pasto
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

    def seleccionar_barra_rapida(self, indice):
        """
        Selecciona un elemento de la barra rápida basado en el índice.
        :param indice: Índice del elemento en la barra rápida (0-8).
        """
        if 0 <= indice < 9:  # Asegurarse de que el índice esté dentro del rango de la barra rápida
            self.item_seleccionado = indice

  
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
