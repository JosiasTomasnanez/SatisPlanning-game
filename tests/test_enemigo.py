import unittest
from unittest.mock import MagicMock
from SatisPlanning.entidades.enemigo import Enemigo

class TestEnemigo(unittest.TestCase):
    def setUp(self):
        self.enemigo = Enemigo(10, 20, 40, 40, distancia_persecucion=100)

    def test_init(self):
        self.assertEqual(self.enemigo.x, 10)
        self.assertEqual(self.enemigo.y, 20)
        self.assertEqual(self.enemigo.ancho, 40)
        self.assertEqual(self.enemigo.alto, 40)
        self.assertTrue(hasattr(self.enemigo, "movimiento_aleatorio"))
        self.assertTrue(hasattr(self.enemigo, "movimiento_persecucion"))
        self.assertEqual(self.enemigo.vida, 100)
        self.assertTrue(self.enemigo.es_enemigo)

    def test_recibir_danio(self):
        self.enemigo.recibir_danio(30)
        self.assertEqual(self.enemigo.vida, 70)
        self.enemigo.recibir_danio(100)
        self.assertEqual(self.enemigo.vida, 0)

    def test_set_comportamiento_movimiento(self):
        mock_strategy = MagicMock()
        self.enemigo.set_comportamiento_movimiento(mock_strategy)
        self.assertEqual(self.enemigo.comportamiento_movimiento, mock_strategy)

    def test_set_mundo(self):
        mock_mundo = MagicMock()
        self.enemigo.set_mundo(mock_mundo)
        self.assertEqual(self.enemigo.mundo, mock_mundo)
        self.assertEqual(self.enemigo.componente_mover.mundo, mock_mundo)

if __name__ == '__main__':
    unittest.main()
