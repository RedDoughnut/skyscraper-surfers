import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, window: pygame.Surface, velocity):
        super().__init__()
        self.window = window
        self.orientation = 0
        self.velocity = velocity
        self.x = window.get_width()//2
        self.y = window.get_height()//2
    def update(self):
        if self.orientation == -1:
            player = pygame.image.load("assets/spaceship_left.png").convert_alpha()
        elif self.orientation == 0:
            player = pygame.image.load("assets/spaceship_idle.png").convert_alpha()
        elif self.orientation == 1:
            player = pygame.image.load("assets/spaceship_right.png").convert_alpha()
        player = pygame.image.load("assets/white.png")
        self.window.blit(player, (self.x, self.y))