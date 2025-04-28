import pygame
from SatisPlanning.objeto import Objeto
from SatisPlanning.personaje import Personaje
from SatisPlanning.mapa import Mapa
import SatisPlanning.constantes as ct
from SatisPlanning.suelo import Suelo
from SatisPlanning.camara import Camara

class Mundo:
    def __init__(self, camara):
        self.objetos_por_chunk = {}  # Diccionario para asociar posiciones de chunks con objetos
        self.mapa = Mapa()  # Instancia de la clase Mapa
        self.personaje = Personaje(100, 100, 40, 40)  # Personaje principal
        self.ultimo_chunk = None  # Variable para rastrear el último chunk del personaje
        self.chunks_visibles = []  # Lista de posiciones de los chunks visibles
        self.submatrices_chunks = []  # Lista de submatrices para carga progresiva
        self.camara = camara  # Instancia de la cámara

        # Cargar los chunks iniciales
        self._cargar_chunks_iniciales()

    def _cargar_chunks_iniciales(self):
        """
        Carga los chunks iniciales (anterior, actual y siguiente).
        """
        chunk_actual = int(self.personaje.x // (ct.COLUMNAS * ct.TAMANIO_BLOQUE))
        self.ultimo_chunk = chunk_actual

        for offset in [-1, 0, 1]:
            chunk_x = (chunk_actual + offset) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
            self._cargar_chunk_completo(chunk_actual + offset, chunk_x)

        # Actualizar la lista de chunks visibles
        self.chunks_visibles = [
            (chunk_actual - 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
            chunk_actual * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
            (chunk_actual + 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
        ]

    def _cargar_chunk_completo(self, chunk_index, chunk_x):
        """
        Carga un chunk completo y lo almacena en objetos_por_chunk.
        """
        chunk = self.mapa.obtener_chunk(chunk_index)
        objetos = []

        for fila_index, fila in enumerate(chunk):
            for col_index, bloque in enumerate(fila):
                x = chunk_x + col_index * ct.TAMANIO_BLOQUE
                y = fila_index * ct.TAMANIO_BLOQUE

                if bloque == 3:  # Bloque de superficie (pasto)
                    objetos.append(Suelo(x, y, ct.TAMANIO_BLOQUE, ct.TAMANIO_BLOQUE, ct.TEXTURA_PASTO))
                elif bloque == 1:  # Bloque de tierra
                    objetos.append(Suelo(x, y, ct.TAMANIO_BLOQUE, ct.TAMANIO_BLOQUE, ct.TEXTURA_TIERRA))
                elif bloque == 2:  # Bloque de piedra
                    objetos.append(Suelo(x, y, ct.TAMANIO_BLOQUE, ct.TAMANIO_BLOQUE, ct.TEXTURA_PIEDRA))

        self.objetos_por_chunk[chunk_x] = objetos

        """IMPORTANTE: ver la forma de  no hacer cadenas de if asi, creo que hay una forma facil si definimos bien los numeros de las costantes"""

    def _iniciar_carga_progresiva(self, chunk_index, chunk_x):
        """
        Divide el chunk en submatrices y luego en sub-submatrices para cargarlo progresivamente.
        """
        chunk = self.mapa.obtener_chunk(chunk_index)
        self.submatrices_chunks = []  # Reiniciar las submatrices

        for fila_inicio in range(0, ct.FILAS, 5):  # Dividir en bloques de 5 filas
            submatriz = chunk[fila_inicio:fila_inicio + 5]
            for fila_offset, fila in enumerate(submatriz):  # Dividir cada fila en sub-submatrices
                for col_inicio in range(0, len(fila), 5):  # Dividir en bloques de 5 columnas
                    sub_submatriz = fila[col_inicio:col_inicio + 5]
                    self.submatrices_chunks.append((sub_submatriz, chunk_x, fila_inicio + fila_offset, col_inicio))

    def _procesar_submatriz(self, sub_submatriz, chunk_x, fila_inicio, col_inicio):
        """
        Procesa una sub-submatriz y crea los objetos correspondientes.
        """
        objetos = self.objetos_por_chunk.get(chunk_x, [])

        for col_offset, bloque in enumerate(sub_submatriz):
            x = chunk_x + (col_inicio + col_offset) * ct.TAMANIO_BLOQUE
            y = fila_inicio * ct.TAMANIO_BLOQUE

            if bloque == 3:  # Bloque de superficie (pasto)
                objetos.append(Suelo(x, y, ct.TAMANIO_BLOQUE, ct.TAMANIO_BLOQUE, ct.TEXTURA_PASTO))
            elif bloque == 1:  # Bloque de tierra
                objetos.append(Suelo(x, y, ct.TAMANIO_BLOQUE, ct.TAMANIO_BLOQUE, ct.TEXTURA_TIERRA))
            elif bloque == 2:  # Bloque de piedra
                objetos.append(Suelo(x, y, ct.TAMANIO_BLOQUE, ct.TAMANIO_BLOQUE, ct.TEXTURA_PIEDRA))
            
            """IMPORTANTE: al igual que el otro, es posible optimizar este codigo por lo mismo"""


        self.objetos_por_chunk[chunk_x] = objetos

    def actualizar(self, dt, eventos):
        """
        Actualiza la lógica del mundo.
        """
        for evento in eventos:
            self.personaje.manejar_evento(evento, self)

        teclas = pygame.key.get_pressed()
        self.personaje.actualizar(teclas, self)

        self.generar_mapa()
        self.camara.actualizar(self.personaje.x, self.personaje.y)

        # Procesar una sub-submatriz en cada frame
        if self.submatrices_chunks:
            sub_submatriz, chunk_x, fila_inicio, col_inicio = self.submatrices_chunks.pop(0)
            self._procesar_submatriz(sub_submatriz, chunk_x, fila_inicio, col_inicio)

    def generar_mapa(self):
        """
        Genera y actualiza los chunks visibles en función de la posición del personaje.
        """
        chunk_actual = int(self.personaje.x // (ct.COLUMNAS * ct.TAMANIO_BLOQUE))

        if chunk_actual != self.ultimo_chunk:
            self.ultimo_chunk = chunk_actual
            self._actualizar_chunks_visibles(chunk_actual)

    def _actualizar_chunks_visibles(self, chunk_actual):
        """
        Actualiza los chunks visibles, cargando los siguientes y eliminando los más antiguos.
        """
            # Cargar el siguiente chunk progresivamente (a la derecha)
        chunk_siguiente_x = (chunk_actual + 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
        if chunk_siguiente_x not in self.objetos_por_chunk:
            self._iniciar_carga_progresiva(chunk_actual + 1, chunk_siguiente_x)

            # Cargar el chunk anterior progresivamente (a la izquierda)
        chunk_anterior_x = (chunk_actual - 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
        if chunk_anterior_x not in self.objetos_por_chunk:
            self._iniciar_carga_progresiva(chunk_actual - 1, chunk_anterior_x)

            # Eliminar el chunk más antiguo a la derecha (si está fuera de rango)
        chunk_fuera_derecha_x = (chunk_actual + 2) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
        if chunk_fuera_derecha_x in self.objetos_por_chunk:
            del self.objetos_por_chunk[chunk_fuera_derecha_x]
        
            # Eliminar el chunk más antiguo a la izquierda (si está fuera de rango)
        chunk_fuera_izquierda_x = (chunk_actual - 2) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
        if chunk_fuera_izquierda_x in self.objetos_por_chunk:
            del self.objetos_por_chunk[chunk_fuera_izquierda_x]
        
            # Actualizar la lista de chunks visibles
        self.chunks_visibles = [
            (chunk_actual - 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
            chunk_actual * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
            (chunk_actual + 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
        ]

    def colisiona(self, hitbox):
        """
        Verifica si la hitbox colisiona con algún objeto.
        """
        for chunk_x in self.chunks_visibles:
            for objeto in self.objetos_por_chunk.get(chunk_x, []):
                if objeto.hitbox.colliderect(hitbox):
                    return True
        return False

    def agregar_objeto(self, objeto):
        """
        Agrega un objeto al mundo para que sea dibujado.
        :param objeto: Instancia de la clase Objeto.
        """
        chunk_x = int(objeto.x // (ct.COLUMNAS * ct.TAMANIO_BLOQUE))
        chunk_y = int(objeto.y // (ct.FILAS * ct.TAMANIO_BLOQUE))
        chunk_key = (chunk_x, chunk_y)

        if chunk_key not in self.objetos_por_chunk:
            self.objetos_por_chunk[chunk_key] = []

        self.objetos_por_chunk[chunk_key].append(objeto)

    def dibujar(self, pantalla):
        """
        Dibuja el mundo y los objetos en la pantalla.
        """
        for chunk_key in self.objetos_por_chunk.keys():
            objetos = self.objetos_por_chunk.get(chunk_key, [])
            for objeto in objetos:
                objeto_x, objeto_y = self.camara.aplicar(objeto.x, objeto.y)
                objeto.dibujar_con_desplazamiento(pantalla, objeto_x, objeto_y)

        self.personaje.dibujar(pantalla, ct.FUENTE, self.camara)

#se tendria que separar la logica del cargado y gestionado de chunks en otra clase que lo haga , y devuelva solo las listas de los elementos para que world se ocupe, para simplificar la logica , hacerlo mas ecalable y legible
