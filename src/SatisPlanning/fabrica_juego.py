from SatisPlanning.vista_menu import VistaMenu
from SatisPlanning.presentador_menu import PresentadorMenu
from SatisPlanning.vista_juego import VistaJuego
from SatisPlanning.presentador_juego import PresentadorJuego
from SatisPlanning.gestor_presentadores import GestorPresentadores
from SatisPlanning.camara import Camara
from SatisPlanning.entidades.personaje_jugador import PersonajeJugador
from SatisPlanning.mapa import Mapa
from SatisPlanning.manejador_chunks import ManjeadorChunks
from SatisPlanning.mundo import Mundo
import SatisPlanning.constantes as ct

class FabricaJuego:
    @staticmethod
    def crear_todo(pantalla):
        # Vistas y presentadores del menú
        vista_menu = VistaMenu(pantalla)
        presentador_menu = PresentadorMenu(vista_menu)

        # Objetos del mundo
        mapa = Mapa()
        personaje = PersonajeJugador(100, 100, 40, 40)
        manejador_chunks = ManjeadorChunks(mapa)
        mundo = Mundo(personaje, mapa, manejador_chunks)
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
            "manejador_chunks": manejador_chunks
        }
