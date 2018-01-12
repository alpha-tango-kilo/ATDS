import pygame#, math

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
dan = (42,117,225)
###
class World_Object():
    def getShot(self):
        print("World_Object says 'ow!'")
        return None

class Actor(pygame.sprite.Sprite, World_Object):
    def __init__(self, x = 10, y = 10, w = 15, h = 15, speed = 1, colour = black):
        super().__init__()

        """
        Parameters provided allow for a better customisation of the player "model"
        """

        self.w = w
        self.h = h
        self.colour = colour
        self.speed = speed
        self.bannedDirs = [False, False, False, False]

        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.colour)
        #self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.rect.x = round(x)
        self.rect.y = round(y)

        self.virtualx = x
        self.virtualy = y

    def __str__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "Actor is at ({x},{y}), and is {w} x {h} pixels.".format(x = self.rect.x, y = self.rect.y, w = self.w, h = self.h)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "Actor is at ({x},{y}), and is {w} x {h} pixels.".format(x = self.rect.x, y = self.rect.y, w = self.w, h = self.h)

    def simpleMove(self, direction, distance):
        if direction == 'u':
            self.virtualy -= distance
        elif direction == 'd':
            self.virtualy += distance

        if direction == 'l':
            self.virtualx -= distance
        elif direction == 'r':
            self.virtualx += distance

        self.rect.x = round(self.virtualx)
        self.rect.y = round(self.virtualy)

    def collisionCheck(self, sprGroup):
        keep = [False, False, False, False]
        directions = ['u', 'd', 'l', 'r']
        tActor = Actor(self.virtualx, self.virtualy, self.w, self.h, self.speed)
        for test in range(len(directions)):
            tActor.rect.x = self.rect.x
            tActor.rect.y = self.rect.y
            tActor.virtualx = self.virtualx
            tActor.virtualy = self.virtualy
            tActor.simpleMove(directions[test], self.speed)
            if len(pygame.sprite.spritecollide(tActor, sprGroup, False)) > 0:
                self.bannedDirs[test] = True
                keep[test] = True
            elif len(pygame.sprite.spritecollide(tActor, sprGroup, False)) == 0 and not keep[test]:
                self.bannedDirs[test] = False

    def move(self, direction, sprGroup):
        if direction == 'u' and not self.bannedDirs[0]:
            self.virtualy -= self.speed
        elif direction == 'd' and not self.bannedDirs[1]:
            self.virtualy += self.speed
        elif direction == 'l' and not self.bannedDirs[2]:
            self.virtualx -= self.speed
        elif direction == 'r' and not self.bannedDirs[3]:
            self.virtualx += self.speed

        self.rect.x = round(self.virtualx)
        self.rect.y = round(self.virtualy)
        self.collisionCheck(sprGroup) # must go after co-ordinate rounding

    def goto(self, x, y, sprGroup = None):
        """
        Stopping in close proximity (as opposed to on top of the target) only works if the 2 squares are the same width
        """

        # x co-ordinate #
        if abs(self.rect.x - x) > self.w + self.speed:
            if x < self.virtualx and not self.bannedDirs[2]:
                self.virtualx -= self.speed
            elif x > self.virtualx and not self.bannedDirs[3]:
                self.virtualx += self.speed
        elif abs(self.virtualx - x) <= self.w + self.speed and abs(self.virtualx - x) >= self.w and sprGroup == None: # fine adjusment
            if x < self.virtualx and not self.bannedDirs[2]:
                self.virtualx -= 0.1
            elif x > self.virtualx and not self.bannedDirs[3]:
                self.virtualx += 0.1
        ###

        # y co-ordinate #
        if abs(self.rect.y - y) > self.w + self.speed:
            if y < self.virtualy and not self.bannedDirs[0]:
                self.virtualy -= self.speed
            elif y > self.virtualy and not self.bannedDirs[1]:
                self.virtualy += self.speed
        elif abs(self.virtualy - y) <= self.w + self.speed and abs(self.virtualy - y) >= self.w and sprGroup == None: # fine adjustment
            if y < self.virtualy and not self.bannedDirs[0]:
                self.virtualy -= 0.1
            elif y > self.virtualy and not self.bannedDirs[1]:
                self.virtualy += 0.1
        ###

        self.rect.x = round(self.virtualx)
        self.rect.y = round(self.virtualy)
        self.collisionCheck(sprGroup)

    def shoot(self, mouse, sprGroup):
        bullet = Projectile(self.virtualx, self.virtualy, mouse)
        bullet.go(sprGroup)

