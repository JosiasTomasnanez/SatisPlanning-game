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
                from SatisPlanning.entidades.suelo import Suelo
                if(self.inventario.visible):
                    item_soltado = self.inventario.soltar_item_seleccionado_matrix()
                else:
                    item_soltado = self.inventario.soltar_item_seleccionado_barra()
                # Solo permitir soltar si es de la clase Suelo
                if item_soltado and isinstance(item_soltado, Suelo):
                    # Usar atributos del propietario
                    if self.propietario.direccion == 1:
                        item_soltado.actualizar_posicion(self.propietario.x + 45, self.propietario.y - 10)
                    else:
                        item_soltado.actualizar_posicion(self.propietario.x - 60, self.propietario.y - 10)
                    # Ajustar posición en Y para evitar colisiones
                    while self.mundo.colisiona(item_soltado.hitbox, item_soltado):
                        item_soltado.actualizar_posicion(item_soltado.x, item_soltado.y - 1)
                    self.mundo.agregar_objeto(item_soltado, True)
                elif item_soltado:
                    # Si no es de tipo Suelo, lo devuelve al inventario
                    self.inventario.agregar_item(item_soltado)

            # NUEVO: Soltar cualquier objeto de forma NO tangible con la tecla Q
            if teclas.key == pygame.K_q:
                from SatisPlanning.entidades.arma import Arma
                # Si el inventario está visible, soltar desde la matriz, sino desde la barra rápida
                if(self.inventario.visible):
                    item_soltado = self.inventario.soltar_item_seleccionado_matrix()
                else:
                    item_soltado = self.inventario.soltar_item_seleccionado_barra()
                if item_soltado:
                    # Si es un arma, crea una copia visual pequeña para el mundo
                    if isinstance(item_soltado, Arma):
                        tipo_arma = type(item_soltado)
                        # Para Espada, respeta la firma de su __init__
                        if tipo_arma.__name__ == "Espada":
                            # Espada(x=..., y=..., ancho=30, alto=30, danio=..., sprites=...)
                            item_soltado = tipo_arma(
                                self.propietario.x, self.propietario.y,
                                30, 30,
                                getattr(item_soltado, "danio", 20),
                                getattr(item_soltado, "sprites", None)
                            )
                        else:
                            # Para otras armas, usa la firma genérica
                            item_soltado = tipo_arma(
                                self.propietario.x, self.propietario.y,
                                30, 30,
                                getattr(item_soltado, "danio", 20),
                                getattr(item_soltado, "ruta_final", None),
                                getattr(item_soltado, "sprites", None)
                            )
                    # Usar atributos del propietario
                    if self.propietario.direccion == 1:
                        item_soltado.actualizar_posicion(self.propietario.x + 45, self.propietario.y - 10)
                    else:
                        item_soltado.actualizar_posicion(self.propietario.x - 60, self.propietario.y - 10)
                    # Ajustar posición en Y para evitar colisiones
                    while self.mundo.colisiona(item_soltado.hitbox, item_soltado):
                        item_soltado.actualizar_posicion(item_soltado.x, item_soltado.y - 1)
                    # Soltar como NO tangible
                    self.mundo.agregar_objeto(item_soltado, False)

            # Consumir objeto with tecla E si es consumible
            if teclas.key == pygame.K_e:
                consumido = False
                personaje = self.propietario  # El propietario es el personaje
                if self.inventario.visible:
                    consumido = self.inventario.consumir_item_seleccionado_matrix(personaje)
                else:
                    consumido = self.inventario.consumir_item_seleccionado_barra(personaje)
                # Puedes agregar feedback visual o sonoro si consumido es True

            # Equipar/desequipar arma con la tecla R
            if teclas.key == pygame.K_r:
                from SatisPlanning.entidades.arma import Arma
                from SatisPlanning.entidades.mano import Mano
                # Selecciona el item actual según inventario visible o barra rápida
                if self.inventario.visible:
                    item = self.inventario.obtener_item_actual()
                else:
                    idx = self.inventario.item_seleccionado_barra
                    grupo = self.inventario.barra_rapida[idx] if 0 <= idx < len(self.inventario.barra_rapida) else []
                    item = grupo[0] if grupo else None

                if item and isinstance(item, Arma):
                    # Si ya está equipada esa arma, desequipar (volver a la mano y agregar arma al inventario)
                    if self.propietario.arma is item:
                        self.propietario.equipar_arma(Mano())
                        self.inventario.agregar_item(item)
                    else:
                        # Si hay otra arma equipada (no Mano), la devuelve al inventario antes de equipar la nueva
                        if isinstance(self.propietario.arma, Arma) and self.propietario.arma is not item and not isinstance(self.propietario.arma, Mano):
                            self.inventario.agregar_item(self.propietario.arma)
                        self.inventario.remover_item(item)
                        self.propietario.equipar_arma(item)
                elif item is None or not isinstance(item, Arma):
                    # Si no es arma, siempre vuelve a la mano
                    if isinstance(self.propietario.arma, Arma) and not isinstance(self.propietario.arma, Mano):
                        self.inventario.agregar_item(self.propietario.arma)
                    self.propietario.equipar_arma(Mano())

        if teclas.type == pygame.MOUSEBUTTONDOWN and teclas.button == 1 and self.inventario.visible:

            mouse_x, mouse_y = teclas.pos
            rect_matrix = rect = pygame.Rect(
                self.inventario.posicion[0],
                self.inventario.posicion[1],
                self.inventario.ancho,
                self.inventario.altura_total
            )
            if rect_matrix.collidepoint(mouse_x, mouse_y):
                self.click_item_matrix(mouse_x,mouse_y)
            #else:
                #debería revisar si hace click en la barra rapida
                
                
        
        

    def click_item_matrix(self, mouse_x, mouse_y):
        ancho_celda = self.inventario.ancho / self.inventario.tamanio_col
        alto_celda = self.inventario.altura_total / self.inventario.tamanio_filas

        columna = int((mouse_x - self.inventario.posicion[0]) / ancho_celda)
        fila = int((mouse_y - self.inventario.posicion[1]) / alto_celda)

        # Validamos que esté dentro del rango del inventario
        dentro_rango=0 <= fila < self.inventario.tamanio_filas and 0 <= columna < self.inventario.tamanio_col
        
        if dentro_rango and self.inventario.posicion_ocupada_cuadricula(fila,columna) :
            self.inventario.posicion_inventario_actual = (fila, columna)

    def click_item(self, mouse_y):
        inicio = self.inventario.posicion[1]+ self.inventario.alto_categoria + 10 
        fin = inicio + self.inventario.alto_item*len(self.inventario.items)
        if mouse_y > inicio and mouse_y < fin :
            y_item = math.floor((mouse_y-inicio)/self.inventario.alto_item)
            self.inventario.item_seleccionado = y_item


