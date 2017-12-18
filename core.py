import pygame

pygame.init()

displayWidth = 1280
displayHeight = 720

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight), pygame.NOFRAME)
pygame.display.set_caption("ATDS")

clock = pygame.time.Clock()

# Colours #
black = (0,0,0)
grey = (105,105,105)
white = (255,255,255)
red = (255,0,0)
###

class Player(pygame.sprite.Sprite):
    """
    This is the player's actor
    """
    def __init__(self, x = 10, y = 10, w = 15, h = 15, colour = red):
        """
        Parameters provided allow for a better customisation of the player "model"
        """
        super().__init__()

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.colour = colour
        self.speed = 1

        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.colour)
        #self.image.set_colorkey(white)
        self.rect = self.image.get_rect()

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

    def drawCrosshair(self, mouse):
        # line to player
        pygame.draw.aaline(gameDisplay, black, mouse, (self.rect.x + (self.w / 2), self.rect.y + (self.h / 2)), 2)
        # top hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 1, mouse[1] - 10, 2, 6])
        # bottom hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 1, mouse[1] + 4, 2, 6])
        # left hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 10, mouse[1] - 1, 6, 2])
        # right hair
        pygame.draw.rect(gameDisplay, black, [mouse[0] + 4, mouse[1] - 1, 6, 2])

    def move(self, direction):
        if direction == 'u':
            self.rect.y -= self.speed
        if direction == 'd':
            self.rect.y += self.speed
        if direction == 'l':
            self.rect.x -= self.speed
        if direction == 'r':
            self.rect.x += self.speed

    """
    def shoot(self, mouse):
        xDiff = self.x - mouse[0]
        yDiff = self.y - mouse[1]
        xStep = xDiff
        yStep = yDiff
        while xStep > 5 or yStep > 5: #reduce to small increments to increase accuracy, increases time taken
            xStep = xStep/2
            yStep = yStep/2
    """

class Guard():
    """
    These are the bad guys
    """
    def __init__(self, x, y, w, h, speed = 1.2):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = speed

    def draw(self):
        pygame.draw.rect(gameDisplay, black, [self.x, self.y, self.w, self.h])

    def goto(self, x, y):
        """
        Stopping in close proximity (as opposed to on top of the target) only works if the 2 rectangles are the same width
        """

        # x co-ordinate #
        if abs(self.x - x) > self.w + self.speed:
            if x < self.x:
                self.x -= self.speed
            elif x > self.x:
                self.x += self.speed
        elif abs(self.x - x) <= self.w + self.speed and abs(self.x - x) >= self.w: # fine adjusment
            if x < self.x:
                self.x -= 0.1
            elif x > self.x:
                self.x += 0.1
        ###

        # y co-ordinate #
        if abs(self.y - y) > self.w + self.speed:
            if y < self.y:
                self.y -= self.speed
            elif y > self.y:
                self.y += self.speed
        elif abs(self.y - y) <= self.w + self.speed and abs(self.y - y) >= self.w: # fine adjustment
            if y < self.y:
                self.y -= 0.1
            elif y > self.y:
                self.y += 0.1
        ###

class Obstacle():
    """
    Those things we love to hit our heads against
    """
    def __init__(self, vertices, destructable = False):
        """
        Define the shape and destructability of the wall
        """
        self.destructable = destructable
        self.vertices = vertices

        # Obstacle will be grey if you can break it
        if self.destructable:
            self.colour = black
        else:
            self.colour = grey

    def __str__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "This obstacle has {vnum} vertices, of which the co-ordinates are {vs}".format(vnum = len(self.vertices), vs = self.vertices)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "This obstacle has {vnum} vertices, of which the co-ordinates are {vs}".format(vnum = len(self.vertices), vs = self.vertices)

    def draw(self):
        pygame.draw.polygon(gameDisplay, self.colour, self.vertices)

def instance():
    running = True

    player = Player()
    guard = Guard(500, 500, 15, 15)
    wallTest = Obstacle(((100,100), (100,200), (150,200), (220,200), (140, 50)), False)

    allSpritesList = pygame.sprite.Group()
    allSpritesList.add(player)

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

                # close game if escape is pressed
                if event.key == pygame.K_ESCAPE:
                    running = False
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
        wallTest.draw()
        guard.goto(player.rect.x, player.rect.y)
        guard.draw()
        player.drawCrosshair(pygame.mouse.get_pos())
        allSpritesList.draw(gameDisplay)
        ###

        pygame.display.update()
        clock.tick(120)

    pygame.quit()

instance()
