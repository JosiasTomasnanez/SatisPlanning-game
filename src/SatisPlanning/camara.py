import SatisPlanning.constantes as ct

class Camara:

    ancho_pantalla = ct.ANCHO
    alto_pantalla = ct.ALTO

    def __init__(self):
        self.desplazamiento_x = 0
        self.desplazamiento_y = 0

    def actualizar(self, objetivo_x, objetivo_y):
        """
        Actualiza el desplazamiento de la cámara para centrarse en la posición objetivo.
        """
        self.desplazamiento_x = objetivo_x - (ct.ANCHO // 2)
        self.desplazamiento_y = objetivo_y - (ct.ALTO // 2)

    def aplicar(self, x, y):
        """
        Aplica el desplazamiento de la cámara a una posición dada.
        """
        return x - self.desplazamiento_x, y - self.desplazamiento_y

#Esta clase va a ser mas compleja , para poder realizar zoom usando teclas, hay que ver como se puede implementar eso en un futuro, quizas cambiando el valor del tamaño de los bloques y a la vez el valor del tamaño de los chunks a voluntad
