from SatisPlanning.entidades.arma import Arma
from SatisPlanning.componentes.componente_animacion import ComponenteAnimacion
import SatisPlanning.constantes as ct

class Espada(Arma):
    def __init__(self, x=0, y=0, ancho=60, alto=65, danio=30, sprites=ct.SPRITES_ESPADA):
        ruta_imagen = ct.obtener_ruta_asset("espada/e1.png")
        super().__init__(x, y, ancho, alto, danio, ruta_imagen=ruta_imagen, sprites=sprites, frames_por_sprite=4)
        self.cooldown_ataque = 0.5  # cooldown propio de la espada
        self.componente_animacion = ComponenteAnimacion(self, self.sprites)
