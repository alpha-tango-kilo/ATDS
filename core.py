import pygame
import math as m
import random as rng

pygame.init()

# Global constants #
directions = ['u','l','d','r']
displayWidth = 1280
displayHeight = 720
framerate = 120
myfont = pygame.font.SysFont("monospace", 16)
# Colours #
black = (0,0,0)
grey = (105,105,105)
white = (255,255,255)
red = (255,0,0)
dan = (42,117,225)
lightgrey = (230,230,230)
###
###

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight), pygame.NOFRAME)
pygame.display.set_caption("ATDS")

clock = pygame.time.Clock()

class World_Object(): # any object that is visible to and interactive with the player should inherit from this class
    def getShot(self): # a default case for any object rendered to the screen being shot, needed otherwise projectiles will error
        print("World_Object says 'ow!'")
        return None

class Point():
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def distance(self, point):
        return m.sqrt((self.x - point.x)**2 + (self.y - point.y)**2)

class Actor(pygame.sprite.Sprite, World_Object):
    def __init__(self, x = 10, y = 10, w = 15, h = 15, speed = 1, colour = black):
        super().__init__() # inits sprite

        """
        Parameters provided allow for a better customisation of the player "model"
        """

        self.w = w # width
        self.h = h # height
        self.colour = colour
        self.speed = speed
        self.bannedDirs = [False for _ in range(4)] # used with collision detection to determine directions in which the actor can't move

        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(self.colour) # creates a rectangular picture for the sprite using given parameters
        #self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.rect.x = round(x) # accounts for float inputs
        self.rect.y = round(y)

        self.virtualx = x # allows for decimal movement
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
        if direction == 'u': # up
            self.virtualy -= distance
        elif direction == 'd': # down
            self.virtualy += distance

        if direction == 'l': # left and right are in an independent if statement to up and down to allow for diagonal movement
            self.virtualx -= distance # left
        elif direction == 'r':
            self.virtualx += distance # right

        self.rect.x = round(self.virtualx) # update physical (pixel) co-ordinates
        self.rect.y = round(self.virtualy)

    def collisionCheck(self, sprGroup):
        keep = [False for _ in range(4)] # used to preserve banned directions if a test says the actor can't move up but another test says the actor can move up
        directions = ['u', 'd', 'l', 'r'] # we were never told we had to be proud of our solutions...
        tActor = Actor(self.virtualx, self.virtualy, self.w, self.h, self.speed) # create a clone of the actor being tested, with the same key characteristics (colour is not important as tActor will never be drawn to screen)
        for test in range(len(directions)): # iterates from 0 to 3
            tActor.rect.x = self.rect.x # resets all co-ordinates for each test
            tActor.rect.y = self.rect.y
            tActor.virtualx = self.virtualx
            tActor.virtualy = self.virtualy
            tActor.simpleMove(directions[test], self.speed) # uses movement function without collision checking
            if len(pygame.sprite.spritecollide(tActor, sprGroup, False)) > 0: # checks if an objects are collided with from sprGroup (typically environmentSprites)
                self.bannedDirs[test] = True # bans direction
                keep[test] = True # ensures that banned direction is not overwritten
            elif len(pygame.sprite.spritecollide(tActor, sprGroup, False)) == 0 and not keep[test]: # if there are no collisions and the direction has no already been banned in this test battery...
                self.bannedDirs[test] = False # ...allow movement in this direction

    def move(self, direction, sprGroup):
        if direction == 'u' and not self.bannedDirs[0]: # up
            self.virtualy -= self.speed
        elif direction == 'd' and not self.bannedDirs[1]: # down
            self.virtualy += self.speed
        elif direction == 'l' and not self.bannedDirs[2]: # left
            self.virtualx -= self.speed
        elif direction == 'r' and not self.bannedDirs[3]: # right
            self.virtualx += self.speed

        self.rect.x = round(self.virtualx) # update physical co-ords
        self.rect.y = round(self.virtualy)

        if sprGroup:
            self.collisionCheck(sprGroup) # must go after co-ordinate rounding

    def shoot(self, target, sprGroup):
        bullet = Projectile(self.virtualx + (self.w / 2) - 1, self.virtualy + (self.h / 2) - 1, target) # create a bullet, such that its centre is the actor's centre
        bullet.go(sprGroup) # fires bullet (dramatically)

    def drawCone(self, mouse, fov, distance):
        fov = m.radians(fov) # convert fov to radians

        # Mr. Marshall's code #

        dx = mouse[0] - (self.rect.x + (self.w / 2))
        dy = mouse[1] - (self.rect.y + (self.w / 2))
        mod_m = m.sqrt(dx**2 + dy**2)
        sf = distance/mod_m
        centre_x = sf*dx + (self.rect.x + (self.w / 2))
        centre_y = sf*dy + (self.rect.y + (self.w / 2))

        angle_sf = sf*m.tan(fov/2)

        perp_dx = dy
        perp_dy = -dx
        corner1_x = centre_x + angle_sf*perp_dx
        corner1_y = centre_y + angle_sf*perp_dy
        corner2_x = centre_x - angle_sf*perp_dx
        corner2_y = centre_y - angle_sf*perp_dy

        # End Mr. Marshall magic #

        xDiff = corner1_x - self.virtualx # work out difference from point to actor
        yDiff = self.virtualy - corner1_y
        angFromVert = 0.0 # initialise as float

        if yDiff != 0: # to prevent 0 division errors
            if corner1_y < self.rect.y: # I don't know, it just works
                angFromVert = -1 * m.atan(xDiff / yDiff)
            else:
                angFromVert = -1 * m.atan(xDiff / yDiff) + m.pi
        elif xDiff > 0: # looking exactly right
            angFromVert = 0.5 * m.pi
        elif xDiff < 0: # looking exactly left
            angFromVert = 1.5 * m.pi

        viewBox = pygame.Surface([(distance * 2), (distance * 2)]) # create large square upon which to draw arc (pygame things)
        viewBox.fill(white)
        arcRect = viewBox.get_rect()
        arcRect.x = round(self.virtualx - distance + (self.w / 2)) # move square such that the centre of the player is at the centre of the square
        arcRect.y = round(self.virtualy - distance + (self.h / 2))

        pygame.draw.rect(gameDisplay, black, arcRect, 2)

        pygame.draw.arc(viewBox, black, arcRect, angFromVert, angFromVert + fov, round(distance)) # draw the arc to the virtual surface, for mask creation purposes
        pygame.draw.arc(gameDisplay, lightgrey, arcRect, angFromVert, angFromVert + fov, round(distance)) # why is this not filled in properly

        viewBox.set_colorkey(white)
        actorMask = pygame.mask.from_surface(viewBox) # create mask of arc *WORKING CORRECTLY*
        #print(actorMask.count())

        pygame.draw.aaline(gameDisplay, black, ((self.rect.x + (self.w / 2)), (self.rect.y + (self.h / 2))), (corner1_x, corner1_y))
        pygame.draw.aaline(gameDisplay, black, (self.rect.x + (self.w / 2), self.rect.y + (self.h / 2)), (corner2_x, corner2_y))

        return actorMask

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
        pygame.draw.rect(gameDisplay, white, [mouse[0] - 2, mouse[1] - 11, 4, 8]) # all hairs are outlined in white so they can be seen even when the cursor is over a black object
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

    def viewMask(self, mouse, fov, distance):
        fov = m.radians(fov) # convert fov to radians

        # Mr. Marshall's code #

        dx = mouse[0] - (self.rect.x + (self.w / 2))
        dy = mouse[1] - (self.rect.y + (self.w / 2))
        mod_m = m.sqrt(dx**2 + dy**2)
        sf = distance/mod_m
        centre_x = sf*dx + (self.rect.x + (self.w / 2))
        centre_y = sf*dy + (self.rect.y + (self.w / 2))

        angle_sf = sf*m.tan(fov/2)

        perp_dx = dy
        perp_dy = -dx
        corner1_x = centre_x + angle_sf*perp_dx
        corner1_y = centre_y + angle_sf*perp_dy

        # End Mr. Marshall magic #

        xDiff = corner1_x - self.virtualx # work out difference from point to actor
        yDiff = self.virtualy - corner1_y
        angFromVert = 0.0 # initialise as float

        if yDiff != 0: # to prevent 0 division errors
            if corner1_y < self.rect.y: # magic?
                angFromVert = -1 * m.atan(xDiff / yDiff)
            else:
                angFromVert = -1 * m.atan(xDiff / yDiff) + m.pi # why adding pi solves everything is still unknown to this day
        elif xDiff > 0: # looking exactly right
            angFromVert = 0.5 * m.pi
        elif xDiff < 0: # looking exactly left
            angFromVert = 1.5 * m.pi

        arcRect = pygame.Rect(self.rect.x, self.rect.y, distance * 2, distance * 2)
        gameDisplay.fill(white)
        pygame.draw.arc(gameDisplay, black, arcRect, angFromVert, angFromVert + fov, round(distance))
        renderArea = pygame.mask.from_surface(gameDisplay) # now we have to find all the sprites we need to draw within this cone
        print("Render area count: " + str(renderArea.count()))

        return renderArea

    def selectToRender(self, playerViewMask, allSprites):

        visibleSprites = pygame.sprite.Group()

        for sprite in allSprites:
            spriteMask = pygame.mask.from_surface(sprite.image)
            #print("Sprite mask count: " + str(spriteMask.count()) + " overlaps " + str(spriteMask.overlap_area(playerViewMask, (0,0))) + " pixels.")

            if spriteMask.overlap_area(playerViewMask, (0,0)) > 0:
                visibleSprites.add(sprite)

        return visibleSprites

