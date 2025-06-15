import pygame

class PresentadorJuego:
    def __init__(self, mundo, vista_juego):
        self.mundo = mundo
        self.vista_juego = vista_juego

    """
    Manejador de eventos del juego.
    Captura eventos de entrada y verifica si el juego debe cerrarse.
    """
    def manejar_eventos(self, eventos):
        """
        Procesa la lista de eventos recibida desde la vista.
        Si hay un evento de cierre, retorna None para indicar que debe cerrarse el juego.
        """
        for evento in eventos:
            if getattr(evento, "type", None) == getattr(self.vista_juego, "QUIT", None):
                return "salir"
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "menu"
        return eventos  # Devuelve la lista de eventos

    """Actualiza el juego."""
    def actualizar(self, dt, eventos):
        resultado = self.manejar_eventos(eventos)
        if resultado == "salir":
            return "salir"
        elif resultado == "menu":
            return "menu"
        else:
            self.mundo.actualizar(dt, resultado)
            objetos, personaje = self.mundo.obtener_objetos_a_dibujar()
            self.vista_juego.dibujar(objetos, personaje)  # Actualiza la pantalla con los objetos a dibujar
            return None
