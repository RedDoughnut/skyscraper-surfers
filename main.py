import engine
import pygame
import math
import time


def main():
    pygame.init()
    pygame.display.set_caption("Skyscraper Surfers")
    width = engine.width
    height = engine.height
    fps = 60
    font = pygame.font.Font('assets/8-bit-font.ttf', 30)
    small_font = pygame.font.Font('assets/8-bit-font.ttf', 18)
    window = pygame.display.set_mode((width, height))

    #Title Screen
    onTitleScreen = True
    ALL_KEYS_OFF = tuple([0] * len(pygame.key.get_pressed()))
    selectedOption = 0
    title_image = pygame.image.load("assets/title.png").convert_alpha()
    pointer = pygame.image.load("assets/Pointer.png").convert_alpha()
    # Player
    score = 0
    highscore = 0
    player_x = 150
    player_y = 0
    player_z = -50
    player_a = 0    # Horizontal angle
    player_l = 180    # Vertical angle
    sensitivity = 30 / fps
    player_forward_speed = 1280 / fps
    dx = 0
    dy = player_forward_speed
    dz = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        buttons = pygame.key.get_pressed()
        start_frametime = time.time()
        if onTitleScreen:
            window.fill((0,0,0))
            player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz

            framebuffer = engine.draw3D(player_x, player_y, player_z, player_a, player_l, False)
            pygame.surfarray.blit_array(window, framebuffer)

            buttons = pygame.key.get_pressed()
            if buttons[pygame.K_DOWN] and selectedOption<1:
                selectedOption+=1
            if buttons[pygame.K_UP] and selectedOption>0:
                selectedOption-=1
            if buttons[pygame.K_RETURN] or buttons[pygame.K_SPACE]:
                match selectedOption:
                    case 0:
                        onTitleScreen = False
                    case _:
                        pass
            hiscore_text = font.render(f"HI: {highscore}", True, (255,0,0))
            start_text = font.render("START", True, (255,0,0))
            help_text = font.render("HELP", True, (255,0,0))
            window.blit(hiscore_text, (window.get_width()//2 - hiscore_text.get_width()//2, 150))
            window.blit(pointer, (500, 207+50*selectedOption))
            window.blit(start_text, (window.get_width()//2 - start_text.get_width()//2, 200))
            window.blit(help_text, (window.get_width()//2 - help_text.get_width()//2, 250))
            window.blit(title_image, ((window.get_width() - title_image.get_width()) // 2, 5))

            pygame.display.flip()
            time_passed = time.time() - start_frametime
            pygame.time.delay(int(1000 / fps - time_passed))
            continue

        score += 1
        if score>highscore:
            highscore = score
        # player_a, player_l = playerMovement(player_a, player_l)
        dx, dy, dz, player_a, player_l = cameraMovement(player_a, player_l, buttons, player_forward_speed, sensitivity)
        
        player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz

        window.fill((0, 0, 0))
        framebuffer = engine.draw3D(player_x, player_y, player_z, player_a, player_l, True)
        pygame.surfarray.blit_array(window, framebuffer)
        score_text = small_font.render(f"{score}", True, (255,0,0))
        hiscore_text = small_font.render(f"HI: {highscore}", True, (255,0,0))
        window.blit(score_text, (window.get_width()//2 - score_text.get_width()//2, 5))
        window.blit(hiscore_text, (window.get_width() - hiscore_text.get_width() - 5, 5))
        pygame.display.flip()

        if buttons[pygame.K_ESCAPE]:
            onTitleScreen = True
            score = 0
        time_passed = time.time() - start_frametime
        pygame.time.delay(int(1000 / fps - time_passed))

def cameraMovement(player_a, player_l, buttons, player_forward_speed, sensitivity):
    # Camera movement
    dx = 0
    dy = player_forward_speed
    dz = 0
    # Camera
    # Horizontal angle
    if buttons[pygame.K_LEFT]:
        dx = -3
        player_a -= sensitivity
        if player_a < 0:
            player_a = player_a + 360
    if buttons[pygame.K_RIGHT]:
        dx = 3
        player_a += sensitivity
        if player_a > 360:
            player_a = player_a - 360
    # Look angle
    if buttons[pygame.K_DOWN]:
        player_l -= sensitivity
    if buttons[pygame.K_UP]:
        player_l += sensitivity

    return dx, dy, dz, player_a, player_l

def playerMovement(player_a, player_l, buttons):
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

if __name__ == "__main__":
    main()