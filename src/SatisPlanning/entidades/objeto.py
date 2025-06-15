import pygame

class Objeto:
    def __init__(self, x, y, ancho, alto, ruta_imagen, dinamico, tangible=True):
        """
        Inicializa un objeto con posición, hitbox, una imagen y un cuerpo físico en el mundo.

        :param x: Posición X del objeto.
        :param y: Posición Y del objeto.
        :param ancho: Ancho del hitbox.
        :param alto: Altura del hitbox.
        :param ruta_imagen: Ruta de la imagen en la carpeta assets.
        :param dinamico: Define si el objeto es dinámico (True) o estático (False).
        :param tangible: Define si el objeto es tangible (True) o no (False).
        """
        self.x, self.y = x, y
        self.vel_x = self.vel_y = 0
        self.direccion = 1
        self.ancho = ancho
        self.alto = alto
        # La hitbox se ajusta con un desplazamiento respecto a la posición del objeto
        self.hitbox = pygame.Rect(x + 17, y + 20, ancho - 4, alto)
        self.imagen = pygame.image.load(ruta_imagen)
        self.imagen = pygame.transform.scale(self.imagen, (ancho, alto))  # Ajustar tamaño de la imagen
        self.dinamico = dinamico
        self.tangible = tangible  # Indica si el objeto es tangible
        self.componentes = []  # Lista de componentes asociadas al objeto

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


