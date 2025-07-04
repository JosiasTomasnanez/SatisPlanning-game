import pygame
import os

class Objeto:
    def __init__(self, x, y, ancho, alto, ruta_imagen, dinamico, tangible=True, ajustar_hitbox=True):
        """
        Inicializa un objeto con posición, hitbox, una imagen y un cuerpo físico en el mundo.

        :param x: Posición X del objeto.
        :param y: Posición Y del objeto.
        :param ancho: Ancho del hitbox.
        :param alto: Altura del hitbox.
        :param ruta_imagen: Ruta de la imagen en la carpeta assets.
        :param dinamico: Define si el objeto es dinámico (True) o estático (False).
        :param tangible: Define si el objeto es tangible (True) o no (False).
        :param ajustar_hitbox: Define si se ajusta la hitbox con desplazamiento (True) o sin desplazamiento (False).
        """
        self.x, self.y = x, y
        self.vel_x = self.vel_y = 0
        self.direccion = 1
        self.ancho = ancho
        self.alto = alto
        ruta_final = ruta_imagen
        if not os.path.isabs(ruta_imagen):
            ruta_final = os.path.join(os.path.dirname(__file__), "assets", ruta_imagen)
        self.ruta_final = ruta_final  # Guarda la ruta absoluta/final para comparación de tipo
        self.imagen = pygame.image.load(ruta_final)
        self.imagen = pygame.transform.scale(self.imagen, (ancho, alto))  # Ajustar tamaño de la imagen
        self.dinamico = dinamico
        self.tangible = tangible  # Indica si el objeto es tangible
        self.componentes = []  # Lista de componentes asociadas al objeto

        if ajustar_hitbox:
            # Reducción horizontal de la hitbox para personajes y enemigos
            from SatisPlanning.entidades.personaje_jugador import PersonajeJugador
            from SatisPlanning.entidades.enemigo import Enemigo
            if isinstance(self, PersonajeJugador) or isinstance(self, Enemigo):
                hitbox_ancho = int(ancho * 0.6)
                hitbox_x = x + (ancho - hitbox_ancho) // 2
                self.hitbox = pygame.Rect(hitbox_x, y + 20, hitbox_ancho, alto)
            else:
                # La hitbox se ajusta con un desplazamiento respecto a la posición del objeto
                self.hitbox = pygame.Rect(x + 17, y + 20, ancho - 4, alto)
        else:
            # Hitbox exacta al tamaño y posición del objeto (para armas)
            self.hitbox = pygame.Rect(x, y, ancho, alto)

    def dibujar(self, pantalla):
        """
        Dibuja el objeto en la pantalla y su hitbox para depuración.
        """
        pantalla.blit(self.imagen, (self.x, self.y))
        # Dibuja el hitbox en rojo (opcional para depuración)
        pygame.draw.rect(pantalla, (255, 0, 0), self.hitbox, 2)

    def actualizar_posicion(self, x, y):
        """
        Actualiza la posición del objeto y centra su hitbox.

        :param x: Nueva posición X.
        :param y: Nueva posición Y.
        """
        self.x = x
        self.y = y
        # Ajustar la hitbox respetando los desplazamientos iniciales
        self.hitbox.topleft = (self.x + 17, self.y + 20)

    def dibujar_con_desplazamiento(self, pantalla, desplazamiento_x, desplazamiento_y):
        """
        Dibuja el objeto en la pantalla ajustado por un desplazamiento.

        :param pantalla: Superficie de pygame donde se dibuja el objeto.
        :param desplazamiento_x: Desplazamiento en el eje X.
        :param desplazamiento_y: Desplazamiento en el eje Y.
        """
        pantalla.blit(self.imagen, (desplazamiento_x, desplazamiento_y))
        # Para depuración, se puede dibujar la hitbox desplazada
        # pygame.draw.rect(pantalla, (255, 0, 0), self.hitbox.move(desplazamiento_x - self.x, desplazamiento_y - self.y), 2)

    def agregar_componente(self, componente):
        """
        Agrega un componente al objeto.

        :param componente: Instancia de una subclase de Componente.
        """
        self.componentes.append(componente)

    def notificar_colision(self, objeto):
        """
        Notifica al personaje sobre una colisión con otro objeto.

        :param objeto: Objeto con el que colisiona.
        """
        pass

    def actualizar(self, dt):
        """
        Actualiza todos los componentes del objeto.

        :param dt: Delta time (tiempo transcurrido desde el último frame).
        """
        for componente in self.componentes:
            componente.actualizar(dt)

    def tipo_igual(self, otro):
        """
        Determina si este objeto es del mismo tipo que otro.
        Compara la clase y la ruta final de la imagen.
        """
        return type(self) == type(otro) and getattr(self, "ruta_final", None) == getattr(otro, "ruta_final", None)


