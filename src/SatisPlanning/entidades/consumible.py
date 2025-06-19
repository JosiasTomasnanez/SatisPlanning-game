import SatisPlanning.constantes as ct
from SatisPlanning.entidades.objeto import Objeto
import pygame

class PocionCura(Objeto):
    def __init__(self, x=0, y=0, ancho=30, alto=30, ruta_imagen=ct.ITEM_POCIONES[0]):
        super().__init__(x, y, ancho, alto, ruta_imagen, dinamico=False, tangible=True)
        self.es_consumible = True

    def consumir(self, personaje=None):
        """
        Cura 20 de vida al personaje si se pasa como argumento.
        """
        if personaje and hasattr(personaje, "curar"):
            personaje.curar(20)
