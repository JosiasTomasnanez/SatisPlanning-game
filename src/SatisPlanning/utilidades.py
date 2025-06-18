# src/SatisPlanning/utils.py
import os
import pygame

def obtener_ruta_asset(ruta_relativa: str) -> str:
    """
    Devuelve la ruta absoluta del asset desde el archivo actual.

    :param ruta_relativa: Ruta relativa del asset dentro de la carpeta assets.
    :return: Ruta absoluta del asset.
    """
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "assets", ruta_relativa)

def obtener_posicion_mouse():
    """
    Devuelve la posición actual del ratón en la pantalla.

    :return: Una tupla (x, y) con la posición del ratón.
    """
    return pygame.mouse.get_pos()
#esta clase funciona bien y nos puede servir para muchas cosas que exedan las responsabilidades del juego, por ejemplo aca podemos tener la funcion para cargar  y leer el archivo json de guardado de progreso de nuestro juego, o por otra parte podemos tener archivos txt de dialogos de personajes y que sean leidos por metodos de esta clase y puestos en string para enviarlos a otras clases que nesesiten ciertos dialogos de algun archivo

