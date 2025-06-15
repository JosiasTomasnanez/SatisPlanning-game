import unittest
from unittest.mock import MagicMock
from SatisPlanning.presentador_menu import PresentadorMenu
from SatisPlanning.menu import Menu

class TestMenu(unittest.TestCase):
    def setUp(self):
        self.menu = Menu(["Jugar", "Controles", "Créditos", "Salir"])

    def test_mover_arriba_abajo(self):
        self.menu.opcion_seleccionada = 0
        self.menu.mover_abajo()
        self.assertEqual(self.menu.opcion_seleccionada, 1)
        self.menu.mover_arriba()
        self.assertEqual(self.menu.opcion_seleccionada, 0)
        self.menu.mover_arriba()
        self.assertEqual(self.menu.opcion_seleccionada, 3)  # wrap around

    def test_seleccionar(self):
        self.menu.opcion_seleccionada = 2
        self.menu.seleccionar()
        self.assertTrue(self.menu.terminado)
        self.assertEqual(self.menu.seleccion, "creditos")

    def test_reiniciar(self):
        self.menu.terminado = True
        self.menu.seleccion = "salir"
        self.menu.opcion_seleccionada = 2
        self.menu.reiniciar()
        self.assertFalse(self.menu.terminado)
        self.assertIsNone(self.menu.seleccion)
        self.assertEqual(self.menu.opcion_seleccionada, 0)

class TestPresentadorMenu(unittest.TestCase):
    def setUp(self):
        self.vista_menu = MagicMock()
        self.vista_menu.opciones = ["Jugar", "Controles", "Créditos", "Salir"]
        self.presentador = PresentadorMenu(self.vista_menu)

    def test_manejar_eventos_quit(self):
        evento = MagicMock()
        evento.type = 999
        self.vista_menu.QUIT = 999
        self.presentador.manejar_eventos([evento])
        self.assertTrue(self.presentador.menu.terminado)
        self.assertEqual(self.presentador.menu.seleccion, "salir")

    def test_manejar_eventos_teclado(self):
        evento = MagicMock()
        evento.type = 768  # pygame.KEYDOWN
        evento.key = 13    # pygame.K_RETURN
        self.presentador.menu.opcion_seleccionada = 0
        self.presentador.manejar_eventos([evento])
        self.assertTrue(self.presentador.menu.terminado)
        self.assertEqual(self.presentador.menu.seleccion, "jugar")

    def test_reiniciar(self):
        self.presentador.menu.terminado = True
        self.presentador.menu.seleccion = "salir"
        self.presentador.reiniciar()
        self.assertFalse(self.presentador.menu.terminado)
        self.assertIsNone(self.presentador.menu.seleccion)

if __name__ == '__main__':
    unittest.main()
