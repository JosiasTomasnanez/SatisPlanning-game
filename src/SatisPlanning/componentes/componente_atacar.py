import pygame
import SatisPlanning.constantes as ct

class ComponenteAtacar:
    def __init__(self, arma):
        self.arma = arma

    def atacar(self, arma, personaje):
        # El ataque comienza desde la mitad del personaje
        mitad_pj_x = personaje.x + personaje.ancho // 2
        if personaje.direccion == 1:
            ataque_x = mitad_pj_x
        else:
            ataque_x = mitad_pj_x - arma.ancho
        ataque_y = personaje.y + (personaje.alto - arma.alto) // 2
        ruta_img = getattr(arma, "ruta_imagen", ct.RUTA_MANO)
        arma_copia = type(arma)(
            ataque_x, ataque_y, arma.ancho, arma.alto, arma.danio, ruta_img
        )
        ataque_hitbox = arma_copia.hitbox

        mundo = personaje.mundo
        for enemigo in mundo.obtener_enemigos():
            if ataque_hitbox.colliderect(enemigo.hitbox):
                enemigo.notificar_colision(arma_copia)

        # Calcula la duración del ataque según la animación del arma
        frames_por_sprite = getattr(arma, "_frames_por_sprite", 4)  # Usa 4 por defecto, o el valor real
        total_sprites = len(getattr(arma, "sprites", [])) or 1
        personaje.atacando = True
        personaje.tiempo_ataque = frames_por_sprite * total_sprites
        arma.iniciar_animacion_ataque()
