import engine
import pygame
import math
import time
from player import Player

def main():
    pygame.init()
    pygame.display.set_caption("3d engine")
    width = engine.width
    height = engine.height
    fps = 60
    window = pygame.display.set_mode((width, height))
    # Player
    PLAYER_VELOCITY = 10
    player = Player(window, PLAYER_VELOCITY)
    player_x = 150
    player_y = -200
    player_z = 150
    player_a = 0    # Horizontal angle4
    player_l = 180    # Vertical angle
    sensitivity = 160 / fps
    player_forward_speed = 128 / fps
    def cameraMovement():
        # Camera movement
        dx = 0
        dy = player_forward_speed
        dz = 0
        player_a = 0
        player_l = 180

        return dx, dy, dz, player_a, player_l

    running = True
    while running:
        start_frametime = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        buttons = pygame.key.get_pressed()
        if buttons[pygame.K_LEFT]:
            player.orientation = -1
            player.x -= player.velocity
        elif buttons[pygame.K_RIGHT]:
            player.orientation = 1
            player.x += player.velocity
        else:
            player.orientation = 0
        dx, dy, dz, player_a, player_l = cameraMovement()
        player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz
        window.fill((0, 0, 0))

        framebuffer = engine.draw3D(player_x, player_y, player_z, player_a, player_l)
        pygame.surfarray.blit_array(window, framebuffer)
        player.update()

        pygame.display.flip()

        time_passed = time.time() - start_frametime
        pygame.time.delay(int(1000 / fps - time_passed))
if __name__ == "__main__":
    main()