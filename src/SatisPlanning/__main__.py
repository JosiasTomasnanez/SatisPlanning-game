import pygame
from .fabrica_juego import FabricaJuego
from .persistencia.gestor_db import GestorDB
import SatisPlanning.constantes as ct
from SatisPlanning.patron_observer import GestorPresentadoresObserver

def main():
    coneDB = GestorDB()
    pygame.init()
    pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO))
    pygame.display.set_caption("SatisPlanning")
    reloj = pygame.time.Clock()
    fullscreen = False

    # Usar la fábrica para crear todos los objetos
    objetos = FabricaJuego.crear_todo(pantalla)
    vista_menu = objetos["vista_menu"]
    vista_juego = objetos["vista_juego"]
    gestor = objetos["gestor"]
    personaje_jugador = objetos["personaje"]  # <-- Cambia "personaje_jugador" por "personaje"

    personaje_jugador.agregar_observer(GestorPresentadoresObserver(gestor))

    corriendo = True
    gestor.cambiar_a_menu()

    while corriendo:
        dt = reloj.tick(ct.FPS) / 1000

        presentador_actual = gestor.obtener_presentador_actual()
        vista_actual = gestor.obtener_vista_actual()

        eventos = vista_actual.obtener_eventos()
        # --- Pantalla completa: F11 ---
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO), pygame.FULLSCREEN)
                else:
                    pantalla = pygame.display.set_mode((ct.ANCHO, ct.ALTO))
                vista_menu.pantalla = pantalla
                vista_juego.pantalla = pantalla

        comando = presentador_actual.actualizar(dt, eventos)
        if comando == "jugar":
            gestor.cambiar_a_juego()
        elif comando == "menu":
            gestor.cambiar_a_menu()
        elif comando == "salir":
            corriendo = False

    pygame.quit()

if __name__ == "__main__":
    main()