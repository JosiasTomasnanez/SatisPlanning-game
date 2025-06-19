import unittest
from unittest.mock import MagicMock
from SatisPlanning.generador_monstruos import GeneradorMonstruos
from SatisPlanning.manejador_niveles import ManejadorNiveles

class TestManejadorGenerador(unittest.TestCase):
    def setUp(self):
        # Mock personaje y mundo
        self.personaje = MagicMock()
        self.personaje.x = 100
        self.personaje.y = 100

        self.mundo = MagicMock()
        self.mundo.colisiona.return_value = False

        # Generador y manejador con parámetros simples
        self.generador = GeneradorMonstruos(distancia_persecucion=200)
        self.manejador = ManejadorNiveles(
            self.generador,
            spawn_frame_interval=1,
            max_enemigos=2,
            spawn_dist_min=10,
            spawn_dist_max=20,
            despawn_dist=1000
        )
        self.manejador.set_mundo(self.mundo)

    def test_spawn_enemigos(self):
        # Debe agregar enemigos hasta el máximo permitido
        self.manejador.spawn_enemigos(self.personaje)
        self.assertEqual(len(self.manejador.enemigos), 1)
        self.manejador.spawn_enemigos(self.personaje)
        self.assertEqual(len(self.manejador.enemigos), 2)
        # No debe agregar más allá del máximo
        self.manejador.spawn_enemigos(self.personaje)
        self.assertEqual(len(self.manejador.enemigos), 2)

    def test_spawn_boss(self):
        # Debe agregar un boss
        self.manejador.spawn_boss(self.personaje)
        bosses = [e for e in self.manejador.enemigos if getattr(e, "es_boss", False)]
        self.assertEqual(len(bosses), 1)

    def test_actualizar_enemigos(self):
        # Agrega un enemigo y simula que está lejos para ser eliminado
        self.manejador.spawn_enemigos(self.personaje)
        enemigo = self.manejador.enemigos[0]
        enemigo.x = 9999  # Muy lejos
        enemigo.y = 9999
        self.manejador._actualizar_enemigos(self.personaje)
        self.assertEqual(len(self.manejador.enemigos), 0)

if __name__ == '__main__':
    unittest.main()
