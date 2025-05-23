from SatisPlanning.mundo import Mundo  # Cambiado de World a Mundo
from SatisPlanning.interfaz_grafica import Graficos
from SatisPlanning.camara import Camara

import pygame

class Juego:
    def __init__(self):
        self.camara = Camara()
        self.mundo = Mundo(self.camara)
        self.graficos = Graficos(self.mundo)

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

    """Dibuja el juego en pantalla."""
    def dibujar(self):
        self.graficos.dibujar()

#A esta clase la veo ok , tiene el metodo para almacenar los eventos de teclado, tiene otro para actualizar el mundo en correspondencia a dichos eventos y otro que se realiza constantemente para ordenar a graficos que dibuje todo lo que es visible de nuestro mundo. por otro lado esta clase es importante por que es quien gestiona la creacion de un nuevo mundo, los graficos y la camara asociada a dicho mundo y delega las responsabilidades propuestas por el main a las clases correspondientes (dibujar a grafics y actualizar a mundo) 
