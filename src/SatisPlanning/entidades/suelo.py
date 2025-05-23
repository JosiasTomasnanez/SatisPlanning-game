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

# en principio esta bien esta clase, bien general, pero los que hereden de esta clase pueden implementar cosas como buff ante ciertos materiales de suelos al perosnaje, o como en terraria, que la piedra infernal queme al personaje, pero esas son extenciones hacia las subclases

