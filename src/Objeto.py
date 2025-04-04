import pygame
import constantes as ct
class Objeto:
    def __init__(self, x, y, width, height, image_path, dinamico):
        """
        Inicializa un objeto con posición, hitbox, una imagen y un cuerpo físico en el mundo.

        :param x: Posición X del objeto.
        :param y: Posición Y del objeto.
        :param width: Ancho del hitbox.
        :param height: Altura del hitbox.
        :param image_path: Ruta de la imagen en la carpeta assets.
        :param world: Instancia de Box2D.b2World para asociar el cuerpo físico.
        :param dinamico: Define si el objeto es dinámico (True) o estático (False).
        """
        self.x, self.y = x, y
        self.vel_x = self.vel_y = 0
        self.direccion = 1
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(x+17, y+20, width-4, height)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))  # Ajustar tamaño de la imagen
        

    def draw(self, screen):
        """
        Dibuja el objeto en la pantalla y su hitbox para depuración.
        """
        screen.blit(self.image, (self.x, self.y))
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)  # Dibuja el hitbox (opcional para depuración)


    def update_position(self, x, y):
        """
        Actualiza la posición del objeto y su hitbox.

        :param x: Nueva posición X.
        :param y: Nueva posición Y.
        """
        self.x = x
        self.y = y
        self.hitbox.topleft = (self.x, self.y)  # Actualizar la hitbox con la nueva posición

    def draw_with_offset(self, screen, offset_x, offset_y):
        """
        Dibuja el objeto en la pantalla ajustado por un desplazamiento.

        :param screen: Superficie de pygame donde se dibuja el objeto.
        :param offset_x: Desplazamiento en el eje X.
        :param offset_y: Desplazamiento en el eje Y.
        """
        screen.blit(self.image, (offset_x, offset_y))
        #pygame.draw.rect(screen, (255, 0, 0), self.hitbox.move(offset_x - self.x, offset_y - self.y), 2)  # Opcional para depuración

    def notificar_colision(self, objeto):
        """
        Método llamado cuando este objeto colisiona con otro.
        """
        pass  # Por defecto, no hace nada. Las subclases pueden sobrescribir este método.