"""
Classes and objects exported:
Hitbox: Class used for collision detection on enemy attacks and ships.
enemies: Sprite group containing the images and hitboxes of enemies.
attacks: Sprite group that includes only the drawn images of enemy attacks.
shots: Sprite group that holds hitboxes for various attacks.
Note: attacks and shots are maintained as separate groups to allow for hitbox calibration during testing. Attacks are drawn on screen, shots should not be.
"""

import random
import math
from variables import *


class Hitbox(pygame.sprite.Sprite):
    """
    Hitbox sprite class using pygame.rect attributes for use in collision testing

    This class is meant to be used by the player Ship class, enemy attacks, and most enemy classes for
    fast and sufficiently accurate collision detection. A hitbox defined here is a rectangular sprite
    that must be added to the enemies or shots sprite groups for collision detection to occur.
    A separate hitbox is necessary when a ship's image contains even small amounts of blank space at the edges
    of the rectangle defining the image of the ship. Some large ships, or ships of a complex shape, may
    require multiple hitboxes.
    """

    def __init__(self, width, height, x_pos, y_pos, damage):
        """
        Instantiate a Hitbox object. Must be added to a sprite group to function.

        :param width: Horizontal boundary of collision detection
        :param height: Vertical boundary of collision detection
        :param x_pos: Horizontal offset on the ship or attack image surface
        :param y_pos: Vertical offset
        :param damage: Integer value of damage done to player ship when collisions occur
        """
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)  # To allow for tracking during collision testing
        self.rect = self.image.get_rect()
        self.position = [x_pos, y_pos]
        self.rect.center = self.position[:]
        self.damage = damage


class BasicAttack(pygame.sprite.Sprite):
    """
    Super class for all straight line attacks.

    This class defines a standard, non-accelerating, single-image attack. It contains all methods
    required to produce a functional attack, calibrated to the BasicEnemy class. It is meant to be
    subclassed by specific types of attacks that require different parameters.
    Methods defined:
    """

    def __init__(self, source, offset, angle, velocity, damage, line_length, line_width, color=RED):
        """
        Create an attack object.

        The default values for this attack object are calibrated to the BasicEnemy class. The surfaces,
        lines, and hitbox offsets are aligned to that class. As detailed in the player's Ship class,
        integer rounding in pygame.rect necessitates a separate floating point attribute (position) to
        accurately update the object's position on the screen.

        :param source: Enemy surface image where the attack originates
        :param offset: Pixel offset that defines the origin of the attack line to be drawn
        :param angle: Angle in radians for the attack. 0 is defined as straight down
        :param velocity: Speed in pixels/frame that the attack will move on update
        :param damage: Integer value of damage done. Passed to the Hitbox instance created
        :param line_length: Length in pixels of the attack line
        :param line_width: Width of attack line
        :param color: Keyword arg defaulting to RED (from variables module). RGB values as tuples should be passed. Eg RED = (255, 0, 0)
        """
        super().__init__()
        self.image = pygame.Surface((30, 60))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = [source[0] - 15, source[1] - 7]
        self.position = self.rect.center[:]  # use separate position attribute to avoid rect.center int rounding
        self.angle = angle
        self.velocity = [0, velocity]
        self.color = color
        self.line_length = line_length
        self.line_width = line_width
        self.line_origin = offset
        self.line_terminus = self.line_origin[:]
        self.calc_and_draw()
        self.damage = damage
        #  Standard hitbox offset is for BasicEnemy class. Overwrite this for other classes of enemies
        self.hitbox = Hitbox(2, 8, self.rect.center[0] + 15, self.rect.center[1] + 30, self.damage)
        attacks.add(self)
        shots.add(self.hitbox)

    def calc_and_draw(self):
        """
        Adjust velocity based on angle of firing. Calculate line terminus from line origin, angle, and length.

        This method uses simple trig calculations to change the velocity (while keeping magnitude) of an attack.
        Those calculations are also used to determine where the endpoint of an attack line should be drawn. Finally,
        it draws the calculated line on the attack surface.
        """
        x_factor = math.sin(self.angle)
        y_factor = math.cos(self.angle)
        self.velocity[0] = self.velocity[1] * x_factor * 1.1
        self.velocity[1] *= y_factor * 1.1
        self.line_terminus[0] += (x_factor * self.line_length)
        self.line_terminus[1] += (y_factor * self.line_length)

        pygame.draw.line(self.image, self.color, self.line_origin, self.line_terminus, self.line_width)

    def update(self):
        """
        Update the position of the sprite, then draw it on screen. Determine if attack has run off the screen.

        Again, position is used here to avoid integer rounding. Hitboxes are updated at the same time to
        avoid disconnects between the hitbox and the image of the sprite on screen. The sprite is killed
        (removed from all sprite groups, thus garbage collected) if it runs far enough off screen. It is
        also killed if its corresponding hitbox is not in the shots sprite group due to a collision with
        the player ship.
        """
        self.position = [self.position[0] + self.velocity[0],
                         self.position[1] + self.velocity[1]]
        self.rect.center = self.position[:]
        self.hitbox.position = [self.hitbox.position[0] + self.velocity[0],
                                self.hitbox.position[1] + self.velocity[1]]
        self.hitbox.rect.center = self.hitbox.position[:]
        screen.blit(self.image, self.rect.center)

        if self.rect.center[1] > 1000 or self.hitbox not in shots:
            self.kill()  # removes attack from all sprite groups (inherited from superclass)


