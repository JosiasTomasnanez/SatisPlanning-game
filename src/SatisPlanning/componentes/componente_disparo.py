import pygame
from .utilidades import obtener_posicion_mouse
from .componente import Componente

class ComponenteDisparo(Componente):
    def __init__(self, personaje):
        """
        Inicializa el componente de disparo.

        :param personaje: Referencia al personaje que utiliza este componente.
        """
        super().__init__(personaje)

    def disparar(self, mundo):
        """
        Dispara un proyectil hacia la posición del ratón.

        :param mundo: Referencia al mundo para agregar el proyectil.
        """
        posicion_mouse = obtener_posicion_mouse()
        posicion_inicial = (self.personaje.x, self.personaje.y)

        # Crear un proyectil y agregarlo al mundo
        proyectil = Proyectil(posicion_inicial, posicion_mouse)
        mundo.agregar_objeto(proyectil)
        
    def actualizar(self, *args, **kwargs):
        """
            Método requerido por la clase abstracta Componente.
        """
        pass
        
        #esto es un ejemplo mapeo de mause
