import unittest
from unittest.mock import MagicMock, patch
from SatisPlanning.entidades.objeto import Objeto

class TestObjeto(unittest.TestCase):
    @patch('SatisPlanning.entidades.objeto.pygame')
    def test_init(self, mock_pygame):
        mock_pygame.image.load.return_value = MagicMock()
        mock_pygame.transform.scale.return_value = MagicMock()
        obj = Objeto(1, 2, 3, 4, 'fake_path', True, True)
        self.assertEqual(obj.x, 1)
        self.assertEqual(obj.y, 2)
        self.assertEqual(obj.ancho, 3)
        self.assertEqual(obj.alto, 4)
        self.assertTrue(obj.dinamico)
        self.assertTrue(obj.tangible)
        self.assertIsInstance(obj.componentes, list)

    def test_agregar_componente(self):
        obj = MagicMock(spec=Objeto)
        obj.componentes = []
        componente = MagicMock()
        Objeto.agregar_componente(obj, componente)
        self.assertIn(componente, obj.componentes)

    def test_actualizar_posicion(self):
        obj = MagicMock(spec=Objeto)
        obj.x = 0
        obj.y = 0
        obj.hitbox = MagicMock()
        Objeto.actualizar_posicion(obj, 10, 20)
        obj.hitbox.topleft = (10 + 17, 20 + 20)

if __name__ == '__main__':
    unittest.main()