class Player(Actor):
    """
    This is the player's actor
    """
    def __init__(self, x = 10, y = 10, w = 15, h = 15, colour = red):
        super().__init__(x, y, w, h, 1, colour)

    def drawCrosshair(self, mouse):
        # line to player
        pygame.draw.aaline(gameDisplay, black, mouse, (self.virtualx + (self.w / 2), self.virtualy + (self.h / 2)), 2)
        # top hair
        pygame.draw.rect(gameDisplay, white, [mouse[0] - 2, mouse[1] - 11, 4, 8])
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 1, mouse[1] - 10, 2, 6])
        # bottom hair
        pygame.draw.rect(gameDisplay, white, [mouse[0] - 2, mouse[1] + 3, 4, 8])
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 1, mouse[1] + 4, 2, 6])
        # left hair
        pygame.draw.rect(gameDisplay, white, [mouse[0] - 11, mouse[1] - 2, 8, 4])
        pygame.draw.rect(gameDisplay, black, [mouse[0] - 10, mouse[1] - 1, 6, 2])
        # right hair
        pygame.draw.rect(gameDisplay, white, [mouse[0] + 3, mouse[1] - 2, 8, 4])
        pygame.draw.rect(gameDisplay, black, [mouse[0] + 4, mouse[1] - 1, 6, 2])

    def drawCone(self, mouse):
        pass

class Guard(Actor):
    """
    These are the bad guys
    """
    def __init__(self, x, y, w, h, speed = 1.2, colour = black):
        super().__init__(x, y, w, h, speed, colour)

class Obstacle(pygame.sprite.Sprite, World_Object):
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

    def __str__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "({x}, {y})".format(x = self.rect.x, y = self.rect.y)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is
        returned
        """
        return "({x}, {y})".format(x = self.rect.x, y = self.rect.y)

    def getShot(self):
        if self.destructable: # wall breaks
            self.kill()
            print("You killed a wall, you monster")
            return None
        else:
            print("You shot a wall, I hope you get more gratification from this than the programmer did writing this line.")
            return None

class Projectile(pygame.sprite.Sprite):
    """
    The pew pew things
    """
    def __init__(self, x, y, mouse):
        super().__init__()
        self.xStep = mouse[0] - x
        self.yStep = mouse[1] - y
        self.moveXfirst = False

        if self.xStep < self.yStep:
            self.yStep = self.yStep / self.xStep
            self.xStep = 1
            self.moveXfirst = True
        else:
            self.xStep = self.xStep / self.yStep
            self.yStep = 1

        self.image = pygame.Surface([2, 2])
        self.image.fill(black)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.virtualx = x
        self.virtualy = y

    def go(self, sprGroup):
        while len(pygame.sprite.spritecollide(self, sprGroup, False)) == 0:
            if self.rect.x > displayWidth or self.rect.x + 2 < 0 or self.rect.y > displayHeight or self.rect.y < 0:
                return None
            self.virtualx += self.xStep
            self.virtualy += self.yStep

            if self.moveXfirst:
                self.rect.x = self.virtualx
                self.rect.y = int(round(self.virtualy))
            else:
                self.rect.x = int(round(self.virtualx))
                self.rect.y = self.virtualy

        collidedWith = pygame.sprite.spritecollide(self, sprGroup, False)[0]
        collidedWith.getShot()
        return collidedWith

def instance():
    running = True

    # Prevent player from leaving the screen
    gameBoundTop = Obstacle(0, -10, displayWidth, 10, False)
    gameBoundBottom = Obstacle(0, displayHeight, displayWidth, 10, False)
    gameBoundLeft = Obstacle(-10, 0, 10, displayHeight, False)
    gameBoundRight = Obstacle(displayWidth, 0, 10, displayHeight, False)

    player = Player()
    guard = Guard(500, 500, 15, 15, 1.2, dan)
    wall = Obstacle(200, 200, 300, 150, False)
    wall2 = Obstacle(700, 600, 200, 20, True)

    allSprites = pygame.sprite.Group()
    allSprites.add(player)
    allSprites.add(guard)
    allSprites.add(wall)
    allSprites.add(wall2)

    environmentSprites = pygame.sprite.Group()
    environmentSprites.add(wall)
    environmentSprites.add(wall2)
    environmentSprites.add(gameBoundTop)
    environmentSprites.add(gameBoundBottom)
    environmentSprites.add(gameBoundLeft)
    environmentSprites.add(gameBoundRight)

    guards = pygame.sprite.Group()
    guards.add(guard)

    shootables = pygame.sprite.Group()
    shootables.add(guard)
    shootables.add(wall)
    shootables.add(wall2)

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

            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(pygame.mouse.get_pos(), shootables)
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

        # Continuous functions #
        gameDisplay.fill(white)
        guard.goto(player.virtualx, player.virtualy, environmentSprites)
        player.drawCrosshair(pygame.mouse.get_pos())
        player.drawCone(pygame.mouse.get_pos())
        allSprites.draw(gameDisplay)
        ###

        #print(pygame.sprite.spritecollide(player, environmentSprites, False))

        """
        collided = pygame.sprite.spritecollide(player, environmentSprites, False) # returns array of repr of objects collided with
        guardHit = pygame.sprite.collide_rect(player, guard) # returns boolean
        """

        pygame.display.update()
        clock.tick(120)

    pygame.quit()

instance()
