"""
Classes and objects exported:
1. Background: Class that generates and updates the parallax starfield.
"""

import random
from variables import *

star_spawn_rate = [0, 0, 0, 0, 0, 0, 1]
star_speeds = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3]


class Star(pygame.sprite.Sprite):
    """
    Simple pygame.Sprite class that generates single pixel stars

    Instances of this class are used by the Background class as individual stars. The stars are
    randomly given a vertical speed in pixels/frame. Star uses the rect.center attribute to track
    its location. As such, all star speeds must be integer values.
    """

    def __init__(self, y_pos=None):
        """
        :param y_pos: This should only be passed in on initial starfield population. It sets the
        vertical value of where the star will be draw initially. All new stars after startup should
        spawn at the top pixel.
        """
        super().__init__()
        self.image = pygame.Surface([1, 1])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        if not y_pos:
            self.rect.center = (random.randint(0, size[0] - 1), 0)
        else:
            self.rect.center = (random.randint(0, size[0] - 1), y_pos)
        self.y_speed = random.choice(star_speeds)


class Background(object):
    """
    Class for creating and displaying a parallax starfield

    This class spawns instances of the Star class to populate a blank background with single pixel stars
    moving at various rates for a parallax effect. Each new frame of the game shifts the stars down and
    there is a 1/7 chance that a new star will spawn. That rate is applied to all vertical pixels on
    initialization to populate the background at the same density and distribution as when the game
    is running.

    Methods defined:
    """

    def __init__(self):
        """
        Set the surface image at the size of the screen and run the populate method
        """
        self.image = pygame.Surface((size[0], size[1]))
        self.image.fill(BLACK)
        self.stars = pygame.sprite.Group()
        self.populate()

    def spawn_star(self, y_pos=None):
        """Create a new star and add it to the stars sprite group"""
        new_star = Star(y_pos)
        self.stars.add(new_star)

    def populate(self):
        """
        Fill the new, blank screen with a uniform distribution of stars.

        This method, meant to be called only once, iterates through the vertical screen pixels,
        spawning a star 1/7th of the time. The y-value of that pixel is then passed to Star for placement.
        """
        for pixel in range(size[1]):
            if random.choice(star_spawn_rate):
                self.spawn_star(pixel)

    def update(self):
        """
        Choose if a star will spawn and kill any stars that fall off the screen. Draw all stars.

        This is called on each frame of the game loop to see if a new star will spawn. It is also
        responsible for moving the stars at their given speeds across the screen.
        """
        will_spawn = random.choice(star_spawn_rate)

        if will_spawn:
            self.spawn_star()

        for star in self.stars:
            star.rect.center = (star.rect.center[0], (star.rect.center[1] + star.y_speed))
            # Kill the stars that fall off the bottom of the screen
            if star.rect.center[1] > size[1]:
                star.kill()
        self.stars.draw(screen)
