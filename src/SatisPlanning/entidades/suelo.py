from SatisPlanning.entidades.objeto import Objeto

class Suelo(Objeto):
    def __init__(self, x, y, ancho, alto, ruta_imagen):
        """
        Inicializa un objeto de tipo Suelo que actúa como un sensor.

        :param x: Posición X del suelo.
        :param y: Posición Y del suelo.
        :param ancho: Ancho del suelo.
        :param alto: Altura del suelo.
        :param ruta_imagen: Ruta de la imagen en la carpeta assets.
        """
        super().__init__(x, y, ancho, alto, ruta_imagen, dinamico=False, tangible=True)
        # Configuramos todos los fixtures como sensores



