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

    def draw(self):
        pygame.draw.rect(gameDisplay, self.colour, [self.x, self.y, self.w, self.h])

def drawCrosshair(mouse, player, colour=black):
    # top hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] - 1, mouse[1] - 10, 2, 6])
    # bottom hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] - 1, mouse[1] + 4, 2, 6])
    # left hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] - 10, mouse[1] - 1, 6, 2])
    # right hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] + 4, mouse[1] - 1, 6, 2])
    #pygame.draw.lines(gameDisplay, colour, mouse, player, 2)

def instance():
    running = True

    player = Player()

    # hide mouse
    pygame.mouse.set_visible(False)

    while running:
        for event in pygame.event.get():
            #print(event)

            # Any actions should be put here #

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
            player.y -= 1
            print("up")
        # A
        if keys[pygame.K_a]:
            player.x -= 1
            print("left")
        # S
        if keys[pygame.K_s]:
            player.y += 1
            print("down")
        # D
        if keys[pygame.K_d]:
            player.x += 1
            print("right")
        ###

        mousePos = pygame.mouse.get_pos()
        #print(mousePos)

        # Draw things to screen #
        gameDisplay.fill(white)
        #player(red, player.x, player.y, 15, 15)
        player.draw()
        drawCrosshair(mousePos, (player.x, player.y), black)

        ###
        pygame.display.update()
        clock.tick(120)

    pygame.quit()

instance()
