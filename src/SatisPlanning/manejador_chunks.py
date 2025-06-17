from .mapa import Mapa
import SatisPlanning.constantes as ct
from .entidades.suelo import Suelo

class ManjeadorChunks:
    def __init__(self, mapa):
        self.mapa = mapa  # Instancia de la clase Mapa
        self.objetos_por_chunk = {}  # Diccionario para asociar posiciones de chunks con objetos
        self.ultimo_chunk = None  # Variable para rastrear el último chunk del personaje
        self.chunks_visibles = []  # Lista de posiciones de los chunks visibles
        self.submatrices_chunks = []  # Lista de submatrices para carga progresiva
        self.chunks_cargados = set()  # Conjunto para almacenar los índices de chunks cargados

    def cargar_chunks_iniciales(self, personaje):
        """
        Carga los chunks iniciales (anterior, actual y siguiente).
        """
        chunk_actual = int(personaje.x // (ct.COLUMNAS * ct.TAMANIO_BLOQUE))
        self.ultimo_chunk = chunk_actual

        for offset in [-1, 0, 1]:
            chunk_x = (chunk_actual + offset) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
            self._cargar_chunk_completo(chunk_actual + offset, chunk_x)
            self.chunks_cargados.add(chunk_actual + offset)

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

    def iniciar_carga_progresiva(self, chunk_index, chunk_x):
        """
        Divide el chunk en submatrices y luego en sub-submatrices para cargarlo progresivamente.
        Si el chunk ya está cargado, no se vuelve a cargar.
        """
        if chunk_index in self.chunks_cargados:
            return  # No recargar si ya está cargado

        chunk = self.mapa.obtener_chunk(chunk_index)
        self.submatrices_chunks = []  # Reiniciar las submatrices

        for fila_inicio in range(0, ct.FILAS, 5):  # Dividir en bloques de 5 filas
            submatriz = chunk[fila_inicio:fila_inicio + 5]
            for fila_offset, fila in enumerate(submatriz):  # Dividir cada fila en sub-submatrices
                for col_inicio in range(0, len(fila), 5):  # Dividir en bloques de 5 columnas
                    sub_submatriz = fila[col_inicio:col_inicio + 5]
                    self.submatrices_chunks.append((sub_submatriz, chunk_x, fila_inicio + fila_offset, col_inicio))

    def procesar_submatriz(self):
        """
        Procesa una sub-submatriz en cada frame y crea los objetos correspondientes.
        """
        if self.submatrices_chunks:
            sub_submatriz, chunk_x, fila_inicio, col_inicio = self.submatrices_chunks.pop(0)
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

            self.objetos_por_chunk[chunk_x] = objetos

    def actualizar_chunks_visibles(self, personaje):
        """
        Genera y actualiza los chunks visibles en función de la posición del personaje.
        """
        chunk_actual = int(personaje.x // (ct.COLUMNAS * ct.TAMANIO_BLOQUE))

        if chunk_actual != self.ultimo_chunk:
            self.ultimo_chunk = chunk_actual
            self._actualizar_chunks_visibles(chunk_actual)

    def _actualizar_chunks_visibles(self, chunk_actual):
        """
        Actualiza los chunks visibles, cargando los siguientes y reutilizando los ya cargados.
        """
        # Cargar el siguiente chunk progresivamente (a la derecha)
        chunk_siguiente_x = (chunk_actual + 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
        if chunk_actual + 1 not in self.chunks_cargados:
            self.iniciar_carga_progresiva(chunk_actual + 1, chunk_siguiente_x)
            self.chunks_cargados.add(chunk_actual + 1)

        # Cargar el chunk anterior progresivamente (a la izquierda)
        chunk_anterior_x = (chunk_actual - 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE
        if chunk_actual - 1 not in self.chunks_cargados:
            self.iniciar_carga_progresiva(chunk_actual - 1, chunk_anterior_x)
            self.chunks_cargados.add(chunk_actual - 1)

        # Mantener los chunks fuera de rango en memoria, pero no visibles
        # Actualizar la lista de chunks visibles
        self.chunks_visibles = [
            (chunk_actual - 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
            chunk_actual * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
            (chunk_actual + 1) * ct.COLUMNAS * ct.TAMANIO_BLOQUE,
        ]

    def obtener_chunks_visibles(self):
        """
        Devuelve los chunks visibles.
        """
        return self.chunks_visibles

    def obtener_objetos_por_chunk(self, chunk_x):
        """
        Devuelve los objetos de un chunk específico.
        """
        return self.objetos_por_chunk.get(chunk_x, [])

    def agregar_objeto(self, objeto):
        """
        Agrega un objeto al chunk correspondiente según su posición.
        """
        chunk_index = int(objeto.x // (ct.COLUMNAS * ct.TAMANIO_BLOQUE))
        chunk_x = chunk_index * ct.COLUMNAS * ct.TAMANIO_BLOQUE
        self.objetos_por_chunk.setdefault(chunk_x, []).append(objeto)

# mejora: persistencia en los bloques
