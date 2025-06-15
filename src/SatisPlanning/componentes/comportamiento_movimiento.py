import random

class ComportamientoMovimiento:
    def mover(self, enemigo):
        raise NotImplementedError

class MovimientoAleatorio(ComportamientoMovimiento):
    def __init__(self):
        self.tiempo_cambio_direccion = 0
        self.duracion_direccion = random.randint(30, 90)
        self.direccion_aleatoria = random.choice([-1, 0, 1])

    def mover(self, enemigo):
        self.tiempo_cambio_direccion += 1
        if self.tiempo_cambio_direccion > self.duracion_direccion:
            self.direccion_aleatoria = random.choice([-1, 0, 1])
            self.duracion_direccion = random.randint(30, 90)
            self.tiempo_cambio_direccion = 0
        enemigo.vel_x = self.direccion_aleatoria * 2
        teclas_falsas = {
            100: self.direccion_aleatoria == 1,  # pygame.K_d
            97: self.direccion_aleatoria == -1, # pygame.K_a
            119: False, # pygame.K_w
            32: False   # pygame.K_SPACE
        }
        enemigo.componente_mover.actualizar(teclas_falsas)

class MovimientoPersecucion(ComportamientoMovimiento):
    def __init__(self, distancia_activacion=120):
        self.distancia_activacion = distancia_activacion

    def mover(self, enemigo):
        # Perseguir al jugador si está cerca
        jugador = enemigo.mundo.personaje
        dx = jugador.x - enemigo.x
        if abs(dx) < self.distancia_activacion:
            if dx > 0:
                direccion = 1
            else:
                direccion = -1
            enemigo.vel_x = direccion * 2
            teclas_falsas = {
                100: direccion == 1,  # pygame.K_d
                97: direccion == -1, # pygame.K_a
                119: False, # pygame.K_w
                32: False   # pygame.K_SPACE
            }
            enemigo.componente_mover.actualizar(teclas_falsas)
        else:
            # Si el jugador no está cerca, quedarse quieto
            teclas_falsas = {100: False, 97: False, 119: False, 32: False}
            enemigo.componente_mover.actualizar(teclas_falsas)
