import engine
import pygame
import math
import time

def main():
    pygame.init()
    pygame.display.set_caption("3d engine")
    width = engine.width
    height = engine.height
    fps = 60
    window = pygame.display.set_mode((width, height))
    # Player
    player_x = 150
    player_y = 0
    player_z = 200
    player_a = 0    # Horizontal angle4
    player_l = 180    # Vertical angle
    sensitivity = 30 / fps
    player_forward_speed = 1284 / fps
    def cameraMovement(player_a, player_l):
        # Camera movement
        dx = 0
        dy = player_forward_speed
        dz = 0
        # Camera
        # Horizontal angle
        if buttons[pygame.K_LEFT]:
            player_a -= sensitivity
            if player_a < 0:
                player_a = player_a + 360
        if buttons[pygame.K_RIGHT]:
            player_a += sensitivity
            if player_a > 360:
                player_a = player_a - 360
        # Look angle
        if buttons[pygame.K_DOWN]:
            player_l -= sensitivity
        if buttons[pygame.K_UP]:
            player_l += sensitivity

        return dx, dy, dz, player_a, player_l

    def playerMovement(player_a, player_l):
        dx = 0
        dy = 0
        dz = 0
        # Movement
        # X
        if buttons[pygame.K_w]:
            dx = dx + 10 * math.sin(math.radians(player_a))
            dy = dy + 10 * math.cos(math.radians(player_a))
        if buttons[pygame.K_s]:
            dx = dx + 10 * -math.sin(math.radians(player_a))
            dy = dy + 10 * -math.cos(math.radians(player_a))
        # Y
        if buttons[pygame.K_d]:
            dx = dx + 10 * math.cos(math.radians(player_a))
            dy = dy + 10 * -math.sin(math.radians(player_a))
        if buttons[pygame.K_a]:
            dx = dx + 10 * -math.cos(math.radians(player_a))
            dy = dy + 10 * math.sin(math.radians(player_a))
        # Z
        if buttons[pygame.K_SPACE]:
            dz = dz + -10
        if buttons[pygame.K_LSHIFT]:
            dz = dz + 10

        # Camera
        # Horizontal angle
        if buttons[pygame.K_LEFT]:
            player_a -= 3
            if player_a < 0:
                player_a = player_a + 360
        if buttons[pygame.K_RIGHT]:
            player_a += 3
            if player_a > 360:
                player_a = player_a - 360
        # Look angle
        if buttons[pygame.K_DOWN]:
            player_l -= 3
        if buttons[pygame.K_UP]:
            player_l += 3

        return player_a, player_l

    running = True
    while running:
        start_frametime = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        buttons = pygame.key.get_pressed()

        # player_a, player_l = playerMovement(player_a, player_l)
        dx, dy, dz, player_a, player_l = cameraMovement(player_a, player_l)
        
        player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz

        window.fill((0, 0, 0))
        framebuffer = engine.draw3D(player_x, player_y, player_z, player_a, player_l)
        engine
        pygame.surfarray.blit_array(window, framebuffer)
    
        pygame.display.flip()

        time_passed = time.time() - start_frametime
        pygame.time.delay(int(1000 / fps - time_passed))
if __name__ == "__main__":
    main()