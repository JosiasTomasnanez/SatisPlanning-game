import random
from perlin_noise import PerlinNoise
import SatisPlanning.constantes as ct

class Mapa:
    def __init__(self):
        """
        Inicializa el mapa con un diccionario para almacenar los chunks generados.
        """
        self.semilla = random.randint(0, 1000)
        self.chunks = {}  # Diccionario para almacenar los chunks generados

    def _generar_chunk(self, chunk_x):
        """
        Genera un nuevo chunk basado en la posición X del chunk.

        :param chunk_x: Coordenada X del chunk (en unidades de chunks).
        :return: Matriz 2D representando el chunk generado.
        """
        chunk = [[0 for _ in range(ct.COLUMNAS)] for _ in range(ct.FILAS)]
        ruido = PerlinNoise(octaves=3, seed=self.semilla)
        altura_media = ct.FILAS // 2

        for col in range(ct.COLUMNAS):
            altura = altura_media + int(ruido((chunk_x * ct.COLUMNAS + col) / 15) * 10)
            for fila in range(ct.FILAS):
                if fila > altura:
                    if fila == altura + 1:
                        chunk[fila][col] = 3  # Bloque de superficie
                    elif fila <= altura + 4:
                        chunk[fila][col] = 1  # Bloque de tierra
                    else:
                        chunk[fila][col] = 2  # Bloque de piedra
        return chunk

    def obtener_chunk(self, chunk_x):
        """
        Devuelve el chunk correspondiente a la posición X. Si no existe, lo genera y lo guarda.

        :param chunk_x: Coordenada X del chunk (en unidades de chunks).
        :return: Matriz 2D representando el chunk.
        """
        if chunk_x not in self.chunks:
            # Generar y guardar el chunk si no existe
            self.chunks[chunk_x] = self._generar_chunk(chunk_x)
        return self.chunks[chunk_x]

#separar la logica  de generar chunks  de obtener el tipo de bloque para mayor modularidad y poder meter mas materiales o menas, por ejemplo algo asi: 
#def _generar_chunk(self, chunk_x):
#    """
#    Genera un nuevo chunk basado en la posición X del chunk.
#    Incluye terreno base y estructuras especiales (menas, árboles, agua, etc.).
#
#    :param chunk_x: Coordenada X del chunk (en unidades de chunks).
#    :return: Matriz 2D representando el chunk generado.
#    """
#
#    # --- Primera pasada: generar terreno base ---
#    chunk = [[ct.AIRE for _ in range(ct.COLUMNAS)] for _ in range(ct.FILAS)]
#    ruido = PerlinNoise(octaves=3, seed=self.semilla)
#    altura_media = ct.FILAS // 2
#
#    for col in range(ct.COLUMNAS):
#        altura = altura_media + int(ruido((chunk_x * ct.COLUMNAS + col) / 15) * 10)
#        for fila in range(ct.FILAS):
#            if fila > altura:
#                profundidad = fila - altura
#                chunk[fila][col] = self._bloque_por_profundidad(profundidad, chunk_x)
#
#    # --- Segunda pasada: agregar estructuras especiales ---
#    self._agregar_menas(chunk)
#    self._agregar_agua_subterranea(chunk)
#    self._agregar_arboles(chunk)
#
#    return chunk
#
#
#def _bloque_por_profundidad(self, profundidad, chunk_x):
#    if 0 <= chunk_x <= 5:  # Bosque
#        if profundidad == 1:
#            return ct.SUPERFICIE
#        elif profundidad <= 4:
#            return ct.TIERRA
#        else:
#            return ct.PIEDRA
#    elif 6 <= chunk_x <= 10:  # Desierto
#        if profundidad == 1:
#            return ct.ARENA
#        elif profundidad <= 4:
#            return ct.ARENA_COMPACTA
#        else:
#            return ct.ROCA_VOLCANICA
#    else:  # Nieve
#        if profundidad == 1:
#            return ct.NIEVE
#        elif profundidad <= 4:
#            return ct.HIELO
#        else:
#            return ct.PIEDRA_CONGELADA
#
#def _agregar_menas(self, chunk, probabilidad=0.01):
#    for fila in range(len(chunk)):
#        for col in range(len(chunk[0])):
#            if chunk[fila][col] == ct.PIEDRA and random.random() < probabilidad:
#                self._generar_mena_grande(chunk, fila, col)
#
#def _generar_mena_grande(self, chunk, fila_inicial, col_inicial, radio=2):
#    for dy in range(-radio, radio + 1):
#        for dx in range(-radio, radio + 1):
#            y = fila_inicial + dy
#            x = col_inicial + dx
#            if 0 <= y < len(chunk) and 0 <= x < len(chunk[0]):
#                if chunk[y][x] == ct.PIEDRA:
#                    chunk[y][x] = ct.MENA_HIERRO
#def _agregar_agua_subterranea(self, chunk, profundidad_min=12):
#    for fila in range(profundidad_min, len(chunk)):
#        for col in range(len(chunk[0])):
#            if chunk[fila][col] == ct.AIRE and random.random() < 0.01:
#                chunk[fila][col] = ct.AGUA
#def _agregar_arboles(self, chunk):
#    for col in range(len(chunk[0])):
#        for fila in range(len(chunk)):
#            if chunk[fila][col] == ct.SUPERFICIE:
#                if random.random() < 0.1:
#                    self._generar_arbol(chunk, fila, col)
#                break  # Solo checamos el primer bloque sólido desde arriba
#def _generar_arbol(self, chunk, base_fila, col):
#    altura = random.randint(3, 5)
#    for i in range(1, altura + 1):
#        if base_fila - i >= 0:
#            chunk[base_fila - i][col] = ct.TRONCO
#
#    # Hojas (simplificadas)
#    hoja_nivel = base_fila - altura
#    for dx in [-1, 0, 1]:
#        for dy in [-1, 0, 1]:
#            x = col + dx
#            y = hoja_nivel + dy
#            if 0 <= x < ct.COLUMNAS and 0 <= y < ct.FILAS:
#                chunk[y][x] = ct.HOJA
# esto propone chatgpt pero hay que ver que tan viable y de que forma hacerlo, pero la idea es hacer varias pasadas por la matriz, haciendo estas cosas , y hay que ver la forma de que quede lo mas modular posible
