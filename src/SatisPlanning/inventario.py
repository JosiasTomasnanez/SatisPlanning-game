import pygame
import SatisPlanning.constantes as ct
from .entidades.objeto import Objeto

class Inventario:
    def __init__(self):
        # Tamaño deseado para las imágenes en el inventario y la barra rápida
        self.posicion_inventario_actual= (1,1) 
        self.tamanio_filas=10
        self.tamanio_col=6
        self.tamanio_icono = (30, 30)  # Cambiado de icon_size a tamanio_icono
        self.textura_vacia=""
        self.num_slots_barra=9
        self.item_seleccionado_barra=0
        
        # Inventario inicializado con bloques de tierra, piedra y pasto en la barra rápida
        
        self.matrix = [[[] for _ in range(self.tamanio_col)] for _ in range(self.tamanio_filas)] 
        self.barra_rapida = [[] for _ in range(self.num_slots_barra)]  
        self.visible = False
        self.posicion = (ct.ANCHO - 220, 50)
        self.alto_item = 40
        self.margen = 5
        self.ancho = (self.tamanio_icono[0] + self.margen)*self.tamanio_col
        self.altura_total =  (self.tamanio_icono[0] + self.margen)*self.tamanio_filas-4
        
        #caracteristicas de la barra rapida
        
        ancho_barra = self.num_slots_barra * 50 + (self.num_slots_barra - 1) * 5 
        barra_x = (ct.ANCHO - ancho_barra) // 2
        barra_y = ct.ALTO - 60
        self.posicion_barra=(barra_x,barra_y)

        #inicializar inventario
        for i in range(5):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_POCIONES[0], dinamico=False,tangible=True))
        for i in range(3):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_POCIONES[1], dinamico=False, tangible=True))
        for i in range(4):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_POCIONES[2], dinamico=False,tangible=True))
        for i in range(7):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_POCIONES[3], dinamico=False,tangible=True))
        for i in range(8):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_POCIONES[4], dinamico=False,tangible=True))
        for i in range(11):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_MINERALES[0], dinamico=False,tangible=True))
        for i in range(2):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_MINERALES[1], dinamico=False,tangible=True))
        for i in range(6):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_MINERALES[2], dinamico=False, tangible=True))
        for i in range(12):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_MINERALES[3], dinamico=False,tangible=True))
        for i in range(2):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_MINERALES[4], dinamico=False,tangible=True))
        for i in range(3):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_MINERALES[5], dinamico=False,tangible=True))
        for i in range(7):
            self.agregar_item(Objeto(0, 0, 30, 30, ct.ITEM_MINERALES[6], dinamico=False,tangible=True))
        
        self.asignar_item_a_barra_rapida(0, 0, 0)  # Asignar el primer item a la barra rápida
        self.asignar_item_a_barra_rapida(1, 1, 2)
        self.asignar_item_a_barra_rapida(2, 0, 2) 
        self.asignar_item_a_barra_rapida(3, 1, 3)  
        self.asignar_item_a_barra_rapida(4, 0, 1) 
          

    def  cantidad_items_posicion(self, x, y):
        if self._posicion_ocupada_cuadricula(x,y):
            return len(self.matrix[x][y])
        return   0
    
    def existeItemEnPosicion(self,x,y, objeto):
        #devuelve verdadero si en la posición x,y hay una referencia al objeto pasado por parámetro
        if not self._posicion_ocupada_cuadricula(x,y):
            return False
        if any(elem is objeto for elem in self.matrix[x][y]):
            return True
        return False
    
    def itemsMismoTipoEnPosicion(self,x,y, objeto):
        #devuelve true si en la posición hay items del mismo tipo que el pasado por parametro
        if not self._posicion_ocupada_cuadricula(x,y):
            return False
        return objeto.tipo_igual(self.matrix[x][y][0])
    
    def existeTipoItemInventario(self,objeto):
        #devuelve true si en el inventario existen items del mismo tipo que el pasado por parámetro
        encontrado = False
        i = 0
        while not encontrado and i < self.tamanio_filas:
            j = 0
            while not encontrado and j < self.tamanio_col:
                for obj in self.matrix[i][j]:
                    if obj.tipo_igual(objeto):  # obj es buscado para comparar referencia
                        encontrado = True
                        break
                j += 1
            i += 1
        return encontrado 
    
    def agregar_item(self,objeto):
        coincide_tipo=False
        pos_i = pos_j = -1
        i=0
        while not coincide_tipo and i < self.tamanio_filas:
            j = 0
            while not coincide_tipo and j < self.tamanio_col:
                for obj in self.matrix[i][j]:
                    if obj.tipo_igual(objeto):
                        coincide_tipo = True
                        pos_i, pos_j = i, j
                        break
                j += 1
            i += 1

        if coincide_tipo:
            if objeto in self.matrix[pos_i][pos_j]:
                #print(" item ya existe en el inventario")
                return False
            else:
                #print("agregar item en posicion:(",pos_i,",",pos_j,")")
                self.matrix[pos_i][pos_j].append(objeto)
                return True
        else:
            # Si no hay coincidencia de tipo, buscar una posición vacía
            for i in range(self.tamanio_filas):
                for j in range(self.tamanio_col):
                    if len(self.matrix[i][j]) == 0:
                        #print("agregar item en posicion:(",i,",",j,")")
                        self.matrix[i][j].append(objeto)
                        return True
    
    def posicion_ocupada_cuadricula(self,x,y):
        if not self.pos_inventario_valida(x,y):
            return False
        return len(self.matrix[x][y])
    
    def agregar_en_posicion(self,x,y,objeto):
        #agrega solo si la posición está libre o es del mismo tipo que objeto
        if  not self.pos_inventario_valida(x,y):
            return False
        if self.itemsMismoTipoEnPosicion(x,y,objeto):
            if not self.existeItemEnPosicion(x,y,objeto):
                #agregar en esa posicion si en esa posición no existe ese mismo objeto
                self.matrix[x][y].append(objeto)
                return True
            else:
                #el item ya existe
                return False
        else:
            if self.cantidad_items_posicion(x,y)==0:
                self.matrix[x][y].append(objeto)
                return True
            else:
                return False


    def pos_inventario_valida(self,x,y):
        return x<self.tamanio_filas and x>=0 and y>=0 and y<self.tamanio_col

    def establecer_posicion_inventario_actual(self,x,y):
        if self.pos_inventario_valida(x,y):
            self.posicion_inventario_actual=(x,y)
            return True
        else:
            print('no se puede establecer la posicion solicitada en el inventario')
            return False
        
    def obtener_posicion_inventario_actual(self):
        return self.posicion_inventario_actual
    
    def obtener_item_actual(self):
        """
        Devuelve el objeto actualmente seleccionado.
        """
        x= self.posicion_inventario_actual[0]
        y= self.posicion_inventario_actual[1]
        if len(self.matrix[x][y])>0:
            return self.matrix[x][y][0]
        return None
    
    def soltar_item_seleccionado_matrix(self):
        x= self.posicion_inventario_actual[0]
        y= self.posicion_inventario_actual[1]
        if len(self.matrix[x][y])>0:
            return self.matrix[x][y].pop()
        return None
    
    def sacar_grupo_items_matrix(self,x,y):
        if self.pos_inventario_valida(x,y):
            #no uso el método clear() porque 
            self.matrix[x][y]=[]   

    def obtener_grupo_items_matrix(self,x,y):
        return self.matrix[x][y]

    def seleccionar_barra_rapida(self, indice):
        """
        Selecciona un elemento de la barra rápida basado en el índice.
        :param indice: Índice del elemento en la barra rápida (0-8).
        """
        if 0 <= indice < 9:  # Asegurarse de que el índice esté dentro del rango de la barra rápida
            self.item_seleccionado_barra = indice
        else:
            print("error. indice barra rapida no valido")

   
    
    def obtener_grupo_items_barra(self,indice):
        return self.barra_rapida[indice]
    
    def limpiar_pos_barra(self, indice):
        if 0 <= indice < len(self.barra_rapida):  # Asegurarse de que el índice esté dentro del rango de la barra rápida
            self.barra_rapida[indice]=[] 
        else:
            print("error limpiar. indice barra rapida no valido")
            
    def asignar_item_a_barra_rapida(self, indice_barra, x, y):
        if not (0 <= indice_barra < len(self.barra_rapida)):
            print("Error: índice de barra rápida fuera de rango")
            return False
        if not self.pos_inventario_valida(x, y):
            print("Error: posición de inventario no válida")
            return False  
        self.barra_rapida[indice_barra] = self.obtener_grupo_items_matrix(x, y)
        return True
    
    def soltar_item_seleccionado_barra(self):
        """
        Elimina el elemento actualmente seleccionado de la barra rápida y lo devuelve.
        :return: El objeto eliminado o None si no hay un objeto seleccionado.
        """
        if  0<=self.item_seleccionado_barra < len(self.barra_rapida):
            elemento_soltado = (self.barra_rapida[self.item_seleccionado_barra]).pop()  # Eliminar y guardar el elemento seleccionado
            return elemento_soltado  # Devolver el elemento eliminado
        return None  # No hay elemento para soltar