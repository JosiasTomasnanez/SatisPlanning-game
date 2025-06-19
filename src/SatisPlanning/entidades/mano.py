from SatisPlanning.entidades.arma import Arma
import SatisPlanning.constantes as ct

class Mano(Arma):
    def __init__(self, x=0, y=0, ancho=50, alto=60, danio=10, ruta_imagen=ct.RUTA_MANO):
        super().__init__(x, y, ancho, alto, danio, ruta_imagen)
