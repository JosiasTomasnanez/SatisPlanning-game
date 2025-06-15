import unittest
from unittest.mock import MagicMock, patch
from SatisPlanning.presentador_juego import PresentadorJuego

class TestPresentadorJuego(unittest.TestCase):
    @patch('SatisPlanning.presentador_juego.pygame')
    def test_manejar_eventos_quit(self, mock_pygame):
        # Simula un evento QUIT
        mock_event = MagicMock()
        mock_event.type = 999  # Valor arbitrario para QUIT
        eventos = [mock_event]
        mock_vista = MagicMock()
        mock_vista.QUIT = 999  # Debe coincidir con mock_event.type
        presentador = PresentadorJuego(mundo=MagicMock(), vista_juego=mock_vista)
        resultado = presentador.manejar_eventos(eventos)
        self.assertEqual(resultado, "salir")  # Antes: self.assertIsNone(resultado)

    @patch('SatisPlanning.presentador_juego.pygame')
    def test_manejar_eventos_no_quit(self, mock_pygame):
        # Simula un evento que no es QUIT
        mock_event = MagicMock()
        mock_event.type = 123  # cualquier valor que no sea QUIT
        eventos = [mock_event]
        mock_vista = MagicMock()
        mock_vista.QUIT = 999  # Valor diferente a mock_event.type
        presentador = PresentadorJuego(mundo=MagicMock(), vista_juego=mock_vista)
        resultado = presentador.manejar_eventos(eventos)
        self.assertEqual(resultado, [mock_event])

    def test_actualizar_llama_metodos(self):
        mock_mundo = MagicMock()
        mock_vista = MagicMock()
        mock_mundo.obtener_objetos_a_dibujar.return_value = (['obj1'], 'personaje')
        # Simula un evento válido con .type y .key
        mock_event = MagicMock()
        mock_event.type = 0
        mock_event.key = 0
        presentador = PresentadorJuego(mundo=mock_mundo, vista_juego=mock_vista)
        presentador.actualizar(0.1, [mock_event])
        mock_mundo.actualizar.assert_called_once()
        mock_mundo.obtener_objetos_a_dibujar.assert_called_once()
        mock_vista.dibujar.assert_called_once()

if __name__ == '__main__':
    unittest.main()
