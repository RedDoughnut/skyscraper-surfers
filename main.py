import engine
import pygame
from pygame import mixer
import math
import time
import sys
import numpy

def main():
    pygame.init()
    pygame.font.init()
    mixer.init()
    start_frametime = 0
    volume = 0.2
    sfx = True

    mixer.music.load("assets/ACybersWorld.mp3")
    mixer.music.set_volume(volume)
    mixer.music.play(-1)
    boom = mixer.Sound("assets/explosion.mp3")
    boom.set_volume(0.1)

    pygame.display.set_caption("Skyscraper Surfers")
    width = engine.width
    height = engine.height
    fps = 60
    font = pygame.font.Font('assets/8-bit-font.ttf', 30)
    small_font = pygame.font.Font('assets/8-bit-font.ttf', 18)
    window = pygame.display.set_mode((width, height))

    #Title Screen
    onTitleScreen = True
    screen = 0 # 0 - main 1 - help 2 - settings
    ALL_KEYS_OFF = tuple([0] * len(pygame.key.get_pressed()))
    selectedOption = 0
    title_image = pygame.image.load("assets/title.png").convert_alpha()
    pointer = pygame.image.load("assets/Pointer.png").convert_alpha()
    # Player
    score = 0
    highscore = read_highscore()
    player_x = 150
    player_y = 0
    player_z = -50
    player_a = 0    # Horizontal angle
    player_l = 180    # Vertical angle
    sensitivity = 30 / fps
    player_forward_speed = 1280 / fps
    left_right_speed = 480 / fps
    dx = 0
    dy = player_forward_speed
    dz = 0

    time_per_frame = 0
    time_since_last = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        buttons = pygame.key.get_pressed()
        if onTitleScreen:
            window.fill((0,0,0))
            
            if True: #screen==0:
                player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz

                framebuffer = numpy.zeros((width, height, 3), numpy.uint8)
                framebuffer[:, height // 2 - player_l + 180: height] = (50, 50, 50)
                framebuffer = engine.draw3D(player_x, player_y, player_z, player_a, player_l, False, framebuffer)
                pygame.surfarray.blit_array(window, framebuffer)

            buttons = pygame.key.get_pressed()
            if buttons[pygame.K_DOWN] and selectedOption<3 and screen == 0 and time.time() - time_since_last>0.2:
                selectedOption+=1
                time_since_last = time.time()
            if buttons[pygame.K_UP] and selectedOption>0 and screen == 0 and time.time() - time_since_last>0.2:
                selectedOption-=1
                time_since_last = time.time()
            if buttons[pygame.K_RETURN] or buttons[pygame.K_SPACE] and screen == 0:
                if selectedOption == 0:
                    onTitleScreen = False
                    mixer.music.load("assets/CORE.mp3")
                    mixer.music.play(-1)
                    player_x = 150
                    player_y = 0
                    score = 0
                    player_z = -50
                    player_a = 0 
                    player_l = 180
                    engine.loadMap()

                elif selectedOption == 1:
                    screen = 2
                elif selectedOption == 2:
                    screen = 1
                elif selectedOption == 3:
                    pygame.quit()
                    sys.exit()
            if screen == 0:
                hiscore_text = font.render(f"HI: {highscore}", True, (255,0,0))
                settings_text = font.render("SETTINGS", True, (255,0,0))
                start_text = font.render("START", True, (255,0,0))
                help_text = font.render("HELP", True, (255,0,0))
                quit_text = font.render("QUIT", True, (255,0,0))
                window.blit(hiscore_text, (window.get_width()//2 - hiscore_text.get_width()//2, 150))
                window.blit(pointer, (450, 207+50*selectedOption))
                window.blit(start_text, (window.get_width()//2 - start_text.get_width()//2, 200))
                window.blit(settings_text, (window.get_width()//2 - settings_text.get_width()//2, 250))
                window.blit(help_text, (window.get_width()//2 - help_text.get_width()//2, 300))
                window.blit(quit_text, (window.get_width()//2 - help_text.get_width()//2, 350))
                window.blit(title_image, ((window.get_width() - title_image.get_width()) // 2, 5))
            elif screen == 1:
                if buttons[pygame.K_q]:
                    screen = 0
                text1 = font.render("YOU ARE DRIVING A SPACESHIP, THE GOAL", True, (255,0,0))
                text2 = font.render("IS TO AVOID ALL THE SKYSCRAPERS", True, (255,0,0))
                text3 = font.render("USE ARROW KEYS FOR CONTROLS", True, (255,0,0))
                text4 = font.render("PRESS Q TO LEAVE", True, (255,0,0))
                window.blit(text1, (window.get_width()//2 - text1.get_width()//2, 100))
                window.blit(text2, (window.get_width()//2 - text2.get_width()//2, 150))
                window.blit(text3, (window.get_width()//2 - text3.get_width()//2, 200))
                window.blit(text4, (window.get_width()//2 - text4.get_width()//2, 250))
            elif screen == 2:
                if buttons[pygame.K_q]:
                    screen = 0
                mouse = pygame.mouse.get_pressed()
                mousepos = pygame.mouse.get_pos()
                if mouse[0] and mousepos[1]>=110 and mousepos[1]<=150 and mousepos[0]>=370 and mousepos[0]<830:
                    volume = (mousepos[0]-400)/400
                    if volume>1.0:
                        volume = 1.0
                    elif volume<0:
                        volume = 0
                    mixer.music.set_volume(volume)
                elif mouse[0] and mousepos[0]>window.get_width()//2-55 and mousepos[0]<window.get_width()//2-25 and mousepos[1]>229 and mousepos[1]<259 and time.time() - time_since_last>0.2:
                    sfx = not sfx
                    time_since_last = time.time()
                volumetext = font.render("VOLUME", True, (255,0,0))
                volumetext2 = font.render(f"{round(volume*100)}", True, (255,0,0))
                sfxtext = font.render("SFX", True, (255,0,0))
                quittext = font.render("PRESS Q TO LEAVE", True, (255,0,0))
                window.blit(volumetext, (window.get_width()//2 - volumetext.get_width()//2, 60))
                window.blit(volumetext2, (window.get_width()//2 - volumetext2.get_width()//2, 160))
                window.blit(sfxtext, (window.get_width()//2 - 15, 230))
                window.blit(quittext, (window.get_width()//2 - quittext.get_width()//2, 560))
                pygame.draw.rect(window, (255,0,0), (400,120,400,20), border_radius=5)
                pygame.draw.rect(window, (255,0,0), (window.get_width()//2-55, 229, 30, 30), width = 3)
                if sfx:
                    sfxTick = small_font.render("X", True, (255,0,0))
                    window.blit(sfxTick, (window.get_width()//2-49,235))
                pygame.draw.circle(window, (255,255,255), (400+400*volume,130), 15)
            pygame.display.flip()
            rendertime = time.time() - start_frametime
            start_frametime = time.time()
            pygame.time.delay(int(1000 / fps - rendertime))
            continue
        
        score += 1
        if score>highscore:
            highscore = score
        # dx, dy, dz, player_a, player_l = playerMovement(player_a, player_l, buttons)
        dx, dy, dz, player_a, player_l = cameraMovement(player_a, player_l, buttons, player_forward_speed, left_right_speed, sensitivity)
        # print(f"{player_x:}, {player_y:}, {player_z:}")
        player_x = player_x + dx; player_y = player_y + dy; player_z = player_z + dz
        window.fill((0, 0, 0))
        framebuffer = numpy.zeros((width, height, 3), numpy.uint8)
        framebuffer[:, height // 2 + int(player_l*6) - 180*6: height] = (100, 100, 50)
        framebuffer = engine.draw3D(player_x, player_y, player_z, player_a, player_l, True, framebuffer)
        pygame.surfarray.blit_array(window, framebuffer)

        engine.loadFps(fps)

        if engine.checkQuit():
            if score > read_highscore():
                highscore = score
                try:
                    with open("assets/highscore.txt", "w") as f:
                        f.write(str(highscore))
                except Exception as e:
                    print(f"Error writing highscore: {e}")
            onTitleScreen = True
            score = 0
            if sfx:
                boom.play()
            mixer.music.load("assets/ACybersWorld.mp3")
            mixer.music.play(-1)
            screen = 0
            dx, dy, dz = 0, 0, 0
    
        
        score_text = small_font.render(f"{score}", True, (255,0,0))
        hiscore_text = small_font.render(f"HI: {highscore}", True, (255,0,0))
        fps_text = small_font.render(f"FPS: {int(1 / rendertime) if rendertime > 0 else 0}", True, (255,0,0))
        window.blit(score_text, (window.get_width()//2 - score_text.get_width()//2, 5))
        window.blit(hiscore_text, (window.get_width() - hiscore_text.get_width() - 5, 5))
        window.blit(fps_text, (5, 5))


        pygame.display.flip()
        if buttons[pygame.K_q]:
            onTitleScreen = True
            screen = 0
            score = 0
            mixer.music.load("assets/ACybersWorld.mp3")
            mixer.music.play(-1)
        # print(frametime * 1000)
        rendertime = time.time() - start_frametime
        pygame.time.delay(int(1000 / fps - rendertime))
        # print(1000 / fps)
        frametime = time.time() - start_frametime
        start_frametime = time.time()


def cameraMovement(player_a, player_l, buttons, player_forward_speed, speed, sensitivity):
    # Camera movement
    dx = 0
    dy = player_forward_speed
    dz = 0
    # Camera
    # Horizontal angle
    if buttons[pygame.K_LEFT]:
        dx += -speed  # was 3
        # player_a -= sensitivity
        # if player_a < 0:
        #     player_a = player_a + 360
    if buttons[pygame.K_RIGHT]:
        dx += speed # was 3
        # player_a += sensitivity
        # if player_a > 360:
        #     player_a = player_a - 360
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
    # X54
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

    return dx, dy, dz, player_a, player_l
def read_highscore():
    try:
        with open("assets/highscore.txt", "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

if __name__ == "__main__":
    main()
