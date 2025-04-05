import pygame
from Game import Game
import constantes as ct

def main():
    pygame.init()
    game = Game()

    pygame.display.set_caption("Terraria Clone")
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(ct.FPS) / 1000  # Delta time en segundos

        eventos = game.handle_events()  # Captura los eventos
        if eventos is None:  # Si se detecta un evento de salida
            running = False
            continue

        game.update(dt, eventos)  # Pasa los eventos al método update
        game.render()  # Dibuja en pantalla

    pygame.quit()

if __name__ == "__main__":
    main()
