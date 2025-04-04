from Objeto import Objeto

class Suelo(Objeto):
    def __init__(self, x, y, width, height, image_path):
        """
        Inicializa un objeto de tipo Suelo que actúa como un sensor.

        :param x: Posición X del suelo.
        :param y: Posición Y del suelo.
        :param width: Ancho del suelo.
        :param height: Altura del suelo.
        :param image_path: Ruta de la imagen en la carpeta assets.
        :param world: Instancia de Box2D.b2World para asociar el cuerpo físico.
        """
        super().__init__(x, y, width, height, image_path, dinamico=False)
        #Configuramos todos los fixtures como sensores
       
