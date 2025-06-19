import random
import abc

class EstrategiaMovimiento(abc.ABC):
    """Interfaz de estrategia de movimiento."""
    @abc.abstractmethod
    def mover(self, enemigo):
        pass

class EstrategiaMovimientoAleatorio(EstrategiaMovimiento):
    """Movimiento aleatorio para un enemigo."""
    def __init__(self):
        self.tiempo_cambio_direccion = 0
        self.duracion_direccion = random.randint(30, 90)
        self.direccion_aleatoria = random.choice([-1, 0, 1])

    def mover(self, enemigo):
        # Cambio de dirección aleatorio
        self.tiempo_cambio_direccion += 1
        if self.tiempo_cambio_direccion > self.duracion_direccion:
            self.direccion_aleatoria = random.choice([-1, 0, 1])
            self.duracion_direccion = random.randint(30, 90)
            self.tiempo_cambio_direccion = 0

        # Detectar si hay pared adelante
        if self.direccion_aleatoria != 0:
            dx = self.direccion_aleatoria * enemigo.velocidad
            nueva_hitbox = enemigo.hitbox.move(dx, 0)
            hay_pared = enemigo.mundo.colisiona(nueva_hitbox, enemigo)
        else:
            hay_pared = False

        # Decidir si salta (por pared o aleatoriamente)
        salto = hay_pared or random.random() < 0.02  # Salta si hay pared o 2% de probabilidad

        # Simular teclas para ComponenteMover
        teclas_falsas = {
            100: self.direccion_aleatoria == 1,   # d
            97: self.direccion_aleatoria == -1,   # a
            119: salto,                           # w
            32: False                             # space
        }
        enemigo.componente_mover.actualizar(teclas_falsas)

class EstrategiaMovimientoPersecucion(EstrategiaMovimiento):
    """Movimiento de persecución hacia el jugador si está cerca."""
    def __init__(self, distancia_activacion):
        self.distancia_activacion = distancia_activacion

    def mover(self, enemigo):
        # Calcular dirección hacia el jugador
        jugador = enemigo.mundo.personaje
        dx = jugador.x - enemigo.x
        
        # Decidir dirección basada en la distancia
        if abs(dx) < self.distancia_activacion and abs(dx) > 1:
            direccion = 1 if dx > 0 else -1
        else:
            direccion = 0

        # Detectar si hay pared adelante
        if direccion != 0:
            dx = direccion * enemigo.velocidad
            nueva_hitbox = enemigo.hitbox.move(dx, 0)
            hay_pared = enemigo.mundo.colisiona(nueva_hitbox, enemigo)
        else:
            hay_pared = False

        # Decidir si salta (por pared o aleatoriamente)
        salto = hay_pared or random.random() < 0.02  # Salta si hay pared o 2% de probabilidad

        # Simular teclas para ComponenteMover
        teclas_falsas = {
            100: direccion == 1,    # d
            97: direccion == -1,    # a
            119: salto,            # w
            32: False              # space
        }
        enemigo.componente_mover.actualizar(teclas_falsas)