class Guard(Actor):
    """
    These are the bad guys
    """
    def __init__(self, x = 10, y = 10, w = 15, h = 15, patrolPoints = [Point(10,10)], speed = 1.2, colour = black):
        super().__init__(x, y, w, h, speed, colour)
        self.alive = True

        # Navigation related variables
        self.eightDirs = [0,0] # x, y. Positive right/down
        self.wantToGoHere = [False for _ in range(4)] # udlr
        self.wantToGoStack = []
        self.blocked = [False for _ in range(4)] # udlr
        self.tryThisDir = ''
        self.lastCoords = Point()
        self.problemSolvingDirection = rng.choice([-1,1])
        self.oldDest = Point()
        self.dirToTry = 0 # udlr indexes

        # Brain variables
        self.states = [False for _ in range(5)]
        self.lastSeenCorpses = [] # used as stack
        self.lastSeenPlayer = None
        self.lastSeenGuards = []
        self.patrolPoints = patrolPoints
        self.currentDest = self.patrolPoints[0]

        """
        Guard states (each number referring to an index in the array):
        0 - alerted to presence of player
        1 - alerted to presence of dead guards
        2 - with another guard
        3 - investigating around point
        4 - altRoute-ing

        If all states are False, the guard patrols as normal
        """

    def getShot(self):
        print("Guard hit. They didn't appreciate it.")
        self.alive = False
        return None

    def altRoute(self):
        for thisWay in range(4):
            if self.bannedDirs[thisWay] and self.wantToGoHere[thisWay] and self.block[thisWay] == False: # last clause to prevent repeat appending
                self.blocked[thisWay] = True # identify blocked routes
                self.wantToGoStack.append(thisWay)

        if self.states[4] == False: # if this is the first time altRoute() has been called, save the old destination
            self.oldDest = self.currentDest
            cancer = [0, 2, 1, 3] # please, just stop thinking about this (translates udlr format into uldr format -_-)
            self.dirToTry = (cancer[self.wantToGoStack[len(self.wantToGoStack) - 1]] + self.problemSolvingDirection) % 4
        else:
            self.dirToTry = (self.dirToTry + self.problemSolvingDirection) % 4

        if self.dirToTry == 0: # up
            self.currentDest = Point(self.rect.x, self.rect.y - self.speed * 2)
        elif self.dirToTry == 1: # left
            self.currentDest = Point(self.rect.x - self.speed * 2, self.rect.y)
        elif self.dirToTry == 2: # down
            self.currentDest = Point(self.rect.x, self.rect.y + self.speed * 2)
        elif self.dirToTry == 3: # right
            self.currentDest = Point(self.rect.x + self.speed * 2, self.rect.y)

    def goto(self, dest, sprGroup = None):
        """
        Stopping in close proximity (as opposed to on top of the target) only works if the 2 squares are the same width
        """

        self.eightDirs = [0,0]
        self.wantToGoHere = [False, False, False, False]

        # x co-ordinate #
        if abs(self.rect.x - dest.x) > self.w + self.speed:
            if dest.x < self.virtualx:
                self.wantToGoHere[2] = True
                if not self.bannedDirs[2]:
                    self.virtualx -= self.speed
                    self.eightDirs[1] = -1
            elif dest.x > self.virtualx:
                self.wantToGoHere[3] = True
                if not self.bannedDirs[3]:
                    self.virtualx += self.speed
                    self.eightDirs[1] = 1
        elif abs(self.virtualx - dest.x) <= self.w + self.speed and abs(self.virtualx - dest.x) >= self.w and sprGroup == None: # fine adjusment
            if dest.x < self.virtualx:
                self.wantToGoHere[2] = True # necessary?
                if not self.bannedDirs[2]:
                    self.virtualx -= 0.1
                    self.eightDirs[1] = -1
            elif dest.x > self.virtualx:
                self.wantToGoHere[3] = True # necessary?
                if not self.bannedDirs[3]:
                    self.virtualx += 0.1
                    self.eightDirs[1] = 1
        ###

        # y co-ordinate #
        # could change such that moving up/down is determined before the distance moved is
        if abs(self.rect.y - dest.y) > self.w + self.speed:
            if dest.y < self.virtualy:
                self.wantToGoHere[1] = True
                if not self.bannedDirs[0]:
                    self.virtualy -= self.speed
                    self.eightDirs[0] = 1
            elif dest.y > self.virtualy:
                self.wantToGoHere[0] = True
                if not self.bannedDirs[1]:
                    self.virtualy += self.speed
                    self.eightDirs[0] = -1
        elif abs(self.virtualy - dest.y) <= self.w + self.speed and abs(self.virtualy - dest.y) >= self.w and sprGroup == None: # fine adjustment
            if dest.y < self.virtualy:
                self.wantToGoHere[1] = True
                if not self.bannedDirs[0]:
                    self.virtualy -= 0.1
                    self.eightDirs[0] = 1
            elif dest.y > self.virtualy:
                self.wantToGoHere[0] = True
                if not self.bannedDirs[1]:
                    self.virtualy += 0.1
                    self.eightDirs[0] = -1
        ###

        self.rect.x = round(self.virtualx)
        self.rect.y = round(self.virtualy)
        if sprGroup:
            self.collisionCheck(sprGroup)

            if self.lastCoords.distance(Point(self.rect.x, self.rect.y)) == 0: # if guard hasn't moved since last time procedure was called
                self.altRoute()
                self.states[4] = True # must be left after the above to prevent the original destination being overwritten

    def patrol(self):
        if self.rect.x == self.currentDest.x and self.rect.y == self.currentDest.y:
            self.currentDest = self.patrolPoints[(self.patrolPoints.index(self.currentDest) + 1) % len(self.patrolPoints)] # sets destination to be next point in patrol points list

    def generatePatrol(self, focus, radius):
        # method creates a random 3 point patrol given a central point and radius
        # currently does not check to ensure the path is possible
        udlr = [rng.choice([-1,1]), rng.choice([-1,1])] # chooses -1 or 1 randomly
        self.patrolPoints[Point(focus.x + (radius * udlr[0]), focus.y + (radius * udlr[1])), focus, Point(focus.x - (radius * udlr[0]), focus.y - (radius * udlr[1]))]
        self.currentDest = focus

    def lookAround(self, actors):
        viewMask = self.drawCone((self.virtualx + (5 * self.eightDirs[1]), self.virtualy + (5 * self.eightDirs[0])), 90, 100)
        alreadySeenAGuard = False

        for actor in actors:
            if viewMask.overlap(pygame.mask.from_surface(actor.image), (0,0)):
                if type(actor) == type(Guard()) and actor != self:
                    if actor.alive:
                        if not alreadySeenAGuard:
                            self.lastSeenGuards = []
                            alreadySeenAGuard = True
                        self.lastSeenGuards.append(Point(actor.rect.x, actor.rect.y))
                    else:
                        self.lastSeenCorpses.append(Point(actor.rect.x, actor.rect.y))
                        self.states[1] = True
                elif type(actor) == type(Player()):
                    self.lastSeenPlayer = Point(actor.rect.x, actor.rect.y)
                    self.states[0] = True

    def quickLook(self, actor):
        viewMask = self.drawCone((self.virtualx + (5 * self.eightDirs[1]), self.virtualy + (5 * self.eightDirs[0])), 90, 100)
        return viewMask.overlap(pygame.mask.from_surface(actor.image), (0,0))

    def brain(self, player, allyGroup, actorGroup, envObjs):
        self.lastCoords = Point(self.rect.x, self.rect.y)
        self.lookAround(actorGroup)

        if self.states[4]: # navigating around an obstacle to get to destination
            if self.bannedDirs[self.bannedDirs.index(self.tryThisDir)]: # if I can't move
                self.blocked[directions.index(self.tryThisDir)] = True # ... the direction I just tried to move in must be blocked by something
                self.altRoute() # time to find out where to go again

        elif self.states[0]: # gotta go get the player! Grrrr
            self.currentDest = self.lastSeenPlayer

            if self.rect.x == self.lastSeenPlayer.x and self.rect.y == self.lastSeenPlayer.y and self.quickLook(player) == False: # lost the player
                self.states[0] = True # no longer aware of player
                self.states[3] = True # investigate around last known point

        elif self.states[1]: # omg one of my friends is dead
            self.currentDest = self.lastSeenCorpse.pop() # go to the last seen guard corpse

        else:
            self.patrol() # patrol as usual

        self.goto(self.currentDest)

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
        Providing an str means that if you just type an object is called, this is what is returned
        """
        return "Obstacle at ({x}, {y}), with a width of {w} and height of {h}".format(x = self.rect.x, y = self.rect.y, w = self.w, h = self.h)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is returned
        """
        return "Obstacle at ({x}, {y}), with a width of {w} and height of {h}".format(x = self.rect.x, y = self.rect.y, w = self.w, h = self.h)

    def getShot(self):
        if self.destructable: # wall breaks
            self.kill() # removes sprite
            print("Wall shot. Wall dead.")
            return None
        else:
            print("Wall shot. Wall smiles.")
            return None

