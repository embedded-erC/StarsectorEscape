

import random
from enemies import BasicEnemy, Fighter


def game_manager(distance, player_position):
    if random.randint(0, 1000) > 990:
        spawn = BasicEnemy()

    if random.randint(0, 1000) > 990:
        spawn = Fighter()