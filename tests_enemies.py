__author__ = 'erC'

import unittest
from enemies import *

class TestHitbox(unittest.TestCase):
    def setUp(self):
        self.hitbox = Hitbox(20, 20, 100, 100, 4)

    def test_addition(self):
        self.assertEqual(15, 3 + 12)

    def test_strings(self):
        self.assertNotEqual('Hello', 'Hello...')

    def test_hitbox(self):
        self.assertEqual(self.hitbox.rect.center, (100, 100))
        self.assertEqual(self.hitbox.damage, 4)
        self.assertEqual(self.hitbox.position, [100, 100])


class TestBasicAttack(unittest.TestCase):
    """Tests for the basic laser attack class and its methods"""
    def setUp(self):
        self.attack = BasicAttack([10, 10], [2, 2], 0, 1, 1, 5, 1)
        #  Parameters are source, offset, angle, velocity, damage, line length, line width

    def test_calc_and_draw_method(self):
        self.assertEqual(self.attack.velocity[0], 0)
        self.assertEqual(self.attack.velocity[1], 1.1)  # Method was already run in init, test if it changed velocity
        self.assertAlmostEqual(self.attack.line_terminus, [2, 7], places=1)

    def test_update_method(self):
        old_position = self.attack.position[:]
        self.attack.update()  # method returns nothing, but changes object attributes
        self.assertNotEqual(old_position, self.attack.position)
        self.assertEqual(self.attack.position, [-5, 4.1])
        self.assertNotEqual(self.attack.position, self.attack.rect.center)  # should be different due to int rounding
        self.assertIn(self.attack.hitbox, shots)
        self.assertIn(self.attack, attacks)
        self.attack.position = [2000, 2000]
        self.attack.update()  # shove the sprite way off screen, make sure the kill method runs
        self.assertNotIn(self.attack, attacks)


class TestAngledAttack(unittest.TestCase):
    """Testing for the simple subclass AngledAttack"""
    def setUp(self):
        self.angled = AngledAttack([10, 10], [2, 2], math.radians(30), 1, 1, 5, 1, BLUE)
        self.neg = AngledAttack([10, 10], [2, 2], -math.radians(30), 1, 1, 5, 1, BLUE)

    def test_angled(self):
        self.assertIn(self.angled.hitbox, shots)
        self.assertIn(self.angled, attacks)
        self.assertAlmostEqual(self.angled.velocity[0], 0.55, places=2)
        self.assertAlmostEqual(self.angled.velocity[1], 0.95, places=2)
        self.assertEqual(self.angled.hitbox.rect.center, (14, 25))
        self.assertEqual(self.neg.hitbox.rect.center, (5, 25))  # make sure hitboxes are adjusted on left-side shots


class TestPowerLaser(unittest.TestCase):

    def setUp(self):
        self.power = PowerLaser([10, 10], [2, 2], 0, 1, 1, 5, 1, BLUE)

    def test_power(self):
        self.assertIn(self.power.hitbox, shots)
        self.assertIn(self.power, attacks)
        self.assertEqual(self.power.hitbox.image.get_height(), 17)
        self.assertEqual(self.power.hitbox.image.get_width(), 2)


class TestBasicEnemy(unittest.TestCase):

    def setUp(self):
        self.enemy = BasicEnemy()

    def test_initialization(self):
        self.assertEqual(self.enemy.image.get_height(), 22)
        self.assertEqual(self.enemy.image.get_width(), 21)
        self.assertLess(self.enemy.position[1], 0)
        self.assertGreater(self.enemy.velocity[1], 0)
        self.assertEqual(self.enemy.velocity[0], 0)
        self.assertIn(self.enemy, enemies)
        self.assertIsInstance(self.enemy.current_cooldown, int)
        self.assertIsInstance(self.enemy.lifetime, int)

    def test_intro_method(self):
        first_position = self.enemy.position
        self.enemy.intro()
        self.assertNotEqual(self.enemy.position, first_position)
        self.assertTrue(self.enemy.introduction)
        self.enemy.position = [50, 300]  # skip to a position past the introduction point and run into again
        self.enemy.intro()
        self.assertFalse(self.enemy.introduction)

    def test_outro_method(self):
        self.assertEqual(self.enemy.velocity[1], .5)
        self.assertGreater(self.enemy.lifetime, 0)
        self.enemy.lifetime = 0
        self.enemy.outro()
        self.assertNotEqual(self.enemy.velocity[1], .5)
        self.enemy.velocity = [0, 10]
        self.enemy.outro()  # velocity set too high, should not be altered in outro()
        self.assertEqual(self.enemy.velocity[1], 10)

    def test_update_method(self):
        self.assertTrue(self.enemy.introduction)
        self.assertIn(self.enemy, enemies)
        self.assertEqual(self.enemy.position[1], -22)  # must use y-coord, as x is random
        self.enemy.update()
        self.assertEqual(self.enemy.position[1], -21)  # if introduction, position should not be changed by 1
        self.enemy.introduction = False
        self.enemy.update()
        self.assertEqual(self.enemy.position[1], -20.5)
        self.enemy.position = [50, 10000]  # push it far off screen, update should now kill the sprite
        self.enemy.update()
        self.assertNotIn(self.enemy, enemies)


class TestFighter(unittest.TestCase):

    def setUp(self):
        self.fighter = Fighter()

    def test_initialization(self):
        self.assertEqual(self.fighter.image.get_height(), 36)
        self.assertEqual(self.fighter.image.get_width(), 31)  # make sure proper image is loading
        self.assertIsInstance(self.fighter.rect, pygame.Rect)
        self.assertGreater(self.fighter.mass, 0)

    def test_attack(self):  # not sure how to test when there are small random chances of things happening
        pass


class TestDrawExplosions(unittest.TestCase):

    def setUp(self):
        self.boom = DrawExplosions([100, 100])

    def test_initialization(self):
        self.assertEqual(self.boom.explosion_array.get_height(), 300)
        self.assertEqual(self.boom.explosion_array.get_width(), 320)  # Make sure the correct size image is loaded
        self.assertLess(self.boom.frame_offset[0], 0)
        self.assertLess(self.boom.frame_offset[1], 0)
        self.assertGreater(self.boom.destruction_timer, 0)

    def test_draw_method(self):
        self.assertEqual(self.boom.frame_offset, [-100, -10])
        self.boom.draw()
        self.assertEqual(self.boom.frame_offset, [-180, -10])

    def test_calculate_offset(self):
        self.assertEqual(self.boom.frame_offset, [-100, -10])
        self.boom.frame_offset = [-400, -70]
        self.boom.draw()
        self.assertEqual(self.boom.frame_offset, [-20, -70])

if __name__ == '__main__':
    unittest.main()


""" Testing:
1. Unittesting - small units of code. Each test should be independent.
2. Automatable!!
3. Integrated w/ development process
4. Use assertAlmostEqual for floating point tests
5. Focus on the interactions of class functions, as well as IF statements when writing tests
6. Use Nose for more automated testing, as well as coverage reports (DONT FORGET THE BRANCHES)
7. unittest.main() will discover any tests in a module
8. Greg looks for 'for loops', 'if statements' and 'try, except' statements
9. NOSE!!!
"""