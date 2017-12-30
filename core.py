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

        self.w = w
        self.h = h
        self.colour = colour
        self.speed = 1
        self.bannedDirs = [False, False, False, False]

        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.colour)
        #self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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

    def move(self, direction, sprGroup = None):

        if direction == 'u' and not self.bannedDirs[0]:
            self.rect.y -= self.speed
        elif direction == 'd' and not self.bannedDirs[1]:
            self.rect.y += self.speed
        elif direction == 'l' and not self.bannedDirs[2]:
            self.rect.x -= self.speed
        elif direction == 'r' and not self.bannedDirs[3]:
            self.rect.x += self.speed

        if sprGroup:
            keep = [False, False, False, False]
            directions = ["u", "d", "l", "r"]
            for spr in sprGroup:
                tPlayer = Player(self.rect.x, self.rect.y, self.w, self.h)
                for test in range(len(directions)):
                    tPlayer.rect.x = self.rect.x
                    tPlayer.rect.y = self.rect.y
                    tPlayer.move(directions[test])
                    if pygame.sprite.collide_rect(tPlayer, spr):
                        self.bannedDirs[test] = True
                        keep[test] = True
                    elif not pygame.sprite.collide_rect(tPlayer, spr) and not keep[test]:
                        self.bannedDirs[test] = False

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

class Guard(pygame.sprite.Sprite):
    """
    These are the bad guys
    """
    def __init__(self, x, y, w, h, speed = 1.2, colour = black):

        super().__init__()

        self.w = w
        self.h = h
        self.colour = colour
        self.speed = speed

        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def draw(self):
        pygame.draw.rect(gameDisplay, black, [self.x, self.y, self.w, self.h])

    def goto(self, x, y):
        """
        Stopping in close proximity (as opposed to on top of the target) only works if the 2 rectangles are the same width
        """

        # x co-ordinate #
        if abs(self.rect.x - x) > self.w + self.speed:
            if x < self.rect.x:
                self.rect.x -= self.speed
            elif x > self.rect.x:
                self.rect.x += self.speed
        elif abs(self.rect.x - x) <= self.w + self.speed and abs(self.rect.x - x) >= self.w: # fine adjusment
            if x < self.rect.x:
                self.rect.x -= 0.1
            elif x > self.rect.x:
                self.rect.x += 0.1
        ###

        # y co-ordinate #
        if abs(self.rect.y - y) > self.w + self.speed:
            if y < self.rect.y:
                self.rect.y -= self.speed
            elif y > self.rect.y:
                self.rect.y += self.speed
        elif abs(self.rect.y - y) <= self.w + self.speed and abs(self.rect.y - y) >= self.w: # fine adjustment
            if y < self.rect.y:
                self.rect.y -= 0.1
            elif y > self.rect.y:
                self.rect.y += 0.1
        ###

class Obstacle(pygame.sprite.Sprite):
    """
    Those things we love to hit our heads against
    """
    def __init__(self, x, y, w, h, destructable = False):
        """
        Define the shape and destructability of the wall
        """
        super().__init__()

        self.w = w
        self.h = h
        self.destructable = destructable

        # Obstacle will be grey if you can break it
        if self.destructable:
            self.colour = grey
        else:
            self.colour = black

        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "({x}, {y})".format(x = self.rect.x, y = self.rect.y)

def instance():
    running = True

    # Prevent player from leaving the screen
    gameBoundTop = Obstacle(0, -10, displayWidth, 10, False)
    gameBoundBottom = Obstacle(0, displayHeight, displayWidth, 10, False)
    gameBoundLeft = Obstacle(-10, 0, 10, displayHeight, False)
    gameBoundRight = Obstacle(displayWidth, 0, 10, displayHeight, False)

    player = Player()
    guard = Guard(500, 500, 15, 15)
    wall = Obstacle(200, 200, 300, 150, False)
    wall2 = Obstacle(700, 600, 200, 20, True)

    allSprites = pygame.sprite.Group()
    allSprites.add(player)
    allSprites.add(guard)
    allSprites.add(wall)
    allSprites.add(wall2)
    allSprites.add(gameBoundTop)
    allSprites.add(gameBoundBottom)
    allSprites.add(gameBoundLeft)
    allSprites.add(gameBoundRight)

    environmentSprites = pygame.sprite.Group()
    environmentSprites.add(wall)
    environmentSprites.add(wall2)
    environmentSprites.add(gameBoundTop)
    environmentSprites.add(gameBoundBottom)
    environmentSprites.add(gameBoundLeft)
    environmentSprites.add(gameBoundRight)

    guards = pygame.sprite.Group()
    guards.add(guard)

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
            player.move('u', environmentSprites)
        # A
        if keys[pygame.K_a]:
            player.move('l', environmentSprites)
        # S
        if keys[pygame.K_s]:
            player.move('d', environmentSprites)
        # D
        if keys[pygame.K_d]:
            player.move('r', environmentSprites)
        ###

        # Draw things to screen #
        gameDisplay.fill(white)
        guard.goto(player.rect.x, player.rect.y)
        player.drawCrosshair(pygame.mouse.get_pos())
        allSprites.draw(gameDisplay)
        ###

        """
        collided = pygame.sprite.spritecollide(player, environmentSprites, False) # returns array of repr of objects collided with
        guardHit = pygame.sprite.collide_rect(player, guard) # returns boolean
        """

        pygame.display.update()
        clock.tick(120)

    pygame.quit()

instance()
