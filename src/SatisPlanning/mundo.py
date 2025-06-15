import pygame
from SatisPlanning.entidades.personaje_jugador import PersonajeJugador
from SatisPlanning.mapa import Mapa
from SatisPlanning.manejador_chunks import ManjeadorChunks

class Mundo:
    def __init__(self, personaje, mapa, manejador_chunks):
        self.mapa = mapa  # Instancia de la clase Mapa
        self.personaje = personaje  # Personaje principal
        self.personaje.set_mundo(self)
        self.manejador_chunks = manejador_chunks  # Instancia del manejador de chunks

        # Cargar los chunks iniciales
        self.manejador_chunks.cargar_chunks_iniciales(self.personaje)

    def obtener_personaje(self):
        """
        Devuelve el personaje principal.
        """
        return self.personaje
    
    
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

    def obtener_objetos_a_dibujar(self):
        """
        Devuelve los objetos y el personaje para ser dibujados.
        """
        objetos = []
        for chunk_x in self.manejador_chunks.obtener_chunks_visibles():
            objetos.extend(self.manejador_chunks.obtener_objetos_por_chunk(chunk_x))
        return objetos, self.personaje
