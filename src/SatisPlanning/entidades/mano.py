from SatisPlanning.entidades.arma import Arma
import SatisPlanning.constantes as ct
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion

class Mano(Arma):
    def __init__(self, x=0, y=0, ancho=50, alto=60, danio=25, ruta_imagen=ct.RUTA_MANO, sprites=None):
        if sprites is None:
            sprites = ct.SPRITES_MANO
        super().__init__(x, y, ancho, alto, danio, ruta_imagen, sprites=sprites, frames_por_sprite=4)
        self.cooldown_ataque = 0.4  # cooldown propio de la mano
        self.componente_animacion = ComponenteAnimacion(self, sprites)