class Menu:
    def __init__(self, opciones):
        self.opciones = opciones
        self.opcion_seleccionada = 0
        self.terminado = False
        self.seleccion = None  # "jugar", "controles", "creditos", "salir"

    def mover_arriba(self):
        self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)

    def mover_abajo(self):
        self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)

    def seleccionar(self):
        self.terminado = True
        if self.opcion_seleccionada == 0:
            self.seleccion = "jugar"
        elif self.opcion_seleccionada == 1:
            self.seleccion = "controles"
        elif self.opcion_seleccionada == 2:
            self.seleccion = "creditos"
        elif self.opcion_seleccionada == 3:
            self.seleccion = "salir"

    def seleccionar_por_indice(self, indice):
        self.opcion_seleccionada = indice
        self.seleccionar()

    def reiniciar(self):
        self.terminado = False
        self.seleccion = None
        self.opcion_seleccionada = 0

    def obtener_texto_creditos(self):
        """
        Devuelve un texto de ejemplo para los créditos.
        """
        return (
            "Créditos\n"
            "Programadores:\n"
            "   Josias Ñañez\n"
            "   Lautaro Callovi\n"
            "   Nicolás Piñera\n"
            "   Dario Zelaya\n"
            "Diseño de personaje:\n"
            "   Franco Choque\n\n"
            "Gracias por jugar a SatisPlanning!"
        )

    def obtener_texto_controles(self):
        """
        Devuelve un texto de ejemplo para los controles del juego.
        """
        return (
            "Controles\n"
            "Mover: Flechas o WASD\n"
            "Inventario: I\n"
            "Seleccionar: Enter o Click\n"
            "Pantalla completa: F11\n"
            "Salir al menú: ESC\n"
            "Salir del juego: Cerrar ventana o desde el menú\n"
        )
