import unittest
from unittest.mock import MagicMock
from SatisPlanning.componentes.componente_mover import ComponenteMover

class TestComponenteMover(unittest.TestCase):
    def test_init(self):
        personaje = MagicMock()
        anim = MagicMock()
        mover = ComponenteMover(personaje, anim)
        self.assertEqual(mover.propietario, personaje)
        self.assertEqual(mover.componente_animacion, anim)
        self.assertIsNone(mover.mundo)

    def test_set_mundo(self):
        mover = ComponenteMover(MagicMock(), MagicMock())
        mundo = MagicMock()
        mover.set_mundo(mundo)
        self.assertEqual(mover.mundo, mundo)

if __name__ == '__main__':
    unittest.main()
