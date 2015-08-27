"""
Classes and objects defined:
1. Ship: Class representing the player's ship.
2. ship_hitbox: Sprite group for player ship used in collision detection.
"""

from variables import *
from enemies import Hitbox


class Ship(pygame.sprite.Sprite):
    """
    Player-controlled Ship class

    This class creates and controls the player ship that is always visible on the game screen.
    Most behavior is determined by attributes defined in the __init__ method, with the exception
    of x and y speeds, which are determined by keypresses in the 'main' module.

    Methods defined:
    """

    def __init__(self):
        """
        Static init for creation of the player ship.

        Arguments:
            position: Initial position on main screen, in pixels
            rect.center: Copy of position, this is the value used by pygame to draw the center
                of the ship image. The position argument can be manipulated as a floating point number to avoid
                the integer rounding that occurs for rect x and y positions.
            vertical/horizontal_hitbox: Instances of the Hitbox class (defined in the enemies module)
                that define the borders of interaction for collision detection.
            energy: Player energy level. 100 is maximum
            shield: Attribute that will hold a pygame.Surface instance for display of the player's shield
            boost: Multiplier used by the update function to modulate ship velocity
            boost_timer: Integer variable that defines the number of frames overdrive is active for
        """
        super().__init__()
        self.surface = pygame.image.load('images\\ship1.png').convert()
        self.surface.set_colorkey((0, 0, 0))
        self.rect = self.surface.get_rect()
        self.position = [345, 400]
        self.rect.center = self.position[:]
        self.vertical_hitbox = Hitbox(18, 67, 407, 452, 0)
        self.horizontal_hitbox = Hitbox(50, 11, 407, 474, 0)
        self.energy = 100
        self.shield = None
        self.shield_level = 0
        self.boost = 1
        self.boost_timer = 0
        self.draw_shield()

    def update(self, x_speed, y_speed, distance_traveled):
        """
        Calculate ship velocity, draw it on screen, and update various timers.

        This method calculates ship velocity based on input x and y speeds, as well as active overdrives.
        As only 8 directions of movement are possible, a simple calculation is performed to make diagonal
        movement close in magnitude to cardinal movement.
        Active overdrives are counted down by 1 per frame.
        If the player has less than 100 (maximum) energy, energy levels are increased every 65 frames traveled.

        :param x_speed: input from main module, positive if right arrow was pressed, negative for left arrow
        :param y_speed: same as x_speed, positive for down arrow, negative for up arrow
        :param distance_traveled: input from main, an integer count of elapsed frames in the game loop
        """
        x_speed *= self.boost
        y_speed *= self.boost

        if x_speed and y_speed:  # This keeps diagonal movement from being much faster than cardinal movement
            x_speed = round((x_speed / 1.414) * 1.1, 3)
            y_speed = round((y_speed / 1.414) * 1.1, 3)

        self.update_position(x_speed, y_speed)
        screen.blit(self.surface, self.rect.center)

        if self.boost_timer > 0:
            self.boost_timer -= 1
            self.overdrive()

        if not distance_traveled % 65 and self.energy < 100:
            self.energy += 1

    def update_position(self, x_speed, y_speed):
        """
        Update the position of the ship's image and associated hitboxes

        As mentioned in init documentation, pygame.rect values are rounded (down) to integer values
        at assignment. This results in irregular movement when floating point velocities are employed.
        Thus, the position attribute is used to store the true position of the ship's image. This
        attribute is then copied to give a pixel-approximation of the position. The same logic applies
        for hitbox movements.
        Positions are not updated if the check_boundary method fails.

        :param x_speed: a floating point number calculated in the update method for horizontal movement
        :param y_speed: same as x_speed, but for vertical movement.
        """
        if self.check_boundary(x_speed, y_speed):
            self.position = [(self.rect.center[0] + x_speed), (self.rect.center[1] + y_speed)]
            self.rect.center = self.position[:]
            self.horizontal_hitbox.position = ((self.horizontal_hitbox.rect.center[0] + x_speed),
                                               (self.horizontal_hitbox.rect.center[1] + y_speed))
            self.horizontal_hitbox.rect.center = self.horizontal_hitbox.position[:]
            self.vertical_hitbox.position = ((self.vertical_hitbox.rect.center[0] + x_speed),
                                             (self.vertical_hitbox.rect.center[1] + y_speed))
            self.vertical_hitbox.rect.center = self.vertical_hitbox.position[:]

    def check_boundary(self, x_speed, y_speed):
        """
        Stop the player ship if it will run off the screen

        This method uses the main screen Surface instance and the ship's current velocity to determine
        if the ship's image is within a certain pixel range of the screen boundary.

        :param x_speed: floating point horizontal movement speed calculated in the update method
        :param y_speed: same as x_speed, for vertical movement.
        :return: False if within a given pixel range of a boundary and moving towards that boundary
            True if not near the boundary, or if on the boundary but not moving toward the boundary
        """
        if self.position[0] < 5 and x_speed < 0:
            return False
        if self.position[0] > (screen.get_width() - 120) and x_speed > 0:
            return False
        if self.position[1] < 15 and y_speed < 0:
            return False
        if self.position[1] > (screen.get_height() - 140) and y_speed > 0:
            return False
        return True

    def overdrive(self):
        """
        Set the ship's boost at +50% if energy is sufficient. Set the boost countdown timer.
        """
        if self.energy >= 25 and self.boost_timer == 0:
            self.boost = 1.5
            self.boost_timer = 400
            self.energy -= 25
        if self.boost_timer == 0:
            self.boost = 1

    def increase_shields(self):
        """
        Reduce energy levels to raise shield level by 1. Call the draw_shield method to update the screen.
        """
        if self.energy >= 20 and self.shield_level < 5:
            self.shield_level += 1
            self.energy -= 20
            self.draw_shield()

    def decrease_shields(self):
        """
        Convert shield level to energy. Energy is capped at 100, and shield level at 0.
        """
        if self.shield_level > 0:
            self.shield_level -= 1
            self.energy += 20
            if self.energy > 100:
                self.energy = 100
            self.draw_shield()

    def draw_shield(self):
        """
        Get current shield level and draw the appropriate level over the ship image.

        This gives the player a visual representation of shield presence and shield level. Shield level
        is modulated by the alpha and width parameters. Width represents the thickness of the oval to be
        drawn, while alpha is an integer from 0-255 representing the opacity of a pygame surface. The shield
        surface opacity increases with shield level to give a more vibrant effect. At maximum levels, the
        method draws a second oval in white as an extra indicator that sheilds are full.
        The pygame.draw.arc function is used to draw the shield. THe position variable describes the
        x and y offsets needed to center the oval around the ship, as well as the horizontal and vertical
        sizes of the oval.
        """
        if self.shield_level < 0:
            self.shield_level = 0
        position = (27, 10, 70, 86)
        alpha = 0
        width = 0
        white_width = 0

        if self.shield_level == 1:
            width = 1
            alpha = 65
        elif self.shield_level == 2:
            width = 1
            alpha = 120
        elif self.shield_level == 3:
            width = 2
            alpha = 150
        elif self.shield_level == 4:
            width = 2
            alpha = 210
        elif self.shield_level == 5:
            width = 3
            alpha = 210
            white_width = 1

        self.shield = pygame.Surface((134, 100))  # same size as ship rectangle
        self.shield.set_colorkey(BLACK)
        self.shield.set_alpha(alpha)
        self.shield.fill(BLACK)
        pygame.draw.arc(self.shield, (51, 92, 214), position, 0, 360, width)
        pygame.draw.arc(self.shield, WHITE, position, 0, 360, white_width)
        self.surface = pygame.image.load('images\\ship1.png').convert() # must redraw ship to erase old shield levels
        self.surface.set_colorkey(BLACK)
        self.surface.blit(self.shield, (0, 0))

    def take_damage(self, damage):
        """
        Adjust the shield level in response to damage. Quit the game if ship damage is taken.

        This method is currently the only way to end the game. Damage that reduces the shields below
        zero will return true to the main module, ending the game loop.

        :param damage: Integer value from the main module. This is either attack damage or collision damage
        :return: False if there was enough shield to absorb the damage
            True if damage taken was more than shield level.
        """
        self.shield_level -= damage
        if self.shield_level < 0:
            return True
        self.draw_shield()
        return False


ship = Ship()
ship_hitbox = pygame.sprite.Group()
ship_hitbox.add(ship.vertical_hitbox)
ship_hitbox.add(ship.horizontal_hitbox)
