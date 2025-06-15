import pygame
from SatisPlanning.presentador_juego import PresentadorJuego
import SatisPlanning.constantes as ct
from SatisPlanning.persistencia.gestor_db import GestorDB
from SatisPlanning.mundo import Mundo  # Cambiado de World a Mundo
from SatisPlanning.vista_juego import VistaJuego
from SatisPlanning.camara import Camara

def main():
    coneDB= GestorDB()
    pygame.init()
    pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO))
    presentador_juego = PresentadorJuego(Mundo(),VistaJuego(Camara(),pantalla))

    pygame.display.set_caption("SatisPlanning")
    reloj = pygame.time.Clock()
    corriendo = True
    
    while corriendo:
        dt = reloj.tick(ct.FPS) / 1000  # Delta time en segundos

        eventos = presentador_juego.vista_juego.obtener_eventos()  # La vista obtiene los eventos de pygame
        eventos_filtrados = presentador_juego.manejar_eventos(eventos)  # Se los pasa al presentador
        if eventos_filtrados is None:  # Si se detecta un evento de salida
            corriendo = False
            continue

        presentador_juego.actualizar(dt, eventos_filtrados) 

    pygame.quit()

if __name__ == "__main__":
    main()


# a esta clase la veo ok, se encarga de iniciar pygame y de generar el bucle que corre el juego, definiendo los fps, y controlando los eventos de salida, ordenando en cada iteraccion al juego ctualizarse y dibujarse
