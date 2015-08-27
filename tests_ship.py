__author__ = 'erC'

import unittest
from ship import Ship
from enemies import Hitbox


class TestShip(unittest.TestCase):

    def setUp(self):
        self.ship = Ship()

    def test_initialization(self):
        self.assertEqual(self.ship.surface.get_height(), 100)
        self.assertEqual(self.ship.surface.get_width(), 134)  # Make sure proper image is loaded
        self.assertIsInstance(self.ship.vertical_hitbox, Hitbox)
        self.assertIsInstance(self.ship.horizontal_hitbox, Hitbox)

    def test_update_method(self):
        self.assertEqual(self.ship.position, [345, 400])
        self.ship.energy = 50
        self.ship.update(5, 0, 65)
        self.assertEqual(self.ship.position, [350, 400])
        self.assertEqual(self.ship.energy, 51)
        self.ship.boost_timer = 1
        self.ship.update(3, 3, 10)
        self.assertEqual(self.ship.energy, 26)
        self.assertAlmostEqual(self.ship.position[0], 352.3, places=1)

    def test_check_boundary_method(self):
        self.ship.position = [-5, 100]
        result = self.ship.check_boundary(-5, 0)
        self.assertFalse(result)
        self.ship.position = [1000, 100]
        result = self.ship.check_boundary(5, 0)
        self.assertFalse(result)
        self.ship.position = [100, 100]
        result = self.ship.check_boundary(3, 3)
        self.assertTrue(result)
        self.ship.position = [100, -5]
        result = self.ship.check_boundary(0, -5)
        self.assertFalse(result)
        self.ship.position = [100, 1000]
        result = self.ship.check_boundary(0, 5)
        self.assertFalse(result)

    def test_overdrive_method(self):
        self.assertEqual(self.ship.boost, 1)
        self.ship.overdrive()
        self.assertEqual(self.ship.boost, 1.5)
        self.assertEqual(self.ship.boost_timer, 400)
        self.ship.energy = 0
        self.ship.boost_timer = 0
        self.ship.overdrive()
        self.assertEqual(self.ship.boost, 1)

    def test_increase_shields_method(self):
        self.assertEqual(self.ship.shield_level, 0)
        self.ship.increase_shields()
        self.assertEqual(self.ship.shield_level, 1)
        self.assertEqual(self.ship.energy, 80)

    def test_decrease_shields_method(self):
        self.ship.decrease_shields()
        self.assertEqual(self.ship.shield_level, 0)
        self.ship.shield_level = 2
        self.ship.energy = 50
        self.ship.decrease_shields()
        self.assertEqual(self.ship.energy, 70)
        self.ship.energy = 100
        self.ship.decrease_shields()
        self.assertEqual(self.ship.energy, 100)

    def test_draw_shield_method(self):
        self.ship.draw_shield()
        self.assertEqual(self.ship.shield.get_alpha(), 0)
        self.ship.shield_level = 1
        self.ship.draw_shield()
        self.assertEqual(self.ship.shield.get_alpha(), 65)
        self.ship.shield_level = 2
        self.ship.draw_shield()
        self.assertEqual(self.ship.shield.get_alpha(), 120)
        self.ship.shield_level = 3
        self.ship.draw_shield()
        self.assertEqual(self.ship.shield.get_alpha(), 150)
        self.ship.shield_level = 4
        self.ship.draw_shield()
        self.assertEqual(self.ship.shield.get_alpha(), 210)
        self.ship.shield_level = 5
        self.ship.draw_shield()

    def test_take_damage_method(self):
        self.ship.shield_level = 5
        result = self.ship.take_damage(2)
        self.assertEqual(self.ship.shield_level, 3)
        self.assertFalse(result)
        self.ship.shield_level = 0
        result = self.ship.take_damage(1)
        self.assertTrue(result)

