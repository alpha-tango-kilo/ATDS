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
    def __init__(self, x = 10, y = 10, w = 15, h = 15):
        """
        Parameters provided allow for a better customisation of the player "model"
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

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

def player(colour, x, y, w, h):
    pygame.draw.rect(gameDisplay, colour, [x, y, w, h])

def drawCrosshair(mouse, player, colour=black):
    # top hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] - 1, mouse[1] - 10, 2, 6])
    # bottom hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] - 1, mouse[1] + 4, 2, 6])
    # left hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] - 10, mouse[1] - 1, 6, 2])
    # right hair
    pygame.draw.rect(gameDisplay, colour, [mouse[0] + 4, mouse[1] - 1, 6, 2])
    pygame.draw.lines(gameDisplay, colour, mouse, player, 2)

def instance():
    running = True
    playerx = 10
    playery = 10

    # hide mouse
    pygame.mouse.set_visible(False)

    while running:
        for event in pygame.event.get():
            #print(event)

            # Any actions should be put here #

            # Quit the game
            if event.type == pygame.QUIT:
                pygame.quit()

            # Key pressed (triggers once, even if held) #
            if event.type == pygame.KEYDOWN:
                pass
            ###

        # Keys being held #
        keys = pygame.key.get_pressed()

        # W
        if keys[pygame.K_w]:
            playery -= 1
            print("up")
        # A
        if keys[pygame.K_a]:
            playerx -= 1
            print("left")
        # S
        if keys[pygame.K_s]:
            playery += 1
            print("down")
        # D
        if keys[pygame.K_d]:
            playerx += 1
            print("right")
        ###

        mousePos = pygame.mouse.get_pos()
        #print(mousePos)

        # Draw things to screen #
        gameDisplay.fill(white)
        player(red, playerx, playery, 15, 15)
        drawCrosshair(mousePos, (playerx, playery), black)

        ###
        pygame.display.update()
        clock.tick(120)

instance()