class Projectile(pygame.sprite.Sprite):
    """
    The pew pew things
    """
    def __init__(self, x, y, mouse):
        super().__init__()
        self.xStep = mouse[0] - x # finds difference in co-ords
        self.yStep = mouse[1] - y

        # makes smaller difference to be 1, and scales the other value appropriately
        if self.xStep < self.yStep:
            self.yStep = self.yStep / abs(self.xStep)
            self.xStep = self.xStep / abs(self.xStep)
        else:
            self.xStep = self.xStep / abs(self.yStep)
            self.yStep = self.yStep / abs(self.yStep) # consider optimising this

        self.image = pygame.Surface([2, 2])
        self.image.fill(black) # bullets are 2x2
        self.rect = self.image.get_rect()

        self.rect.x = round(x) # set co-ords
        self.rect.y = round(y)
        self.virtualx = x
        self.virtualy = y

    def go(self, sprGroup):
        while len(pygame.sprite.spritecollide(self, sprGroup, False)) == 0: # while the bullet has yet to hit anything
            self.virtualx += self.xStep # move bullet in repeated small increments
            self.virtualy += self.yStep

            self.rect.x = round(self.virtualx)
            self.rect.y = round(self.virtualy)

            if self.rect.x > displayWidth or self.rect.x + 2 < 0 or self.rect.y > displayHeight or self.rect.y < 0: # if the bullet is out of bounds
                print("Giving up")
                self.kill()
                return None

        collidedWith = pygame.sprite.spritecollide(self, sprGroup, False) # list of all objects collided with from within the specified sprGroup
        self.kill() # remove the bullet
        print("Registered hit. Bullet removed.")
        for obj in collidedWith:
            obj.getShot() # registers hit for each object collided with in turn

        return collidedWith

