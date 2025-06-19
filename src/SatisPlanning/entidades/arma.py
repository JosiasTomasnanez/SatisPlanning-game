from SatisPlanning.entidades.objeto import Objeto

class Arma(Objeto):
    def __init__(self, x, y, ancho=30, alto=30, danio=20, ruta_imagen="assets/arma.png"):
        super().__init__(x, y, ancho, alto, ruta_imagen, dinamico=False, tangible=False, ajustar_hitbox=False)
        self.danio = danio
        self.es_arma = True  # Identifica el objeto como arma
