import pygame
from SatisPlanning.entidades.arma import Arma
from SatisPlanning.entidades.mano import Mano
import SatisPlanning.constantes as ct

class ComponenteAtacar:
    def __init__(self, personaje):
        self.personaje = personaje

    def atacar(self, arma):
        # El ataque comienza desde la mitad del personaje
        mitad_pj_x = self.personaje.x + self.personaje.ancho // 2
        if self.personaje.direccion == 1:
            ataque_x = mitad_pj_x
        else:
            ataque_x = mitad_pj_x - arma.ancho
        ataque_y = self.personaje.y + (self.personaje.alto - arma.alto) // 2
        ruta_img = getattr(arma, "ruta_imagen", ct.RUTA_MANO)
        arma = arma.__class__(
            ataque_x, ataque_y, arma.ancho, arma.alto, arma.danio, ruta_img
        )
        ataque_hitbox = arma.hitbox

        mundo = self.personaje.mundo
        for enemigo in mundo.obtener_enemigos():
            if ataque_hitbox.colliderect(enemigo.hitbox):
                enemigo.notificar_colision(arma)

        self.personaje.atacando = True
        self.personaje.tiempo_ataque = 10  # frames de animación de ataque (ajusta a gusto)
