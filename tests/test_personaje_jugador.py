import unittest
from unittest.mock import MagicMock, patch
from SatisPlanning.entidades.personaje_jugador import PersonajeJugador

class TestPersonajeJugador(unittest.TestCase):
    @patch('SatisPlanning.entidades.objeto.pygame.image.load', return_value=MagicMock())
    @patch('SatisPlanning.entidades.objeto.pygame.transform.scale', return_value=MagicMock())
    @patch('SatisPlanning.entidades.personaje_jugador.pygame')
    @patch('SatisPlanning.entidades.personaje_jugador.obtener_ruta_asset', return_value='fake_path')
    @patch('SatisPlanning.entidades.personaje_jugador.ComponenteInventario')
    @patch('SatisPlanning.entidades.personaje_jugador.ComponenteAnimacion')
    @patch('SatisPlanning.entidades.personaje_jugador.ComponenteMover')
    def test_init(self, mock_mover, mock_anim, mock_inv, mock_ruta, mock_pygame, mock_scale, mock_load):
        mock_pygame.image.load.return_value = MagicMock()
        mock_pygame.transform.scale.return_value = MagicMock()
        jugador = PersonajeJugador(1, 2, 3, 4)
        self.assertEqual(jugador.x, 1)
        self.assertEqual(jugador.y, 2)
        self.assertEqual(jugador.ancho, 3)
        self.assertEqual(jugador.alto, 4)
        self.assertTrue(hasattr(jugador, 'componente_inventario'))

    def test_obtener_inventario(self):
        jugador = MagicMock(spec=PersonajeJugador)
        jugador.componente_inventario = MagicMock()
        inventario = MagicMock()
        jugador.componente_inventario.inventario = inventario
        self.assertEqual(PersonajeJugador.obtener_inventario(jugador), inventario)

    def test_set_mundo(self):
        jugador = MagicMock(spec=PersonajeJugador)
        jugador.componente_inventario = MagicMock()
        jugador.componente_mover = MagicMock()
        mundo = MagicMock()
        PersonajeJugador.set_mundo(jugador, mundo)
        jugador.componente_inventario.set_mundo.assert_called_once_with(mundo)
        jugador.componente_mover.set_mundo.assert_called_once_with(mundo)  # Se debe llamar

    def test_actualizar(self):
        jugador = MagicMock(spec=PersonajeJugador)
        jugador.componente_mover = MagicMock()
        jugador.componente_animacion = MagicMock()
        jugador.atacando = False  # Añadido para evitar AttributeError
        PersonajeJugador.actualizar(jugador, 'teclas')
        jugador.componente_mover.actualizar.assert_called_once_with('teclas')
        jugador.componente_animacion.actualizar.assert_called_once()

    def test_manejar_evento(self):
        jugador = MagicMock(spec=PersonajeJugador)
        jugador.componente_inventario = MagicMock()
        evento = MagicMock()
        PersonajeJugador.manejar_evento(jugador, evento)
        jugador.componente_inventario.actualizar.assert_called_once_with(evento)

if __name__ == '__main__':
    unittest.main()
