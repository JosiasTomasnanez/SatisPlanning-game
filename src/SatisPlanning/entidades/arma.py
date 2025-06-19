from SatisPlanning.entidades.objeto import Objeto
from SatisPlanning.componentes.componente_atacar import ComponenteAtacar
import time

class Arma(Objeto):
    def __init__(self, x, y, ancho=30, alto=30, danio=20, ruta_imagen="assets/arma.png", sprites=None, frames_por_sprite=4):
        super().__init__(x, y, ancho, alto, ruta_imagen, dinamico=False, tangible=False, ajustar_hitbox=False)
        self.danio = danio
        self.es_arma = True  # Identifica el objeto como arma
        self.componente_atacar = ComponenteAtacar(self)
        self.cooldown_ataque = 0.5  # segundos, puedes ajustar este valor
        self.ultimo_ataque = 0

        # Animación de ataque (genérico para cualquier arma)
        self.sprites = sprites
        self.componente_animacion = None  # Se debe inicializar en la subclase si hay sprites
        self.animacion_ataque_en_curso = False
        self._contador_anim_ataque = 0
        self._frames_por_sprite = frames_por_sprite

    def atacar(self, personaje):
        ahora = time.time()
        if ahora - self.ultimo_ataque < self.cooldown_ataque:
            return  # No permite atacar aún, cooldown activo
        self.ultimo_ataque = ahora
        self.componente_atacar.atacar(self, personaje)

    def iniciar_animacion_ataque(self):
        if self.componente_animacion:
            self.componente_animacion.sprite_actual = 0
            self.componente_animacion.contador_animacion = 0
            self.animacion_ataque_en_curso = True
            self._contador_anim_ataque = 0

    def actualizar_animacion_ataque(self):
        if self.animacion_ataque_en_curso and self.componente_animacion:
            self._contador_anim_ataque += 1
            if self._contador_anim_ataque >= self._frames_por_sprite:
                self.componente_animacion.avanzar_sprite()
                self._contador_anim_ataque = 0
                if self.componente_animacion.sprite_actual == len(self.sprites) - 1:
                    self.animacion_ataque_en_curso = False
