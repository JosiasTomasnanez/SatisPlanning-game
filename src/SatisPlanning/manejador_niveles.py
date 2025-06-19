from .generador_monstruos import GeneradorMonstruos

class EstadoNivel:
    def actualizar(self, manejador, personaje):
        raise NotImplementedError

class EstadoJugando(EstadoNivel):
    def actualizar(self, manejador, personaje):
        # Elimina enemigos muertos y aumenta el contador
        enemigos_vivos = []
        for e in manejador.enemigos:
            if getattr(e, "muerto", False):
                manejador.enemigos_derrotados += 1
            else:
                enemigos_vivos.append(e)
        manejador.enemigos = enemigos_vivos

        if manejador.enemigos_derrotados >= 5:
            manejador.cambiar_estado(EstadoBoss())
            manejador.spawn_boss(personaje)
        else:
            manejador.spawn_enemigos(personaje)
        manejador._actualizar_enemigos(personaje)

class EstadoBoss(EstadoNivel):
    def actualizar(self, manejador, personaje):
        # Buscar el boss antes de filtrar enemigos
        boss = next((e for e in manejador.enemigos if getattr(e, "es_boss", False)), None)

        # Elimina enemigos muertos
        enemigos_vivos = []
        for e in manejador.enemigos:
            if not getattr(e, "muerto", False):
                enemigos_vivos.append(e)
        manejador.enemigos = enemigos_vivos
        if boss and getattr(boss, "muerto", False):
            manejador.nivel_actual += 1
            manejador.enemigos_derrotados = 0
            manejador.enemigos = [e for e in manejador.enemigos if not getattr(e, "es_boss", False)]
            manejador.spawn_frame_counter = 0  # Reinicia el contador de spawn
            manejador.cambiar_estado(EstadoJugando())
            return
        manejador._actualizar_enemigos(personaje)

class ManejadorNiveles:
    def __init__(
        self,
        generador_monstruos,
        spawn_frame_interval,
        max_enemigos,
        spawn_dist_min,
        spawn_dist_max,
        despawn_dist
    ):
        self.generador_monstruos = generador_monstruos
        self.nivel_actual = 1
        self.enemigos = []
        self.enemigos_derrotados = 0
        self.mundo = None  # Se setea luego con set_mundo

        # Lógica de respawn
        self.spawn_frame_counter = 0
        self.spawn_frame_interval = spawn_frame_interval
        self.max_enemigos = max_enemigos
        self.spawn_dist_min = spawn_dist_min
        self.spawn_dist_max = spawn_dist_max
        self.despawn_dist = despawn_dist

        self.estado = EstadoJugando()

    def set_mundo(self, mundo):
        self.mundo = mundo

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def actualizar(self, personaje):
        self.estado.actualizar(self, personaje)

    def _actualizar_enemigos(self, personaje):
        enemigos_actualizados = []
        for enemigo in self.enemigos:
            dx = enemigo.x - personaje.x
            dy = enemigo.y - personaje.y
            distancia = (dx ** 2 + dy ** 2) ** 0.5
            if distancia < self.despawn_dist:
                # Cambia el comportamiento de movimiento según la distancia
                if hasattr(enemigo, "set_comportamiento_movimiento"):
                    # Usar la distancia de activación definida en el enemigo
                    distancia_activacion = getattr(enemigo.movimiento_persecucion, "distancia_activacion", 200)
                    if abs(dx) < distancia_activacion:
                        enemigo.set_comportamiento_movimiento(enemigo.movimiento_persecucion)
                    else:
                        enemigo.set_comportamiento_movimiento(enemigo.movimiento_aleatorio)
                enemigo.actualizar()
                enemigos_actualizados.append(enemigo)
        self.enemigos = enemigos_actualizados

    def spawn_enemigos(self, personaje):
        import random
        # Controla el tiempo entre spawns
        self.spawn_frame_counter += 1
        if self.spawn_frame_counter < self.spawn_frame_interval:
            return
        self.spawn_frame_counter = 0

        # Máximo de enemigos activos
        if len(self.enemigos) >= self.max_enemigos:
            return

        px, py = personaje.x, personaje.y
        distancia = random.uniform(self.spawn_dist_min, self.spawn_dist_max)
        x = px + distancia * random.choice([-1, 1])
        y = py + random.randint(-100, 100)
        monstruo = self.generador_monstruos.crear_monstruo(x, y, nivel=self.nivel_actual)
        monstruo.set_mundo(self.mundo)
        # Ajustar posición si colisiona
        while self.mundo.colisiona(monstruo.hitbox, monstruo):
            y -= 1
            monstruo.hitbox.y = y
            monstruo.y = y
        self.enemigos.append(monstruo)

    def spawn_boss(self, personaje):
        px, py = personaje.x, personaje.y
        x = px + 400
        y = py
        boss = self.generador_monstruos.crear_boss(x, y, nivel=self.nivel_actual)
        boss.set_mundo(self.mundo)
        # Ajustar posición si colisiona con el suelo u otro objeto
        while self.mundo.colisiona(boss.hitbox, boss):
            y -= 1
            boss.hitbox.y = y
            boss.y = y
        self.enemigos.append(boss)

    def obtener_enemigos(self):
        return self.enemigos