def instance():
    running = True

    # Used to prevent player from leaving the screen
    gameBoundTop = Obstacle(0, -100, displayWidth, 100, False)
    gameBoundBottom = Obstacle(0, displayHeight, displayWidth, 100, False)
    gameBoundLeft = Obstacle(-100, 0, 100, displayHeight, False)
    gameBoundRight = Obstacle(displayWidth, 0, 100, displayHeight, False)

    player = Player()
    guard = Guard(500, 500, 15, 15, [Point(100,650), Point(1180, 650)], 1.2, dan)
    wall = Obstacle(200, 200, 300, 150, False)
    wall2 = Obstacle(700, 600, 200, 20, True)

    allSprites = pygame.sprite.Group() # used for drawing all visible sprites
    allSprites.add(guard)
    allSprites.add(wall)
    allSprites.add(wall2)

    actors = pygame.sprite.Group()
    actors.add(player)
    actors.add(guard)

    environmentSprites = pygame.sprite.Group() # used for collision checking
    environmentSprites.add(wall)
    environmentSprites.add(wall2)
    environmentSprites.add(gameBoundTop)
    environmentSprites.add(gameBoundBottom)
    environmentSprites.add(gameBoundLeft)
    environmentSprites.add(gameBoundRight)

    guards = pygame.sprite.Group()
    guards.add(guard)

    lonelyPlayer = pygame.sprite.Group() # used to draw the player (again)
    lonelyPlayer.add(player)

    shootables = pygame.sprite.Group() # objects that can be shot
    shootables.add(guard)
    shootables.add(wall)
    shootables.add(wall2)

    # hide mouse
    pygame.mouse.set_visible(False)

    # initialise done before anything is drawn to the screen
    playerView = pygame.mask.from_surface(gameDisplay)

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

            if event.type == pygame.MOUSEBUTTONDOWN: # shoot the gun
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
        mouseCoords = pygame.mouse.get_pos()
        playerView.clear()
        playerView.draw(player.viewMask(mouseCoords, 90, 100), (0,0))
        #print(playerView.count())

        gameDisplay.fill(white) # clean up old frames
        guard.goto(Point(player.virtualx, player.virtualy), environmentSprites)
        #allSprites.draw(gameDisplay) # draw all visible sprites
        renderThese = player.selectToRender(playerView, allSprites)
        print(renderThese)
        renderThese.draw(gameDisplay)

        player.drawCone(mouseCoords, 90, 100)
        player.drawCrosshair(mouseCoords)
        lonelyPlayer.draw(gameDisplay) # draw player so that they're over the top of the crosshair lines
        ###

        """
        collided = pygame.sprite.spritecollide(player, environmentSprites, False) # returns array of repr of objects collided with
        guardHit = pygame.sprite.collide_rect(player, guard) # returns boolean
        """

        pygame.display.update()
        clock.tick(framerate) # sets framerate to be 120

    pygame.quit()

instance()
