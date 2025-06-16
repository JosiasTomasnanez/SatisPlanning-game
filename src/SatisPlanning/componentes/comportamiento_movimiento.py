import random

class ComportamientoMovimiento:
    """Interfaz de estrategia de movimiento."""
    def mover(self, enemigo):
        raise NotImplementedError

class MovimientoAleatorio(ComportamientoMovimiento):
    """Movimiento aleatorio para un enemigo."""
    def __init__(self):
        self.tiempo_cambio_direccion = 0
        self.duracion_direccion = random.randint(30, 90)
        self.direccion_aleatoria = random.choice([-1, 0, 1])
        self.frames_bloqueado = 0

    def mover(self, enemigo):
        self.tiempo_cambio_direccion += 1
        if self.tiempo_cambio_direccion > self.duracion_direccion:
            self.direccion_aleatoria = random.choice([-1, 0, 1])
            self.duracion_direccion = random.randint(30, 90)
            self.tiempo_cambio_direccion = 0

        salto_aleatorio = random.random() < 0.02  # 2% de probabilidad de salto aleatorio por frame

        if self.direccion_aleatoria != 0:
            dx = self.direccion_aleatoria * 1  # velocidad reducida
            nueva_hitbox = enemigo.hitbox.move(dx, 0)
            if enemigo.mundo.colisiona(nueva_hitbox, enemigo):
                self.frames_bloqueado += 1
                if (enemigo.en_el_suelo or abs(enemigo.vel_y) < 1.5 or self.frames_bloqueado > 8 or salto_aleatorio):
                    enemigo.vel_y = -enemigo.mundo.ct.FUERZA_SALTO if hasattr(enemigo.mundo, "ct") else -12  # valor por defecto
                    enemigo.en_el_suelo = False
                    self.frames_bloqueado = 0
            else:
                self.frames_bloqueado = 0
                # Salto aleatorio aunque no esté bloqueado
                if (enemigo.en_el_suelo or abs(enemigo.vel_y) < 1.5) and salto_aleatorio:
                    enemigo.vel_y = -enemigo.mundo.ct.FUERZA_SALTO if hasattr(enemigo.mundo, "ct") else -12  # valor por defecto
                    enemigo.en_el_suelo = False
        else:
            self.frames_bloqueado = 0
            # Salto aleatorio aunque esté quieto
            if (enemigo.en_el_suelo or abs(enemigo.vel_y) < 1.5) and salto_aleatorio:
                enemigo.vel_y = -enemigo.mundo.ct.FUERZA_SALTO if hasattr(enemigo.mundo, "ct") else -12  # valor por defecto
                enemigo.en_el_suelo = False

        enemigo.vel_x = self.direccion_aleatoria * 1  # velocidad reducida
        teclas_falsas = {
            100: self.direccion_aleatoria == 1,
            97: self.direccion_aleatoria == -1,
            119: False,
            32: False
        }
        enemigo.componente_mover.actualizar(teclas_falsas)

class MovimientoPersecucion(ComportamientoMovimiento):
    """Movimiento de persecución hacia el jugador si está cerca."""
    def __init__(self, distancia_activacion):
        self.distancia_activacion = distancia_activacion
        self.frames_bloqueado = 0

    def mover(self, enemigo):
        jugador = enemigo.mundo.personaje
        dx = jugador.x - enemigo.x
        salto_aleatorio = random.random() < 0.02  # 2% de probabilidad de salto aleatorio por frame

        if abs(dx) < self.distancia_activacion:
            if dx > 0:
                direccion = 1
            else:
                direccion = -1

            # Detectar si está bloqueado por una pared
            if direccion != 0:
                dx_mov = direccion * 1  # velocidad corregida
                nueva_hitbox = enemigo.hitbox.move(dx_mov, 0)
                if enemigo.mundo.colisiona(nueva_hitbox, enemigo):
                    self.frames_bloqueado += 1
                    if (enemigo.en_el_suelo or abs(enemigo.vel_y) < 1.5 or self.frames_bloqueado > 8 or salto_aleatorio):
                        enemigo.vel_y = -enemigo.mundo.ct.FUERZA_SALTO if hasattr(enemigo.mundo, "ct") else -12
                        enemigo.en_el_suelo = False
                        self.frames_bloqueado = 0
                else:
                    self.frames_bloqueado = 0
                    # Salto aleatorio aunque no esté bloqueado
                    if (enemigo.en_el_suelo or abs(enemigo.vel_y) < 1.5) and salto_aleatorio:
                        enemigo.vel_y = -enemigo.mundo.ct.FUERZA_SALTO if hasattr(enemigo.mundo, "ct") else -12
                        enemigo.en_el_suelo = False
            else:
                self.frames_bloqueado = 0
                # Salto aleatorio aunque esté quieto
                if (enemigo.en_el_suelo or abs(enemigo.vel_y) < 1.5) and salto_aleatorio:
                    enemigo.vel_y = -enemigo.mundo.ct.FUERZA_SALTO if hasattr(enemigo.mundo, "ct") else -12
                    enemigo.en_el_suelo = False

            enemigo.vel_x = direccion * 1  # velocidad corregida
            teclas_falsas = {
                100: direccion == 1,
                97: direccion == -1,
                119: False,
                32: False
            }
            enemigo.componente_mover.actualizar(teclas_falsas)
        else:
            self.frames_bloqueado = 0
            # Salto aleatorio aunque esté fuera de rango de persecución
            if (enemigo.en_el_suelo or abs(enemigo.vel_y) < 1.5) and salto_aleatorio:
                enemigo.vel_y = -enemigo.mundo.ct.FUERZA_SALTO if hasattr(enemigo.mundo, "ct") else -12
                enemigo.en_el_suelo = False
            teclas_falsas = {100: False, 97: False, 119: False, 32: False}
            enemigo.componente_mover.actualizar(teclas_falsas)
