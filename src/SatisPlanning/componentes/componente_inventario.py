from SatisPlanning.componentes.componente import Componente
import pygame
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