class AngledAttack(BasicAttack):
    """Simple subclass of BasicAttack. Hitboxes were recalibrated to line up with attack image."""

    def __init__(self, *args):
        super().__init__(*args)
        self.hitbox.kill()  # Hitbox was added to shots group at init, must kill to avoid errors
        if self.angle > 0:
            self.hitbox = Hitbox(3, 6, self.rect.center[0] + 19, self.rect.center[1] + 22, self.damage)
        else:
            self.hitbox = Hitbox(3, 6, self.rect.center[0] + 10, self.rect.center[1] + 22, self.damage)
        shots.add(self.hitbox)


class PowerLaser(BasicAttack):
    """Subclass of BasicAttack. Only hitbox calibration changed."""

    def __init__(self, *args):
        super().__init__(*args)
        self.hitbox.kill()
        self.hitbox = Hitbox(2, 17, self.rect.center[0] + 16, self.rect.center[1] + 28, self.damage)
        shots.add(self.hitbox)


class BasicEnemy(pygame.sprite.Sprite):
    """
    Super class defining a functioning enemy.

    This class contains everything necessary to instantiate a standard enemy on the game screen. It
    is meant to be subclassed by overwritting the image, mass, cooldowns, lifetimes, and explosion_offset
    attributes, as well as the attack method.
    Behaviorally, instances of this class spawn just above the screen at a random horizontal location,
    slowly moving down until they are two image-widths on screen. They then slow down and attack at
    random intervals until their lifetime (in frames drawn) expires, at which point they accelerate and
    move off the bottom of the screen. Subclasses of enemies with specific movements should overwrite
    the intro and outro methods as well.

    Methods defined:
    """

    def __init__(self):
        """
        Instantiate a basic enemy using the first_enemy image

        See instantiation of the Ship class for explanations of many of these attributes. Others include:
        position: a random choice horizontally, and above the screen a number of pixels equal to the images height.
        mass: the damage this ship will do if it collides with the player's ship.
        introduction: Bool to determine if the intro method will be run.
        attack_cooldown: minimum number of frames that must pass between attacks.
        current_cooldown: counter that tracks frames since last attack.
        lifetime: number of frames the enemy advances and attacks as normal.
        explosion_offset: value to be passed to DrawExplosion instances to calibrate placement
            of explosion animation.

        Note: This class does NOT use separate hitbox instances. By default, the entire enemy image is
        used for collision detection. You must either redefine the image's rect attribute (for simple cases)
        or define a series of hitbox instances if the entire image is unsuitable for collisions.
        """
        super().__init__()
        self.image = pygame.image.load('images\\first_enemy.png').convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.position = (random.randint(10, 790), -(self.image.get_height()))
        self.rect.center = self.position[:]
        self.velocity = [0, .5]
        self.mass = 1
        self.introduction = True
        self.current_cooldown = 1000
        self.attack_cooldown = 50
        self.lifetime = 310
        self.explosion_offset = [15, 12]
        enemies.add(self)

    def intro(self):
        """
        Move the enemy forward until it is just inside the screen. Allow attacks when introduction is over.
        """
        self.update_position((0, 1))
        if self.rect.center[1] > (self.image.get_height() * 1.8):
            self.introduction = False
            self.current_cooldown = 0

    def outro(self):
        """
        Accelerate the ship every 5 frames until about 5 pixels/frame. Disallow further attacks.
        """
        if not self.lifetime % 5 and self.velocity[1] < 5:
            self.velocity[1] += .35
            self.current_cooldown = 1000

    def update(self):
        """
        Countdown the lifetime of the enemy, update its position, and make attacks.

        This method counts down the main lifetime of an enemy ship and updates its position. If the
        ship is still in its introduction sequence, most of the method is skipped. In main phase, the
        ship calls attack every frame and has its position updated via the update_position method.
        If the ship moves off the bottom of the screen, it is deleted.

        :return: None if the ship is still in its introduction
        """
        self.lifetime -= 1
        if self.introduction:
            self.intro()
            return None
        if self.lifetime < 0:
            self.outro()
        self.update_position(self.velocity)
        if self.rect.center[1] > size[1] + (self.image.get_height() * 2):
            self.kill()  # Kill the enemy sprite if it runs off the bottom of the screen
        self.attack()

    def update_position(self, velocity):
        """
        Update the position of the image and copy that float to the image's rect attribute.
        :param list velocity: Integer or float that defines movement in pixels/frame
        """
        self.position = [(self.position[0] + velocity[0]), (self.position[1] + velocity[1])]
        self.rect.center = self.position[:]

    def attack(self):
        """
        Reduce the attack cooldown and try to fire a shot. If fired, restart the cooldown.
        """
        self.current_cooldown -= 1
        if random.randint(0, 100) > 99 and self.current_cooldown < 0:
            BasicAttack(self.rect.center, [15, 14], 0, 7, damage=1, line_length=15, line_width=1)
            self.current_cooldown = self.attack_cooldown


