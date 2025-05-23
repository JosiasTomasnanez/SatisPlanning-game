import pygame
from SatisPlanning.juego import Juego 
import SatisPlanning.constantes as ct

def main():
    pygame.init()
    juego = Juego()

    pygame.display.set_caption("SatisPlanning")
    reloj = pygame.time.Clock()
    corriendo = True
    while corriendo:
        dt = reloj.tick(ct.FPS) / 1000  # Delta time en segundos

        eventos = juego.manejar_eventos()
        if eventos is None:  # Si se detecta un evento de salida
            corriendo = False
            continue

        juego.actualizar(dt, eventos) 
        juego.dibujar()  

    pygame.quit()

if __name__ == "__main__":
    main()


# a esta clase la veo ok, se encarga de iniciar pygame y de generar el bucle que corre el juego, definiendo los fps, y controlando los eventos de salida, ordenando en cada iteraccion al juego ctualizarse y dibujarse
