__author__ = 'erC'

import unittest
from background_generator import Star, Background


class TestStar(unittest.TestCase):

    def setUp(self):
        self.star = Star()
        self.initial_star = Star(100)

    def test_star(self):
        self.assertGreater(self.star.rect.center[0], 0)
        self.assertEqual(self.star.rect.center[1], 0)
        self.assertEqual(self.initial_star.rect.center[1], 100)


class TestBackground(unittest.TestCase):

    def setUp(self):
        self.background = Background()

    def test_initialization(self):
        self.assertEqual(self.background.image.get_height(), 600)
        self.assertEqual(self.background.image.get_width(), 800)
        self.assertGreater(len(self.background.stars), 10)

    def test_udpate_method(self):
        stars = [star for star in self.background.stars]
        origin = stars[0].rect.center[1]
        self.background.update()
        self.assertNotEqual(stars[0].rect.center[1], origin)
        self.assertIn(stars[0], self.background.stars)
        stars[0].rect.center = [100, 2000]
        self.background.update()
        self.assertNotIn(stars[0], self.background.stars)
