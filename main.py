def main():
    """
    Primary gameplay function. Initializes the pygame package and runs the main game loop.

    This function sets the variables for the main loop, gets the user keyboard inputs, and calls the
    functions and methods required to progress the game. The function iterates through the imported sprite
    groups to update each sprite across the screen. It tests collisions between the player ship hitboxes
    and enemy attacks/ships. Finally, it draws the background, sprites, enemies, and player ship to the
    screen.

    :var clock: a pygame class instance used to set the maximum framerate of the game.
    :var font: the system font used when rendering HUD information.
    :var bool done: responsible for ending the game. Game terminates on True
    :var bool starting: must be True before enemies are spawned.
    :var float x_speed: the horizontal movement speed of the ship.
    :var float y_speed: vertical movement speed of the player ship.
    :var int distance_traveled: number of frames elapsed in the game. Tempo variable for game progress.
    :var list deaths: list of sprites 'killed' in collisions with player ship, deleted after their explosion animation.
    """
    import variables
    from background_generator import Background
    from ship import ship, ship_hitbox
    from enemies import attacks, enemies, shots, DrawExplosions
    from stages import game_manager

    variables.pygame.init()
    clock = variables.pygame.time.Clock()
    background = Background()
    font = variables.pygame.font.SysFont('Calibri', 18, True, False)
    done = False
    starting = False
    x_speed, y_speed = 0, 0
    distance_traveled = 1
    deaths = []

    def render_hud(energy, shield, boost):
        """
        Render the font variables for all HUD information and blit them to the screen.

        :arg energy: integer from ship.energy. Changed to 'MAX' if at or above 100
        :arg shield: integer from ship.shield_level. Changed to 'MAX' if at or above 5
        :arg boost: integer from ship.boost. A value of 1 means no boost, any other value
            is assumed to be a boost multiplier. This must be changed if future enemy attacks
            have the possibility of slowing the player's ship.
        """
        if shield >= 5:
            shield = 'MAX'
        if energy >= 100:
            energy = 'MAX'
        if boost == 1:
            boost = 'Disabled'
        else:
            boost = 'Enabled'
        shield_level_text = font.render('Shield Level: {0}'.format(shield), True, variables.WHITE)
        energy_level_text = font.render('Energy: {0}'.format(energy), True, variables.WHITE)
        overdrive_text = font.render('Overdrive:  {0}'.format(boost), True, variables.WHITE)
        variables.screen.blit(energy_level_text, [18, 570])
        variables.screen.blit(shield_level_text, [130, 570])
        variables.screen.blit(overdrive_text, [315, 570])

    while not done:  # main program loop

        for event in variables.pygame.event.get():
            if event.type == variables.pygame.QUIT:
                done = True

            elif event.type == variables.pygame.KEYDOWN:
                if event.key == variables.pygame.K_LEFT:
                    x_speed = -4
                elif event.key == variables.pygame.K_RIGHT:
                    x_speed = 4
                elif event.key == variables.pygame.K_UP:
                    y_speed = -4
                elif event.key == variables.pygame.K_DOWN:
                    y_speed = 4
                elif event.key == variables.pygame.K_d:
                    ship.increase_shields()
                elif event.key == variables.pygame.K_a:
                    ship.decrease_shields()
                elif event.key == variables.pygame.K_w:
                    ship.overdrive()

            elif event.type == variables.pygame.KEYUP:
                if event.key == variables.pygame.K_LEFT:
                    x_speed = 0
                elif event.key == variables.pygame.K_RIGHT:
                    x_speed = 0
                elif event.key == variables.pygame.K_UP:
                    y_speed = 0
                elif event.key == variables.pygame.K_DOWN:
                    y_speed = 0

        variables.screen.fill(variables.BLACK)
        background.update()
        ship.update(x_speed, y_speed, distance_traveled)

        if starting:
            game_manager(distance_traveled, ship.rect.center)

        for enemy in enemies:
            enemy.update()

        for attack in attacks:
            attack.update()

        for hitbox in ship_hitbox:
            # spritecollide returns a list of all sprites in a group that overlap the tested sprite (here, hitbox)
            # must iterate through the lists in case more than 1 hit occurred in the last frame
            collisions = variables.pygame.sprite.spritecollide(hitbox, enemies, True)
            hits = variables.pygame.sprite.spritecollide(hitbox, shots, True)
            if hits:
                for i in hits:
                    print('Hit, damage is', i.damage)
                    done = ship.take_damage(i.damage)
            if collisions:
                for enemy in collisions:
                    print('Collision, damage is', enemy.mass)
                    temp_death = DrawExplosions((enemy.position[0] - enemy.explosion_offset[0],
                                                enemy.position[1] - enemy.explosion_offset[1]))
                    deaths.append(temp_death)
                    done = ship.take_damage(enemy.mass)

        for dying in deaths:
            dying.draw()

        deaths = [dying for dying in deaths if dying.destruction_timer > 0]  # discards finished animations
        # ship_hitbox.draw(variables.screen)
        # shots.draw(variables.screen)
        enemies.draw(variables.screen)
        render_hud(ship.energy, ship.shield_level, ship.boost)
        variables.pygame.display.update()
        clock.tick(60)  # cap the framerate at 60
        distance_traveled += 1
        if distance_traveled > 25:
            starting = True

    variables.pygame.quit()

if __name__ == '__main__':
    main()
