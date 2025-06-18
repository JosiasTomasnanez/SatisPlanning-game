import random
from .entidades.Zombie_enemy import Zombie

class GeneradorMonstruos:
    def __init__(self, distancia_persecucion):
        self.distancia_persecucion = distancia_persecucion

    def crear_monstruo(self, x, y, nivel=1):
        """
        Crea un monstruo acorde al nivel. Por ahora, solo Zombie, pero ajusta la velocidad.
        """
        zombie = Zombie(x, y, 40, 40, distancia_persecucion=self.distancia_persecucion)
        zombie.velocidad = int(zombie.velocidad * (1 + nivel * 0.3))  # Aumenta la velocidad según el nivel
        return zombie

    def crear_boss(self, x, y, nivel=1):
        """
        Crea un boss acorde al nivel. Por ahora, solo Zombie, pero con más velocidad y flag de boss.
        """
        boss = Zombie(x, y, 70, 70, distancia_persecucion=self.distancia_persecucion)
        boss.velocidad = int(boss.velocidad * (1 + nivel * 0.7))  # Boss más rápido
        boss.es_boss = True  # <-- Esto es necesario para pasar el test
        return boss

    # Puedes agregar más métodos para crear otros tipos de monstruos/bosses
