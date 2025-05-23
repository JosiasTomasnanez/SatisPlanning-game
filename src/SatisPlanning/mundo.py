import pygame
from SatisPlanning.objeto import Objeto
from SatisPlanning.personaje_jugador import PersonajeJugador
from SatisPlanning.mapa import Mapa
import SatisPlanning.constantes as ct
from SatisPlanning.camara import Camara
from SatisPlanning.manejador_chunks import ManjeadorChunks

class Mundo:
    def __init__(self, camara):
        self.mapa = Mapa()  # Instancia de la clase Mapa
        self.personaje = PersonajeJugador(100, 100, 40, 40)  # Personaje principal
        self.personaje.set_mundo(self)
        self.camara = camara  # Instancia de la cámara
        self.manejador_chunks = ManjeadorChunks(self.mapa)  # Instancia del manejador de chunks

        # Cargar los chunks iniciales
        self.manejador_chunks.cargar_chunks_iniciales(self.personaje)

    def actualizar(self, dt, eventos):
        """
        Actualiza la lógica del mundo.
        """
        for evento in eventos:
            self.personaje.manejar_evento(evento)

        teclas = pygame.key.get_pressed()
        self.personaje.actualizar(teclas)

        # Actualizar chunks visibles y procesar submatrices
        self.manejador_chunks.actualizar_chunks_visibles(self.personaje)
        self.manejador_chunks.procesar_submatriz()

        self.camara.actualizar(self.personaje.x, self.personaje.y)

  
    def colisiona(self, hitbox, obj):
        """
        Verifica si la hitbox colisiona con algún objeto.
        """
        for chunk_x in self.manejador_chunks.obtener_chunks_visibles():
            for objeto in self.manejador_chunks.obtener_objetos_por_chunk(chunk_x):
                if objeto.hitbox.colliderect(hitbox) and objeto.tangible==True:
                    obj.notificar_colision(objeto)
                    objeto.notificar_colision(obj)
                    return True
        return False

    def agregar_objeto(self, objeto,tangible):
        """
        Agrega un objeto al mundo para que sea dibujado.
        :param objeto: Instancia de la clase Objeto.
        """
        objeto.tangible = tangible
        self.manejador_chunks.agregar_objeto(objeto)

    def dibujar(self, pantalla):
        """
        Dibuja el mundo y los objetos en la pantalla.
        """
        for chunk_x in self.manejador_chunks.obtener_chunks_visibles():
            for objeto in self.manejador_chunks.obtener_objetos_por_chunk(chunk_x):
                objeto_x, objeto_y = self.camara.aplicar(objeto.x, objeto.y)
                objeto.dibujar_con_desplazamiento(pantalla, objeto_x, objeto_y)

        self.personaje.dibujar(pantalla, ct.FUENTE, self.camara)
