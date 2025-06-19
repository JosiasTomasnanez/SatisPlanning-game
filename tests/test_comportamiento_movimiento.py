import unittest
from unittest.mock import MagicMock
from SatisPlanning.componentes.comportamiento_movimiento import (
    EstrategiaMovimientoAleatorio,
    EstrategiaMovimientoPersecucion
)

class TestEstrategiaMovimientoAleatorio(unittest.TestCase):
    def setUp(self):
        self.estrategia = EstrategiaMovimientoAleatorio()
        self.enemigo = MagicMock()
        self.enemigo.velocidad = 3
        self.enemigo.hitbox.move.return_value = MagicMock()
        self.enemigo.mundo.colisiona.return_value = False
        self.enemigo.componente_mover = MagicMock()

    def test_mover_llama_actualizar(self):
        # Debe llamar a componente_mover.actualizar con un diccionario de teclas
        self.estrategia.mover(self.enemigo)
        self.enemigo.componente_mover.actualizar.assert_called_once()
        teclas = self.enemigo.componente_mover.actualizar.call_args[0][0]
        self.assertIn(100, teclas)
        self.assertIn(97, teclas)
        self.assertIn(119, teclas)
        self.assertIn(32, teclas)

class TestEstrategiaMovimientoPersecucion(unittest.TestCase):
    def setUp(self):
        self.estrategia = EstrategiaMovimientoPersecucion(distancia_activacion=100)
        self.enemigo = MagicMock()
        self.enemigo.velocidad = 3
        self.enemigo.hitbox.move.return_value = MagicMock()
        self.enemigo.mundo.colisiona.return_value = False
        self.enemigo.componente_mover = MagicMock()
        self.enemigo.mundo.personaje = MagicMock()
        self.enemigo.x = 0

    def test_mover_persecucion_derecha(self):
        self.enemigo.mundo.personaje.x = 50
        self.estrategia.mover(self.enemigo)
        self.enemigo.componente_mover.actualizar.assert_called_once()
        teclas = self.enemigo.componente_mover.actualizar.call_args[0][0]
        self.assertTrue(teclas[100])  # d
        self.assertFalse(teclas[97])  # a

    def test_mover_persecucion_izquierda(self):
        self.enemigo.mundo.personaje.x = -50
        self.estrategia.mover(self.enemigo)
        teclas = self.enemigo.componente_mover.actualizar.call_args[0][0]
        self.assertTrue(teclas[97])  # a
        self.assertFalse(teclas[100])  # d

    def test_mover_fuera_de_rango(self):
        self.enemigo.mundo.personaje.x = 200
        self.estrategia.mover(self.enemigo)
        teclas = self.enemigo.componente_mover.actualizar.call_args[0][0]
        self.assertFalse(teclas[100])
        self.assertFalse(teclas[97])

if __name__ == '__main__':
    unittest.main()
