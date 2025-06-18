import pygame
import SatisPlanning.constantes as ct

class VistaJuego:
    def __init__(self, camara, pantalla):
        self.pantalla = pantalla
        self.camara = camara
        self.pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO))

    def dibujar(self, objetos, personaje):
        self.camara.actualizar(personaje.x, personaje.y)
        self.pantalla.fill(ct.COLOR_FONDO)
        self.pantalla.fill(ct.COLORES[0])

        self.dibujar_objetos_mapa(objetos)
        self.dibujar_personaje_centrado(personaje)
        self.dibujar_inventario(personaje.obtener_inventario())

        pygame.display.flip()

    def dibujar_objetos_mapa(self, objetos):
        for objeto in objetos:
            objeto_x, objeto_y = self.camara.aplicar(objeto.x, objeto.y)
            objeto.dibujar_con_desplazamiento(self.pantalla, objeto_x, objeto_y)

    def dibujar_personaje_centrado(self, personaje):
        personaje_centrado_x = (self.camara.ancho_pantalla // 2) - (personaje.ancho // 2)
        personaje_centrado_y = (self.camara.alto_pantalla // 2) - (personaje.alto // 2)
        self.pantalla.blit(personaje.componente_animacion.imagen_actual, (personaje_centrado_x, personaje_centrado_y))

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
        imagen_redimensionada = pygame.transform.scale(item.imagen, inventario.tamanio_icono)
        self.pantalla.blit(imagen_redimensionada, (x, y))
         
    #eliminar _dibujar_item si ya no hace falta
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
                self.pantalla.blit(item.imagen, (x + 10, y + 10))
                
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