class Fighter(BasicEnemy):
    """
    Subclass of BasicEnemy with altered attacks and a custom hitbox.

    This class alters the hitboxes and attacks of the BasicEnemy class. Number of attacks increased from
    one to three, with both angled and straight attacks. The hitbox size was reduced from the full image
    size due to large unfilled areas on the source image.

    Methods overwritten:
        1. attack
    """

    def __init__(self):
        """
        Rect attribute redefined as smaller than image. Mass increased to do more collision damage.
        """
        super().__init__()
        self.image = pygame.image.load('images\\second_enemy.png').convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = pygame.Rect(2, 0, 27, 31)  # smaller rectangle to avoid excessive black-space 'collisions'
        self.mass = 2

    def attack(self):
        """
        Similar to attack method of super class. Fires either two angled shots on regular cooldown or one powerful
        shot on shorter cooldown.
        """
        self.current_cooldown -= 1
        attack_select = random.randint(1, 1000)
        if 965 <= attack_select <= 985 and self.current_cooldown < 0:
            AngledAttack((self.rect.center[0] + 9, self.rect.center[1] - 4), [15, 14], math.radians(30), 6, 1, 15, 1)
            AngledAttack((self.rect.center[0] - 3, self.rect.center[1] - 4), [15, 14], -math.radians(30), 6, 1, 15, 1)
            self.current_cooldown = self.attack_cooldown

        if 986 <= attack_select <= 1000 and self.current_cooldown < 0:
            PowerLaser((self.rect.center[0] + 3, self.rect.center[1] - 8), [15, 14], 0, 5, 2, 23, 3, BLUE)
            self.current_cooldown = self.attack_cooldown - 20


class DrawExplosions(object):
    """
    Animation class for small-scale explosion instances drawn directly on screen.

    This class uses a sliding 'window' frame over a larger image to simulate an explosion centered on an
    enemy that has just collided with the player's ship. On instantiation, the entire explosion image array
    is loaded. A small frame surface is defined and centered over the first explosion image. The 'window' frame
    is then moved across the array every in-game loop frame, resulting in a 20-frame explosion animation.

    Methods defined:
    """

    def __init__(self, position):
        """
        Attributes defined here:
        explosion_array: 300x320 image of 20 segments of an explosion
        destruction timer: Counter that determines when a vertical frame shift needs to occur
        frame_offset: Calibration to get the first frame over the initial explosion image
        :param list position: Position on screen where the explosion is to be placed
        """
        super().__init__()
        self.position = position
        self.explosion_array = pygame.image.load('images\\enemy_explosion.png').convert()
        self.explosion_array.set_colorkey(BLACK)
        self.frame = pygame.Surface((40, 40))
        self.frame.set_colorkey(BLACK)
        self.destruction_timer = 20
        self.frame_offset = [-20, -10]  # sets the viewing frame over the first explosion in the array
        self.draw()

    def draw(self):
        """
        Draw the explosion image to the window frame, then draw the window to the main screen. Advance the frame.
        """
        self.destruction_timer -= 1
        self.frame.blit(self.explosion_array, self.frame_offset)
        screen.blit(self.frame, self.position)
        self.calculate_frame_offset()

    def calculate_frame_offset(self):
        """
        Translate the window frame 80 pixels until frame 4, then reset to the left and move the frame down 1 row.
        """
        self.frame_offset[0] -= 80
        if self.frame_offset[0] < -320:
            self.frame_offset[0] = -20
        if not self.destruction_timer % 4:
            self.frame_offset[1] -= 60


# sprite group creation for collisions and updating in main loop
enemies = pygame.sprite.Group()
shots = pygame.sprite.Group()
attacks = pygame.sprite.Group()
