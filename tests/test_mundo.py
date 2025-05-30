import unittest
from unittest.mock import MagicMock, patch
from SatisPlanning.mundo import Mundo

class TestMundo(unittest.TestCase):
    @patch('SatisPlanning.mundo.Mapa')
    @patch('SatisPlanning.mundo.PersonajeJugador')
    @patch('SatisPlanning.mundo.ManjeadorChunks')
    def test_init(self, mock_chunks, mock_personaje, mock_mapa):
        mundo = Mundo()
        mock_mapa.assert_called_once()
        mock_personaje.assert_called_once()
        mock_chunks.assert_called_once()

    def test_obtener_personaje(self):
        mundo = MagicMock(spec=Mundo)
        personaje = MagicMock()
        mundo.personaje = personaje
        self.assertEqual(Mundo.obtener_personaje(mundo), personaje)

    def test_agregar_objeto(self):
        mundo = MagicMock(spec=Mundo)
        mundo.manejador_chunks = MagicMock()
        objeto = MagicMock()
        Mundo.agregar_objeto(mundo, objeto, True)
        objeto.tangible = True
        mundo.manejador_chunks.agregar_objeto.assert_called_once_with(objeto)

if __name__ == '__main__':
    unittest.main()
