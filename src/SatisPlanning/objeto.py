import pygame
import SatisPlanning.constantes as ct

class Objeto:
    def __init__(self, x, y, ancho, alto, ruta_imagen, dinamico):
        """
        Inicializa un objeto con posición, hitbox, una imagen y un cuerpo físico en el mundo.

        :param x: Posición X del objeto.
        :param y: Posición Y del objeto.
        :param ancho: Ancho del hitbox.
        :param alto: Altura del hitbox.
        :param ruta_imagen: Ruta de la imagen en la carpeta assets.
        :param dinamico: Define si el objeto es dinámico (True) o estático (False).
        """
        self.x, self.y = x, y
        self.vel_x = self.vel_y = 0
        self.direccion = 1
        self.ancho = ancho
        self.alto = alto
        self.hitbox = pygame.Rect(x + 17, y + 20, ancho - 4, alto)
        self.imagen = pygame.image.load(ruta_imagen)
        self.imagen = pygame.transform.scale(self.imagen, (ancho, alto))  # Ajustar tamaño de la imagen

    def dibujar(self, pantalla):
        """
        Dibuja el objeto en la pantalla y su hitbox para depuración.
        """
        pantalla.blit(self.imagen, (self.x, self.y))
        pygame.draw.rect(pantalla, (255, 0, 0), self.hitbox, 2)  # Dibuja el hitbox (opcional para depuración)

    def actualizar_posicion(self, x, y):
        """
        Actualiza la posición del objeto y su hitbox.

        :param x: Nueva posición X.
        :param y: Nueva posición Y.
        """
        self.x = x
        self.y = y
        self.hitbox.topleft = (self.x, self.y)  # Actualizar la hitbox con la nueva posición

    def dibujar_con_desplazamiento(self, pantalla, desplazamiento_x, desplazamiento_y):
        """
        Dibuja el objeto en la pantalla ajustado por un desplazamiento.

        :param pantalla: Superficie de pygame donde se dibuja el objeto.
        :param desplazamiento_x: Desplazamiento en el eje X.
        :param desplazamiento_y: Desplazamiento en el eje Y.
        """
        pantalla.blit(self.imagen, (desplazamiento_x, desplazamiento_y))
        # pygame.draw.rect(pantalla, (255, 0, 0), self.hitbox.move(desplazamiento_x - self.x, desplazamiento_y - self.y), 2)  # Opcional para depuración

#yo creo que esta bien no se me ocurre algo que sea bien general que pueda agregarse aca
