import random
from perlin_noise import PerlinNoise
import constantes as ct

class Mapa:
    def __init__(self):
        """
        Inicializa el mapa con un diccionario para almacenar los chunks generados.
        """
        self.seed = random.randint(0, 1000)  # Semilla para la generación del terreno
        self.chunks = {}  # Diccionario para almacenar los chunks generados

    def _generar_chunk(self, chunk_x):
        """
        Genera un nuevo chunk basado en la posición X del chunk.

        :param chunk_x: Coordenada X del chunk (en unidades de chunks).
        :return: Matriz 2D representando el chunk generado.
        """
        chunk = [[0 for _ in range(ct.COLUMNAS)] for _ in range(ct.FILAS)]
        noise = PerlinNoise(octaves=3, seed=self.seed)
        altura_media = ct.FILAS // 2

        for col in range(ct.COLUMNAS):
            altura = altura_media + int(noise((chunk_x * ct.COLUMNAS + col) / 15) * 10)
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
