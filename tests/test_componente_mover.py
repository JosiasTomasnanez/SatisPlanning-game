import unittest
from unittest.mock import MagicMock
import pygame
from SatisPlanning.componentes.componente_mover import ComponenteMover

class TestComponenteMover(unittest.TestCase):
    def setUp(self):
        self.personaje = MagicMock()
        self.personaje.velocidad = 5
        self.personaje.fuerza_salto = 10
        self.personaje.vel_x = 0
        self.personaje.vel_y = 0
        self.personaje.en_el_suelo = True
        self.personaje.hitbox = pygame.Rect(0, 0, 40, 40)
        self.personaje.x = 0
        self.personaje.y = 0
        self.personaje.direccion = 1

        self.componente_animacion = MagicMock()
        self.mover = ComponenteMover(self.personaje, self.componente_animacion)
        self.mundo = MagicMock()
        self.mundo.colisiona.return_value = False
        self.mover.set_mundo(self.mundo)

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

    def test_mover_horizontal(self):
        teclas = {pygame.K_d: True, pygame.K_a: False, pygame.K_w: False, pygame.K_SPACE: False}
        self.mover.mover(teclas)
        self.assertEqual(self.personaje.vel_x, 5)
        self.assertEqual(self.personaje.direccion, 1)

    def test_mover_izquierda(self):
        teclas = {pygame.K_d: False, pygame.K_a: True, pygame.K_w: False, pygame.K_SPACE: False}
        self.mover.mover(teclas)
        self.assertEqual(self.personaje.vel_x, -5)
        self.assertEqual(self.personaje.direccion, -1)

    def test_salto(self):
        self.personaje.en_el_suelo = True
        teclas = {pygame.K_d: False, pygame.K_a: False, pygame.K_w: True, pygame.K_SPACE: False}
        self.mover.mover(teclas)
        self.assertEqual(self.personaje.vel_y, -10)
        self.assertFalse(self.personaje.en_el_suelo)

    def test_gravedad(self):
        self.personaje.en_el_suelo = False
        self.personaje.vel_y = 0
        teclas = {pygame.K_d: False, pygame.K_a: False, pygame.K_w: False, pygame.K_SPACE: False}
        self.mover.mover(teclas)
        self.assertGreater(self.personaje.vel_y, 0)

    def test_colision_vertical(self):
        self.mundo.colisiona.side_effect = [False, True]
        self.personaje.vel_y = 5
        self.personaje.en_el_suelo = False
        teclas = {pygame.K_d: False, pygame.K_a: False, pygame.K_w: False, pygame.K_SPACE: False}
        self.mover.mover(teclas)
        self.assertEqual(self.personaje.vel_y, 0)
        self.assertTrue(self.personaje.en_el_suelo)

if __name__ == '__main__':
    unittest.main()
