class GestorPresentadores:
    def __init__(self, presentador_menu, vista_menu, presentador_juego, vista_juego):
        self.presentador_menu = presentador_menu
        self.vista_menu = vista_menu
        self.presentador_juego = presentador_juego
        self.vista_juego = vista_juego
        self.presentador_actual = presentador_menu
        self.vista_actual = vista_menu

    def cambiar_a_menu(self):
        self.presentador_actual = self.presentador_menu
        self.vista_actual = self.vista_menu
        self.presentador_menu.reiniciar()  # Reinicia el estado del menú

    def cambiar_a_juego(self):
        self.presentador_actual = self.presentador_juego
        self.vista_actual = self.vista_juego

    def obtener_presentador_actual(self):
        return self.presentador_actual

    def obtener_vista_actual(self):
        return self.vista_actual
