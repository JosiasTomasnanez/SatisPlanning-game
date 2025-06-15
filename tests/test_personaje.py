import unittest
from unittest.mock import MagicMock, patch
from SatisPlanning.entidades.personaje import Personaje

class TestPersonaje(unittest.TestCase):
    @patch('SatisPlanning.entidades.objeto.pygame.image.load', return_value=MagicMock())
    @patch('SatisPlanning.entidades.objeto.pygame.transform.scale', return_value=MagicMock())
    @patch('SatisPlanning.entidades.personaje.pygame')
    @patch('SatisPlanning.utilidades.obtener_ruta_asset')
    def test_init(self, mock_obtener_ruta_asset, mock_pygame, mock_scale, mock_load):
        mock_pygame.image.load.return_value = MagicMock()
        mock_pygame.transform.scale.return_value = MagicMock()
        # Pasa una lista de mocks como sprites
        personaje = Personaje(10, 20, 30, 40, 'fake_path', sprites=[MagicMock(), MagicMock()])
        self.assertEqual(personaje.x, 10)
        self.assertEqual(personaje.y, 20)
        self.assertEqual(personaje.ancho, 30)
        self.assertEqual(personaje.alto, 40)
        self.assertTrue(hasattr(personaje, 'componente_animacion'))
        self.assertTrue(hasattr(personaje, 'componente_mover'))

    def test_set_mundo(self):
        personaje = MagicMock(spec=Personaje)
        personaje.componente_mover = MagicMock()
        mundo = MagicMock()
        # Llama al método real
        Personaje.set_mundo(personaje, mundo)
        personaje.componente_mover.set_mundo.assert_called_once_with(mundo)

    def test_actualizar(self):
        personaje = MagicMock(spec=Personaje)
        personaje.componente_mover = MagicMock()
        personaje.componente_animacion = MagicMock()
        Personaje.actualizar(personaje, 'teclas')
        personaje.componente_mover.actualizar.assert_called_once_with('teclas')
        personaje.componente_animacion.actualizar.assert_called_once()

if __name__ == '__main__':
    unittest.main()
