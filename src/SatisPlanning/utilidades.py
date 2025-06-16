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

def es_click_mouse(evento):
    """
    Devuelve True si el evento es un clic izquierdo del mouse.
    """
    return getattr(evento, "type", None) == pygame.MOUSEBUTTONDOWN and getattr(evento, "button", None) == 1
def scale_keep_aspect(image, target_size):
        original_width, original_height = image.get_size()
        target_width, target_height = target_size

        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        scaled = pygame.transform.smoothscale(image, (new_width, new_height))

        # Crear superficie final centrada
        final_image = pygame.Surface(target_size, pygame.SRCALPHA)
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        final_image.blit(scaled, (x, y))
        
        return pygame.transform.flip(final_image, True, False)

def scale_keep_aspect(image, target_size, invertir):
        original_width, original_height = image.get_size()
        target_width, target_height = target_size

        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        scaled = pygame.transform.smoothscale(image, (new_width, new_height))

        # Crear superficie final centrada
        final_image = pygame.Surface(target_size, pygame.SRCALPHA)
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        final_image.blit(scaled, (x, y))

        if invertir:
            return pygame.transform.flip(final_image, True, False)
        return final_image