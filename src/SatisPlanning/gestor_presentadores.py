from SatisPlanning.entidades.personaje_jugador import PersonajeJugador
from SatisPlanning.mapa import Mapa

class GestorPresentadores:
    def __init__(self, presentador_menu, vista_menu, presentador_juego, vista_juego):
        self.presentador_menu = presentador_menu
        self.vista_menu = vista_menu
        self.presentador_juego = presentador_juego
        self.vista_juego = vista_juego
        self.presentador_actual = presentador_menu
        self.vista_actual = vista_menu
        self.estado = "menu"  # Estado inicial

    def cambiar_a_menu(self):
        self.presentador_actual = self.presentador_menu
        self.vista_actual = self.vista_menu
        self.presentador_menu.reiniciar()  # Reinicia el estado del menú
        self.estado = "menu"

    def cambiar_a_juego(self):
        self.presentador_actual = self.presentador_juego
        self.vista_actual = self.vista_juego
        self.estado = "juego"

    def mostrar_game_over(self):
        self.estado = "game_over"
        # Aquí puedes mostrar la pantalla de game over usando el presentador_menu
        self.presentador_menu.mostrar_game_over()

    def nueva_partida(self, pantalla):
        from .fabrica_juego import FabricaJuego  # Import local para evitar import circular
        from .entidades.personaje_jugador import PersonajeJugador
        from .mapa import Mapa

        # Resetear singletons
        PersonajeJugador.reset()
        Mapa.reset()
        # Recrear todos los objetos del juego
        objetos = FabricaJuego.crear_todo(pantalla)
        self.vista_menu = objetos["vista_menu"]
        self.presentador_menu = objetos["presentador_menu"]
        self.vista_juego = objetos["vista_juego"]
        self.presentador_juego = objetos["presentador_juego"]
        self.mundo = objetos["mundo"]
        self.personaje = objetos["personaje"]

        # RE-SUSCRIBIR EL OBSERVER DEL GESTOR AL NUEVO PERSONAJE
        from SatisPlanning.patron_observer import GestorPresentadoresObserver
        self.personaje.agregar_observer(GestorPresentadoresObserver(self))

        # IMPORTANTE: Salir del estado game_over en la vista y presentador del menú
        if hasattr(self.presentador_menu, "estado"):
            self.presentador_menu.estado = None
        if hasattr(self.vista_menu, "estado"):
            self.vista_menu.estado = None

        # Volver al juego
        self.cambiar_a_juego()

    def obtener_presentador_actual(self):
        return self.presentador_actual

    def obtener_vista_actual(self):
        return self.vista_actual
