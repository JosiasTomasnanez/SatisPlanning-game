import pygame

class PresentadorJuego:
    def __init__(self,mundo,vista_juego):
        self.mundo = mundo
        self.vista_juego = vista_juego

    """
    Manejador de eventos del juego.
    Captura eventos de entrada y verifica si el juego debe cerrarse.
    """
    def manejar_eventos(self):
        eventos = pygame.event.get()  # Obtiene la lista de eventos
        for evento in eventos: 
            if evento.type == pygame.QUIT:  # Si se recibe un evento de cierre
                return None  # Indica que el juego debe cerrarse
        return eventos  # Devuelve la lista de eventos

    """Actualiza el juego."""
    def actualizar(self, dt, eventos):
        self.mundo.actualizar(dt, eventos)
        objetos, personaje, enemigos = self.mundo.obtener_objetos_a_dibujar()
        self.vista_juego.dibujar(objetos, personaje, enemigos)  # Actualiza la pantalla con los objetos y enemigos a dibujar
