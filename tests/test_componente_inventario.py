import unittest
from unittest.mock import MagicMock
from SatisPlanning.componentes.componente_inventario import ComponenteInventario

class TestComponenteInventario(unittest.TestCase):
    def test_init(self):
        propietario = MagicMock()
        inventario = MagicMock()
        comp = ComponenteInventario(propietario, inventario)
        self.assertEqual(comp.propietario, propietario)
        self.assertEqual(comp.inventario, inventario)
        self.assertFalse(comp.inventario.visible)

    def test_set_mundo(self):
        comp = ComponenteInventario(MagicMock(), MagicMock())
        mundo = MagicMock()
        comp.set_mundo(mundo)
        self.assertEqual(comp.mundo, mundo)

if __name__ == '__main__':
    unittest.main()
