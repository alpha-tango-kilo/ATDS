import pygame

pygame.init()

displayWidth = 1280
displayHeight = 720

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("A game")

clock = pygame.time.Clock()

# Colours #
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
###

class Player():
    """
    This is the player's actor
    """
    def __init__(self, x = 10, y = 10, w = 15, h = 15, colour = red):
        """
        Parameters provided allow for a better customisation of the player "model"
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.colour = colour

    def __str__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "Player is at ({x},{y}), and is {w} x {h} pixels.".format(x = self.x, y = self.y, w = self.w, h = self.h)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "Player is at ({x},{y}), and is {w} x {h} pixels.".format(x = self.x, y = self.y, w = self.w, h = self.h)

    def draw(self, mouse):
        # Crosshair #
        # line to player
        pygame.draw.aaline(gameDisplay, black, mouse, (self.x + (self.w / 2), self.y + (self.h / 2)), 2)
        # top hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 1, mouse[1] - 10, 2, 6])
        # bottom hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 1, mouse[1] + 4, 2, 6])
        # left hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 10, mouse[1] - 1, 6, 2])
        # right hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] + 4, mouse[1] - 1, 6, 2])
        ###
        # actual character
        pygame.draw.rect(gameDisplay, self.colour, [self.x, self.y, self.w, self.h])

    def move(self, direction):
        if direction == 'u':
            self.y -= 1
        if direction == 'd':
            self.y += 1
        if direction == 'l':
            self.x -= 1
        if direction == 'r':
            self.x += 1

class Wall():
    """
    Those things we love to hit our heads against
    """
    def __init__(self, x, y, w, h):
        """
        Define size and destructability of the wall
        """
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

def instance():
    running = True

    player = Player()

    # hide mouse
    pygame.mouse.set_visible(False)

    while running:
        for event in pygame.event.get():
            # Any pygame handled events should be put here #
            # Quit the game
            if event.type == pygame.QUIT:
                running = False

            # Key pressed (triggers once, even if held) #
            if event.type == pygame.KEYDOWN:
                pass
            ###

        # Keys being held #
        keys = pygame.key.get_pressed()

        # W
        if keys[pygame.K_w]:
            player.move('u')
        # A
        if keys[pygame.K_a]:
            player.move('l')
        # S
        if keys[pygame.K_s]:
            player.move('d')
        # D
        if keys[pygame.K_d]:
            player.move('r')
        ###

        # Draw things to screen #
        gameDisplay.fill(white)
        player.draw(pygame.mouse.get_pos())
        ###

        pygame.display.update()
        clock.tick(120)

    pygame.quit()

instance()
