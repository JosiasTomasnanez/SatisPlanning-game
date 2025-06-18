import unittest
from unittest.mock import MagicMock
from SatisPlanning.entidades.Zombie_enemy import Zombie

class TestZombie(unittest.TestCase):
    def setUp(self):
        self.zombie = Zombie(10, 20, 40, 40, distancia_persecucion=100)

    def test_init(self):
        self.assertEqual(self.zombie.x, 10)
        self.assertEqual(self.zombie.y, 20)
        self.assertEqual(self.zombie.ancho, 40)
        self.assertEqual(self.zombie.alto, 40)
        self.assertTrue(hasattr(self.zombie, "movimiento_aleatorio"))
        self.assertTrue(hasattr(self.zombie, "movimiento_persecucion"))
        self.assertEqual(self.zombie.vida, 100)
        self.assertTrue(self.zombie.es_enemigo)

    def test_recibir_danio(self):
        self.zombie.recibir_danio(30)
        self.assertEqual(self.zombie.vida, 70)
        self.zombie.recibir_danio(100)
        self.assertEqual(self.zombie.vida, 0)

    def test_set_comportamiento_movimiento(self):
        mock_strategy = MagicMock()
        self.zombie.set_comportamiento_movimiento(mock_strategy)
        self.assertEqual(self.zombie.comportamiento_movimiento, mock_strategy)

    def test_set_mundo(self):
        mock_mundo = MagicMock()
        self.zombie.set_mundo(mock_mundo)
        self.assertEqual(self.zombie.mundo, mock_mundo)
        self.assertEqual(self.zombie.componente_mover.mundo, mock_mundo)

if __name__ == '__main__':
    unittest.main()
