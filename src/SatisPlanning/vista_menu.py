import pygame
import SatisPlanning.constantes as ct
from SatisPlanning.utilidades import obtener_ruta_asset

class VistaMenu:
    QUIT = pygame.QUIT

    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.opciones = ["Jugar", "Controles", "Créditos", "Salir"]
        self.opcion_seleccionada = 0
        self.fuente = pygame.font.SysFont("Arial", 40)
        self._rects_opciones = []
        # Cargar fondo del menú
        ruta_fondo = obtener_ruta_asset("fondo_menu.png")
        self.fondo = pygame.image.load(ruta_fondo).convert()

    def _blit_text_con_contorno(self, texto, fuente, color, x, y):
        # Renderiza el texto con un contorno negro
        base = fuente.render(texto, True, color)
        contorno = fuente.render(texto, True, (0, 0, 0))
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    self.pantalla.blit(contorno, (x + dx, y + dy))
        self.pantalla.blit(base, (x, y))

    def dibujar(self):
        # Dibuja el fondo
        self.pantalla.blit(pygame.transform.scale(self.fondo, self.pantalla.get_size()), (0, 0))
        self._rects_opciones = []
        # Ajusta el valor base de y para subir las letras (por ejemplo, 200 en vez de ct.ALTO // 2)
        base_y = 250
        for i, opcion in enumerate(self.opciones):
            color = (255, 255, 0) if i == self.opcion_seleccionada else (255, 255, 255)
            texto = self.fuente.render(opcion, True, color)
            x = (ct.ANCHO - texto.get_width()) // 2
            y = base_y + i * 60  # Antes: y = (ct.ALTO // 2) + i * 60
            rect = pygame.Rect(x, y, texto.get_width(), texto.get_height())
            self._rects_opciones.append(rect)
            self._blit_text_con_contorno(opcion, self.fuente, color, x, y)
        pygame.display.flip()

    def obtener_eventos(self):
        return pygame.event.get()

    def obtener_opcion_en_posicion(self, x, y):
        """
        Devuelve el índice de la opción sobre la que está la posición (x, y), o None si no está sobre ninguna.
        """
        for i, rect in enumerate(self._rects_opciones):
            if rect.collidepoint(x, y):
                return i
        return None

    def mostrar_creditos(self, texto_creditos):
        self.pantalla.blit(pygame.transform.scale(self.fondo, self.pantalla.get_size()), (0, 0))
        lineas = texto_creditos.split('\n')
        fuente_titulo = pygame.font.SysFont("Arial", 36)
        fuente = pygame.font.SysFont("Arial", 24)
        for i, linea in enumerate(lineas):
            if i == 0:
                fuente_actual = fuente_titulo
                color = (255, 255, 0)
            else:
                fuente_actual = fuente
                color = (255, 255, 255)
            texto = fuente_actual.render(linea, True, color)
            x = (self.pantalla.get_width() - texto.get_width()) // 2
            y = 120 + i * 50
            self._blit_text_con_contorno(linea, fuente_actual, color, x, y)
        texto_volver = fuente.render("Pulsa cualquier tecla o haz click para volver", True, (180, 180, 180))
        x = (self.pantalla.get_width() - texto_volver.get_width()) // 2
        y = 120 + len(lineas) * 50 + 30
        self._blit_text_con_contorno("Pulsa cualquier tecla o haz click para volver", fuente, (180, 180, 180), x, y)
        pygame.display.flip()
