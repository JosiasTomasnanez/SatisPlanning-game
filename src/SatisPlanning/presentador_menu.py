import pygame
from .utilidades import es_click_mouse, obtener_posicion_mouse
from .menu import Menu

class PresentadorMenu:
    def __init__(self, vista_menu, gestor_presentadores=None):
        self.vista_menu = vista_menu
        self.menu = Menu(self.vista_menu.opciones)
        self.gestor_presentadores = gestor_presentadores  # Nuevo: referencia al gestor

    def manejar_eventos(self, eventos):
        for evento in eventos:
            if getattr(evento, "type", None) == getattr(self.vista_menu, "QUIT", None):
                self.menu.terminado = True
                self.menu.seleccion = "salir"
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    self.menu.mover_arriba()
                elif evento.key == pygame.K_DOWN:
                    self.menu.mover_abajo()
                elif evento.key == pygame.K_RETURN:
                    self.menu.seleccionar()
            elif es_click_mouse(evento):
                mouse_x, mouse_y = obtener_posicion_mouse()
                opcion = self.vista_menu.obtener_opcion_en_posicion(mouse_x, mouse_y)
                if opcion is not None:
                    self.menu.seleccionar_por_indice(opcion)

    def actualizar(self, dt, eventos):
        if getattr(self, "estado", None) == "game_over":
            self.vista_menu.mostrar_game_over()
            for evento in eventos:
                if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.type == pygame.MOUSEBUTTONDOWN:
                        x, y = evento.pos
                        if self.vista_menu.obtener_opcion_en_posicion(x, y) == "nueva_partida":
                            self.estado = None
                            self.menu.reiniciar()
                            if self.gestor_presentadores:
                                self.gestor_presentadores.nueva_partida(self.vista_menu.pantalla)
                            return "jugar"
                    elif evento.type == pygame.KEYDOWN:
                        self.estado = None
                        self.menu.reiniciar()
                        if self.gestor_presentadores:
                            self.gestor_presentadores.nueva_partida(self.vista_menu.pantalla)
                        return "jugar"
            return None

        self.manejar_eventos(eventos)
        self.vista_menu.opcion_seleccionada = self.menu.opcion_seleccionada
        self.vista_menu.dibujar()
        # Devuelve el comando de navegación si corresponde
        if self.menu.terminado:
            seleccion = self.menu.seleccion
            if seleccion == "creditos":
                resultado = self.mostrar_creditos()
                if resultado == "salir":
                    return "salir"
                else:
                    return "menu"
            elif seleccion == "controles":
                resultado = self.mostrar_controles()
                if resultado == "salir":
                    return "salir"
                else:
                    return "menu"
            elif seleccion == "jugar":
                return "jugar"
            elif seleccion == "salir":
                return "salir"
        return None

    @property
    def terminado(self):
        return self.menu.terminado

    @property
    def seleccion(self):
        return self.menu.seleccion

    def reiniciar(self):
        self.menu.reiniciar()

    def mostrar_creditos(self):
        texto = self.menu.obtener_texto_creditos()
        self.vista_menu.mostrar_creditos(texto)
        esperando = True
        import pygame
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.menu.terminado = True
                    self.menu.seleccion = "salir"
                    return "salir"
                if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                    esperando = False
                    break
            pygame.time.delay(10)
        self.menu.reiniciar()
        return "menu"

    def mostrar_controles(self):
        texto = self.menu.obtener_texto_controles()
        self.vista_menu.mostrar_creditos(texto)
        esperando = True
        import pygame
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.menu.terminado = True
                    self.menu.seleccion = "salir"
                    return "salir"
                if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                    esperando = False
                    break
            pygame.time.delay(10)
        self.menu.reiniciar()
        return "menu"

    def mostrar_game_over(self):
        # Lógica para mostrar la pantalla de game over y un botón de nueva partida
        # Por ejemplo, puedes cambiar el estado interno y dibujar la pantalla de game over en el método dibujar
        self.estado = "game_over"
        # Aquí puedes mostrar un mensaje y un botón para reiniciar
