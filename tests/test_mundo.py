import unittest
from unittest.mock import MagicMock, patch
from SatisPlanning.mundo import Mundo

class TestMundo(unittest.TestCase):
    @patch('SatisPlanning.mundo.Mapa')
    @patch('SatisPlanning.mundo.PersonajeJugador')
    @patch('SatisPlanning.mundo.ManjeadorChunks')
    def test_init(self, mock_chunks, mock_personaje, mock_mapa):
        generador_monstruos = MagicMock()
        mundo = Mundo(mock_personaje, mock_mapa, mock_chunks, generador_monstruos)
        # Verifica que se llamó a set_mundo en el personaje
        mock_personaje.set_mundo.assert_called_once_with(mundo)
        # Verifica que se llamó a cargar_chunks_iniciales en el manejador de chunks
        mock_chunks.cargar_chunks_iniciales.assert_called_once_with(mock_personaje)

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
