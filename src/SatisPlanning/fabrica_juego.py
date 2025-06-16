from .vista_menu import VistaMenu
from .presentador_menu import PresentadorMenu
from .vista_juego import VistaJuego
from .presentador_juego import PresentadorJuego
from .gestor_presentadores import GestorPresentadores
from .camara import Camara
from .entidades.personaje_jugador import PersonajeJugador
from .mapa import Mapa
from .manejador_chunks import ManjeadorChunks
from .mundo import Mundo
from .generador_monstruos import GeneradorMonstruos
import SatisPlanning.constantes as ct
import random

class FabricaJuego:
    @staticmethod
    def crear_todo(pantalla):
        # Vistas y presentadores del menú
        vista_menu = VistaMenu(pantalla)
        presentador_menu = PresentadorMenu(vista_menu)

        # Objetos del mundo
        mapa = Mapa(random.randint(0, 1000))
        personaje = PersonajeJugador(100, 100, 40, 40)
        manejador_chunks = ManjeadorChunks(mapa)

        # Configuración de monstruos centralizada aquí
        spawn_frame_interval = 350
        max_enemigos = 5
        spawn_dist_min = 600
        spawn_dist_max = 630
        despawn_dist = 1000
        distancia_persecucion = 280

        generador_monstruos = GeneradorMonstruos(
            spawn_frame_interval=spawn_frame_interval,
            max_enemigos=max_enemigos,
            spawn_dist_min=spawn_dist_min,
            spawn_dist_max=spawn_dist_max,
            despawn_dist=despawn_dist,
            distancia_persecucion=distancia_persecucion
        )

        mundo = Mundo(personaje, mapa, manejador_chunks, generador_monstruos)
        personaje.set_mundo(mundo)

        # Vistas y presentadores del juego
        vista_juego = VistaJuego(Camara(), pantalla)
        presentador_juego = PresentadorJuego(mundo, vista_juego)

        # Gestor de presentadores
        gestor = GestorPresentadores(
            presentador_menu, vista_menu,
            presentador_juego, vista_juego
        )

        return {
            "vista_menu": vista_menu,
            "presentador_menu": presentador_menu,
            "vista_juego": vista_juego,
            "presentador_juego": presentador_juego,
            "gestor": gestor,
            "mundo": mundo,
            "personaje": personaje,
            "mapa": mapa,
            "manejador_chunks": manejador_chunks,
            "generador_monstruos": generador_monstruos
        }
