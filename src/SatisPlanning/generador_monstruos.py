import random
from .entidades.Zombie_enemy import Zombie

class GeneradorMonstruos:
    def __init__(self, spawn_frame_interval, max_enemigos, spawn_dist_min, spawn_dist_max, despawn_dist, distancia_persecucion):
        self.spawn_frame_counter = 0
        self.spawn_frame_interval = spawn_frame_interval
        self.max_enemigos = max_enemigos
        self.spawn_dist_min = spawn_dist_min
        self.spawn_dist_max = spawn_dist_max
        self.despawn_dist = despawn_dist
        self.distancia_persecucion = distancia_persecucion
        self.enemigos = []

    def actualizar(self, personaje, mundo):
        """
        Actualiza la lógica de spawn y despawn de enemigos.
        :param personaje: El personaje principal (para obtener su posición)
        :param mundo: El mundo, para pasar a los enemigos nuevos
        """
        # Spawn automático de enemigos fuera de pantalla
        self.spawn_frame_counter += 1
        if self.spawn_frame_counter >= self.spawn_frame_interval and len(self.enemigos) < self.max_enemigos:
            self.spawn_frame_counter = 0
            px, py = personaje.x, personaje.y
            distancia = random.uniform(self.spawn_dist_min, self.spawn_dist_max)
            x = px + distancia * random.choice([-1, 1])
            y = py + random.randint(-100, 100)
            zombie = Zombie(x, y, 40, 40, distancia_persecucion=self.distancia_persecucion)
            zombie.set_mundo(mundo)
            # Ajustar la posición en Y si colisiona con el suelo
            
            while mundo.colisiona(zombie.hitbox, zombie):
                y -= 1
                zombie.hitbox.y = y
                zombie.y = y

            self.enemigos.append(zombie)

        # Actualizar enemigos y eliminar los que se alejan demasiado
        enemigos_actualizados = []
        for enemigo in self.enemigos:
            dx = enemigo.x - personaje.x
            dy = enemigo.y - personaje.y
            distancia = (dx ** 2 + dy ** 2) ** 0.5
            if distancia < self.despawn_dist:
                if hasattr(enemigo, "comportamiento_movimiento"):
                    if abs(dx) < 200:
                        enemigo.set_comportamiento_movimiento(enemigo.movimiento_persecucion)
                    else:
                        enemigo.set_comportamiento_movimiento(enemigo.movimiento_aleatorio)
                enemigo.actualizar()
                enemigos_actualizados.append(enemigo)
        self.enemigos = enemigos_actualizados

    def obtener_enemigos(self):
        return self.enemigos
