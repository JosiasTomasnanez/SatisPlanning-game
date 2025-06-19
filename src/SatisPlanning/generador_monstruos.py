from .entidades.enemigo import Enemigo
import SatisPlanning.constantes as ct

SPRITES_POR_NIVEL = {
    1: ct.SPRITES_ENEMIGO,
    2: ct.SPRITES_ENEMIGO_2,
    3: ct.SPRITES_ENEMIGO_3,
    # ...
}

SPRITES_BOSS_POR_NIVEL = {
    1: ct.SPRITES_BOSS_1,
    2: ct.SPRITES_BOSS_2,
    3: ct.SPRITES_BOSS_3,
    # ...
}

class GeneradorMonstruos:
    def __init__(self, distancia_persecucion):
        self.distancia_persecucion = distancia_persecucion

    def crear_monstruo(self, x, y, nivel=1):
        """
        Crea un monstruo acorde al nivel.
        """
        sprites = SPRITES_POR_NIVEL.get(nivel, ct.SPRITES_ENEMIGO)
        velocidad = 1 * (1 + nivel * 0.5)
        vida = 5 + nivel * 30
        danio = 5 + nivel * 5
        enemigo = Enemigo(x, y, 40, 40, distancia_persecucion=self.distancia_persecucion, sprites=sprites)
        enemigo.velocidad = velocidad
        enemigo.vida = vida
        enemigo.danio = danio
        return enemigo

    def crear_boss(self, x, y, nivel=1):
        """
        Crea un boss acorde al nivel.   
        """
        sprites = SPRITES_BOSS_POR_NIVEL.get(nivel, ct.SPRITES_BOSS_1)
        velocidad = 2 * (1 + nivel*0.3)
        vida = 50 + nivel * 100
        danio = 20 + nivel * 10
        boss = Enemigo(x, y, 70, 70, distancia_persecucion=self.distancia_persecucion, sprites=sprites)
        boss.velocidad = velocidad
        boss.vida = vida
        boss.danio = danio
        boss.es_boss = True
        return boss

    # Puedes agregar más métodos para crear otros tipos de monstruos/bosses
