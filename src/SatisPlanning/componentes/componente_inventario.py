from SatisPlanning.componentes.componente import Componente
import SatisPlanning.constantes as ct 
import pygame
import math
# Este componente actúa como interfaz entre el personaje (o quien use el inventario)
# y el inventario en sí. Recibe eventos y modifica el estado del inventario según corresponda.
class ComponenteInventario(Componente):
    def __init__(self, propietario, inventario):
        super().__init__(propietario)
        self.inventario = inventario
        self.inventario.visible = False

    def set_mundo(self, mundo):
        self.mundo = mundo
        
    def actualizar(self, teclas):

        if teclas.type == pygame.KEYDOWN:
            if teclas.key == pygame.K_i:
                self.inventario.visible = not self.inventario.visible

            if pygame.K_1 <= teclas.key <= pygame.K_9:
                indice_barra = teclas.key - pygame.K_1
                self.inventario.seleccionar_barra_rapida(indice_barra)

            if teclas.key == pygame.K_g:
                item_soltado = self.inventario.soltar_item_seleccionado()
                if item_soltado:
                    # Usar atributos del propietario
                    if self.propietario.direccion == 1:
                        item_soltado.actualizar_posicion(self.propietario.x + 45, self.propietario.y - 10)
                    else:
                        item_soltado.actualizar_posicion(self.propietario.x - 60, self.propietario.y - 10)
                    # Ajustar posición en Y para evitar colisiones
                    while self.mundo.colisiona(item_soltado.hitbox,item_soltado):
                        item_soltado.actualizar_posicion(item_soltado.x, item_soltado.y - 1)
                    self.mundo.agregar_objeto(item_soltado, True)
            
        if teclas.type == pygame.MOUSEBUTTONDOWN and self.inventario.visible:

            mouse_x, mouse_y = teclas.pos
            rect_cat = rect = pygame.Rect(
                self.inventario.posicion[0],
                self.inventario.posicion[1],
                self.inventario.ancho,
                self.inventario.alto_categoria
            )
            if rect_cat.collidepoint(mouse_x, mouse_y):
                self.click_categoria(mouse_x)
            else:
                
                rect_items = rect = pygame.Rect(
                    self.inventario.posicion[0],
                    self.inventario.posicion[1] + self.inventario.alto_categoria + 10,
                    self.inventario.ancho,
                    (self.inventario.alto_item)*len(self.inventario.items)
                )
                if rect_items.collidepoint(mouse_x, mouse_y):
                    self.click_item(mouse_y)
            

        
        
         
        

    def click_categoria(self, mouse_x):
        if mouse_x >self.inventario.posicion[0] and mouse_x < self.inventario.ancho +self.inventario.posicion[0]:
            x_item=math.floor(((mouse_x-self.inventario.posicion[0])*len(ct.CATEGORIAS))/self.inventario.ancho)
            self.inventario.categoria_actual=ct.CATEGORIAS[x_item]



    def click_item(self, mouse_y):
        inicio = self.inventario.posicion[1]+ self.inventario.alto_categoria + 10 
        fin = inicio + self.inventario.alto_item*len(self.inventario.items)
        if mouse_y > inicio and mouse_y < fin :
            y_item = math.floor((mouse_y-inicio)/self.inventario.alto_item)
            self.inventario.item_seleccionado = y_item
                      

