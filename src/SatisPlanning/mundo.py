import pygame
from .entidades.personaje_jugador import PersonajeJugador
from .mapa import Mapa
from .manejador_chunks import ManjeadorChunks
from .generador_monstruos import GeneradorMonstruos
from .manejador_niveles import ManejadorNiveles

class Mundo:
    def __init__(self, personaje, mapa, manejador_chunks, manejador_niveles):
        self.mapa = mapa  # Instancia de la clase Mapa
        self.personaje = personaje  # Personaje principal
        self.personaje.set_mundo(self)
        self.manejador_chunks = manejador_chunks  # Instancia del manejador de chunks

        # Cargar los chunks iniciales
        self.manejador_chunks.cargar_chunks_iniciales(self.personaje)
        self.manejador_niveles = manejador_niveles

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

        self.manejador_niveles.actualizar(self.personaje)

        # Actualizar chunks visibles y procesar submatrices
        self.manejador_chunks.actualizar_chunks_visibles(self.personaje)
        self.manejador_chunks.procesar_submatriz()

  
    def colisiona(self, hitbox, obj):
        """
        Verifica si la hitbox colisiona con algún objeto.
        Permite que jugador y enemigo se superpongan, pero bloquea con el entorno.
        """
        for chunk_x in self.manejador_chunks.obtener_chunks_visibles():
            for objeto in self.manejador_chunks.obtener_objetos_por_chunk(chunk_x):
                if objeto.hitbox.colliderect(hitbox) and objeto.tangible:
                    # Permitir superposición entre jugador y enemigo
                    if (getattr(obj, 'es_jugador', False) and getattr(objeto, 'es_enemigo', False)) or \
                       (getattr(obj, 'es_enemigo', False) and getattr(objeto, 'es_jugador', False)):
                        obj.notificar_colision(objeto)
                        objeto.notificar_colision(obj)
                        # No retorna True, así no bloquea el movimiento
                    else:
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

    def obtener_enemigos(self):
        """
        Devuelve la lista de enemigos.
        """
        return self.manejador_niveles.obtener_enemigos()

    def obtener_objetos_a_dibujar(self):
        """
        Devuelve los objetos, el personaje y los enemigos para ser dibujados.
        """
        objetos = []
        for chunk_x in self.manejador_chunks.obtener_chunks_visibles():
            objetos.extend(self.manejador_chunks.obtener_objetos_por_chunk(chunk_x))
        return objetos, self.personaje, self.obtener_enemigos()

    def chequear_colisiones_jugador_enemigos(self):
        """
        Verifica colisiones entre el personaje jugador y todos los enemigos.
        Llama a notificar_colision en ambos si ocurre una colisión.
        """
        for enemigo in self.obtener_enemigos():
            if self.personaje.hitbox.colliderect(enemigo.hitbox):
                self.personaje.notificar_colision(enemigo)
                enemigo.notificar_colision(self.personaje)