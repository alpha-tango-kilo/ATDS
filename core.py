import pygame
import pygame.gfxdraw # not always needed, but used in drawMask
import math as m
import random as rng

pygame.init()
pygame.font.init()

# Global variables #
directions = ['u','d','l','r']
displayWidth = 1280
displayHeight = 720
framerate = 120
# Textures #
guardAlive = pygame.image.load("./assets/Actor/Guard/alive.png")
guardDead = pygame.image.load("./assets/Actor/Guard/dead.png")
playerAlive = pygame.image.load("./assets/Actor/Player/alive.png")
# Colours #
black = (0,0,0)
grey = (105,105,105)
white = (255,255,255)
red = (255,0,0)
dan = (42,117,225)
lightgrey = (230,230,230)
#########

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
        """
        Returns the distance between itself and another given point.
        Type returned: float
        """
        return m.sqrt((self.x - point.x)**2 + (self.y - point.y)**2)

    def round(self):
        """
        Returns a Point of the rounded co-ordinates.
        Type returned: Point
        """
        return Point(round(self.x), round(self.y))

class Actor(pygame.sprite.Sprite, World_Object):
    def __init__(self, x = 10, y = 10, w = 15, h = 15, speed = 1, colour = black, magSize = 6, shortReload = 2000, longReload = 2500, bulletPen = False):
        super().__init__() # inits pygame.sprite.Sprite

        """
        Parameters provided allow for a better customisation of the player "model"
        """

        self.width = w
        self.height = h
        self.colour = colour
        self.speed = speed
        self.bannedDirs = [False for _ in range(4)] # used with collision detection to determine directions in which the actor can't move

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.colour) # creates a rectangular picture for the sprite using given parameters
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.rect.x = round(x) # accounts for float inputs
        self.rect.y = round(y)

        self.virtualx = x # allows for decimal movement
        self.virtualy = y
        self.cPos = Point(self.virtualx + self.width/2, self.virtualy + self.height/2)

        self.magSize = magSize # number of bullets in a full magazine
        self.currentMag = magSize # number of bullets left in magazine
        self.shortReload = shortReload # delay in milliseconds
        self.longReload = longReload # delay in milliseconds
        self.bulletPen = bulletPen # whether or not bullets carry on after hitting target

    def __str__(self):
        """
        Providing an str means that if you just type an object is called, this is what is returned.
        """
        return "Actor is at ({x},{y}), and is {w} x {h} pixels.".format(x = self.rect.x, y = self.rect.y, w = self.width, h = self.height)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is returned.
        """
        return "Actor is at ({x},{y}), and is {w} x {h} pixels.".format(x = self.rect.x, y = self.rect.y, w = self.width, h = self.height)

    def posUpdate(self):
        self.rect.x = round(self.virtualx) # update physical (pixel) co-ordinates
        self.rect.y = round(self.virtualy)
        self.cPos = Point(self.virtualx + self.width/2, self.virtualy + self.height/2)

    def simpleMove(self, direction, distance):
        if direction == 'u': # up
            self.virtualy -= distance
        elif direction == 'd': # down
            self.virtualy += distance
        elif direction == 'l': # left and right aren't separate in the if statement as only 1 direction will ever be given as a parameter to the function
            self.virtualx -= distance # left
        elif direction == 'r':
            self.virtualx += distance # right

        self.posUpdate()

    def collisionCheck(self, sprGroup):
        keep = [False for _ in range(4)] # used to preserve banned directions if a test says the actor can't move up but another test says the actor can move up
        tActor = Actor(self.virtualx, self.virtualy, self.width, self.height, self.speed) # create a clone of the actor being tested, with the same key characteristics (colour is not important as tActor will never be drawn to screen)
        for test in range(4): # iterates from 0 to 3
            tActor.virtualx = self.virtualx # resets all co-ordinates for each test
            tActor.virtualy = self.virtualy
            tActor.posUpdate()
            tActor.simpleMove(directions[test], self.speed) # uses movement function without collision checking
            if len(pygame.sprite.spritecollide(tActor, sprGroup, False)) > 0: # checks if an objects are collided with from sprGroup (typically environmentSprites)
                self.bannedDirs[test] = True # bans direction
                keep[test] = True # ensures that banned direction is not overwritten
            elif len(pygame.sprite.spritecollide(tActor, sprGroup, False)) == 0 and not keep[test]: # if there are no collisions and the direction has no already been banned in this test battery...
                self.bannedDirs[test] = False # ...allow movement in this direction

    def move(self, direction, sprGroup = None):
        if direction == 'u' and not self.bannedDirs[0]: # up
            self.virtualy -= self.speed
        elif direction == 'd' and not self.bannedDirs[1]: # down
            self.virtualy += self.speed
        elif direction == 'l' and not self.bannedDirs[2]: # left
            self.virtualx -= self.speed
        elif direction == 'r' and not self.bannedDirs[3]: # right
            self.virtualx += self.speed

        self.posUpdate()

        if sprGroup:
            self.collisionCheck(sprGroup) # must go after position update

    def shoot(self, target, sprGroup):
        if self.currentMag > 0:
            bullet = Projectile(self.cPos.x - 1, self.cPos.y - 1, target) # create a bullet, such that its centre is the actor's centre
            self.currentMag -= 1
            bullet.go(sprGroup) # fires bullet (dramatically)
        else:
            pass # empty magazine click sound?

    def reload(self): # assumes the delay/wait has already occurred
        self.currentMag = self.magSize

    def cone(self, mouse, fov, distance, returnMask = False):
        fov = m.radians(fov) # convert fov to radians

        # Mr. Marshall's code #

        dx = mouse.x - self.cPos.x
        dy = mouse.y - self.cPos.y
        mod_m = m.sqrt(dx**2 + dy**2)
        sf = distance/mod_m*2/3 # my lovely addition, multiplying by two thirds
        centre = Point(sf*dx + self.cPos.x, sf*dy + self.cPos.y)

        angle_sf = sf*m.tan(fov/2)

        perp_dx = dy
        perp_dy = -dx
        corner1 = Point(centre.x + angle_sf*perp_dx, centre.y + angle_sf*perp_dy)
        corner2 = Point(centre.x - angle_sf*perp_dx, centre.y - angle_sf*perp_dy)

        # End Mr. Marshall magic #

        xDiff = corner1.x - self.virtualx # work out difference from point to actor
        yDiff = self.virtualy - corner1.y
        angFromVert = 0.0 # initialise as float

        if yDiff != 0: # to prevent 0 division errors
            if corner1.y < self.rect.y: # I don't know, it just works
                angFromVert = -1 * m.atan(xDiff / yDiff)
            else:
                angFromVert = -1 * m.atan(xDiff / yDiff) + m.pi
        elif xDiff > 0: # looking exactly right
            angFromVert = 0.5 * m.pi
        elif xDiff < 0: # looking exactly left
            angFromVert = 1.5 * m.pi

        arcRect = pygame.Rect(round(self.cPos.x - distance), round(self.cPos.y - distance), distance * 2, distance * 2) # creates a square such that the player is at the center and the side length is the arc's diameter
        #pygame.draw.rect(gameDisplay, black, arcRect, 2) # draws arcRect

        pygame.draw.arc(gameDisplay, black, arcRect, angFromVert, angFromVert + fov, 1) # why is this not filled in properly
        pygame.draw.aaline(gameDisplay, black, (self.cPos.x, self.cPos.y), (corner1.x, corner1.y))
        pygame.draw.aaline(gameDisplay, black, (self.cPos.x, self.cPos.y), (corner2.x, corner2.y))

        if returnMask:
            #fov = m.degrees(fov)
            #angFromVert = m.degrees(angFromVert)
            virtualDisplay = pygame.Surface((displayWidth, displayHeight))
            virtualDisplay.set_colorkey(white)
            #temp = self.cPos.round()
            pygame.draw.arc(virtualDisplay, black, arcRect, angFromVert, angFromVert + fov, round(distance))
            #pygame.gfxdraw.pie(gameDisplay, temp.x, temp.y, distance, angFromVert, angFromVert + fov, black) # both coords and angles have to be ints. I think angles might even work in degrees *sigh*
            viewArea = pygame.mask.from_surface(virtualDisplay) # now we have to find all the sprites we need to draw within this cone
            #print("Render area count: " + str(renderArea.count()))
            return viewArea

class Player(Actor):
    """
    This is the player's actor
    """
    def __init__(self, x = 10, y = 10, w = 15, h = 15, colour = red):
        super().__init__(x, y, w, h, 1, colour)

    def drawCrosshair(self, mouse):
        # line to player
        pygame.draw.aaline(gameDisplay, black, (mouse.x, mouse.y), (self.cPos.x, self.cPos.y), 2)
        # top hair
        pygame.draw.rect(gameDisplay, white, [mouse.x - 2, mouse.y - 11, 4, 8]) # all hairs are outlined in white so they can be seen even when the cursor is over a black object
        pygame.draw.rect(gameDisplay, black, [mouse.x - 1, mouse.y - 10, 2, 6])
        # bottom hair
        pygame.draw.rect(gameDisplay, white, [mouse.x - 2, mouse.y + 3, 4, 8])
        pygame.draw.rect(gameDisplay, black, [mouse.x - 1, mouse.y + 4, 2, 6])
        # left hair
        pygame.draw.rect(gameDisplay, white, [mouse.x - 11, mouse.y - 2, 8, 4])
        pygame.draw.rect(gameDisplay, black, [mouse.x - 10, mouse.y - 1, 6, 2])
        # right hair
        pygame.draw.rect(gameDisplay, white, [mouse.x + 3, mouse.y - 2, 8, 4])
        pygame.draw.rect(gameDisplay, black, [mouse.x + 4, mouse.y - 1, 6, 2])

    def selectToRender(self, playerViewMask, allSprites):

        tempGroup = pygame.sprite.GroupSingle()
        visibleSprites = pygame.sprite.Group()

        virtualDisplay = pygame.Surface((displayWidth, displayHeight))
        virtualDisplay.set_colorkey(white)

        for spr in allSprites:
            try:
                if spr.mask.overlap_area(playerViewMask, (0,0)) > 0: # tries to use sprites own premade mask, if it has one
                    visibleSprites.add(spr)
                    #print("Mask from memory")
                #print("Used sprite mask from memory")

            except AttributeError: # if the object doesn't have the attribute mask
                #print("Creating mask...")
                virtualDisplay.fill(white)

                tempGroup.add(spr)
                tempGroup.draw(virtualDisplay)
                spriteMask = pygame.mask.from_surface(virtualDisplay)

                if spriteMask.overlap_area(playerViewMask, (0,0)) > 0:
                    #print(str(spr) + " overlaps the player view mask")
                    visibleSprites.add(spr)

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
        self.wantToGoStack = [] # stack of direction indexes
        self.blocked = [False for _ in range(4)] # udlr
        self.tryThisDir = ''
        self.lastCoords = Point()
        self.problemSolvingDirection = rng.choice([-1,1])
        self.oldDest = Point()
        self.dirToTry = 0 # udlr indexes

        # Brain variables
        self.states = [False for _ in range(5)]
        self.lastSeenCorpse = Point()
        self.lastSeenPlayer = None
        self.lastSeenGuards = []
        self.patrolPoints = patrolPoints
        self.currentDest = self.patrolPoints[0]

        """
        Guard states (each number referring to an index in the array):
        0 - alerted to presence of player
        1 - alerted to presence of dead guards
        2 - with another guard
        3 - investigating a point
        4 - altRoute-ing

        If all states are False, the guard patrols as normal
        """

    def getShot(self):
        print("Guard hit. They didn't appreciate it.")
        self.alive = False
        return None

    def altRoute(self):
        if self.states[4] == False: # if this is the first time altRoute() has been called, save the old destination
            for thisWay in range(4):
                if self.bannedDirs[thisWay] and self.wantToGoHere[thisWay] and self.block[thisWay] == False: # last clause to prevent repeat appending
                    self.blocked[thisWay] = True # identify blocked routes
                    self.wantToGoStack.append(thisWay)

            self.oldDest = self.currentDest
            #cancer = [0, 2, 1, 3] # please, just stop thinking about this (translates udlr format into uldr format -_-)
            self.dirToTry = ([0, 2, 1, 3][self.wantToGoStack[len(self.wantToGoStack) - 1]] + self.problemSolvingDirection) % 4
        elif self.bannedDirs[self.wantToGoStack[len(self.wantToGoStack) - 1]]: # if the way I'm currently trying to go is blocked
            self.dirToTry = (self.dirToTry + self.problemSolvingDirection) % 4
        else: # if the latest direction I've been trying is now free
            self.dirToTry = self.wantToGoStack.pop()
            if len(self.wantToGoStack) == 0: # if the original direction I wanted to go is free and I've finished navigating around all obstacles
                self.states[4] = False # alt routing is no longer needed
                self.currentDest = self.oldDest
                return # return early to prevent the below if statements from changing the destination

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
        if abs(self.rect.x - dest.x) > self.width + self.speed:
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
        elif abs(self.virtualx - dest.x) <= self.width + self.speed and abs(self.virtualx - dest.x) >= self.width and sprGroup == None: # fine adjusment
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
        if abs(self.rect.y - dest.y) > self.width + self.speed:
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
        elif abs(self.virtualy - dest.y) <= self.width + self.speed and abs(self.virtualy - dest.y) >= self.width and sprGroup == None: # fine adjustment
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

        self.posUpdate()

        if sprGroup:
            self.collisionCheck(sprGroup)

            if self.lastCoords.distance(Point(self.rect.x, self.rect.y)) == 0: # if guard hasn't moved since last time procedure was called
                self.altRoute()
                self.states[4] = True # must be left after the above to prevent the original destination being overwritten

    def patrol(self):
        if self.rect.x == self.currentDest.x and self.rect.y == self.currentDest.y:
            self.currentDest = self.patrolPoints[(self.patrolPoints.index(self.currentDest) + 1) % len(self.patrolPoints)] # sets destination to be next point in patrol points list
        elif self.currentDest not in self.patrolPoints: # if not currently heading towards a patrol point
            self.currentDest = self.patrolPoints[rng.randint(0, len(self.patrolPoints) - 1)] # ... pick a random one and start heading there

    def generatePatrol(self, focus, radius):
        # method creates a random 3 point patrol given a central point and radius
        # currently does not check to ensure the path is possible
        focus = focus.round()
        udlr = [rng.choice([-1,1]), rng.choice([-1,1])] # chooses -1 or 1 randomly
        self.patrolPoints = [Point(focus.x + (radius * udlr[0]), focus.y + (radius * udlr[1])), focus, Point(focus.x - (radius * udlr[0]), focus.y - (radius * udlr[1]))]

    def lookAround(self, viewMask, actors):
        alreadySeenAGuard = False

        for actor in actors:
            if viewMask.overlap(pygame.mask.from_surface(actor.image), (0,0)):
                if type(actor) == type(Guard()) and actor != self: # don't know if the second part of this clause will work
                    if actor.alive: # if the guard is alive
                        if not alreadySeenAGuard: # if it's the first guard I've seen
                            self.lastSeenGuards = [] # ... jettison all other previously know guard locations, to avoid duplicates
                            alreadySeenAGuard = True
                        self.lastSeenGuards.append(Point(actor.cPos.x, actor.cPos.y))
                    elif Point(actor.rect.x, actor.rect.y) not in self.patrolPoints and self.states[1] == False: # if the corpse isn't one I'm patrolling around already, and I'm not already taking a shuftie at another corpse already
                        self.lastSeenCorpse = Point(actor.rect.x, actor.rect.y)
                        self.states[1] = True
                elif type(actor) == type(Player()):
                    self.lastSeenPlayer = Point(actor.rect.x, actor.rect.y)
                    self.states[0] = True

    def quickLook(self, viewMask, actor):
        return viewMask.overlap(pygame.mask.from_surface(actor.image), (0,0))

    def brain(self, player, allyGroup, actorGroup, devMode = False):

        self.lastCoords = Point(self.rect.x, self.rect.y)

        #viewMask = self.cone(Point(self.cPos.x + (5 * self.eightDirs[1]), self.cPos.y + (5 * self.eightDirs[0])), 90, 100, True) # could use currentDest instead for more accurate view?
        viewMask = self.cone(self.currentDest, 90, 100, True)
        self.lookAround(viewMask, actorGroup)

        if pygame.sprite.collide_rect(player, self): # if guard is touching the player
            print("Game Over!")

        if self.states[4]: # navigating around an obstacle to get to destination
            if self.bannedDirs[self.bannedDirs.index(self.tryThisDir)]: # if I can't move
                self.blocked[directions.index(self.tryThisDir)] = True # ... the direction I just tried to move in must be blocked by something
            self.altRoute() # I think this needs to be called every time, not within the above if statement
            if devMode:
                drawText("Alt-routing", (self.rect.x + 10, self.rect.y + 10))

        elif self.states[0]: # gotta go get the player! Grrrr
            self.currentDest = self.lastSeenPlayer

            if self.rect.x == self.lastSeenPlayer.x and self.rect.y == self.lastSeenPlayer.y and self.quickLook(viewMask, player) == False: # lost the player
                self.states[0] = True # no longer aware of player
                self.states[3] = True # investigate around last known point
                self.generatePatrol(self.currentDest, rng.randint(100,300)) # generate a new patrol centering on the player's last known location
                if devMode:
                    drawText("Searching for player", (self.rect.x + 10, self.rect.y + 20))
            elif devMode:
                drawText("Chasing player", (self.rect.x + 10, self.rect.y + 20))

        elif self.states[1]: # upon seeing a guard's corpse
            self.currentDest = self.lastSeenCorpse # go to the last seen corpse

            if abs(self.cPos.x - self.currentDest.x) <= self.width and abs(self.cPos.y - self.currentDest.y) <= self.height: # if within a body length of the corpse
                self.states[3] = True # investigating around a point
                self.generatePatrol(self.currentDest, rng.randint(100,300)) # generate a new patrol centering on the corpse

        if self.states[3]: # if investigating a point, assuming self.currentDest is the thing we're interested in
            pass

        elif not self.states[0] and not self.states[1] and not self.states[4]: # if I'm not doing anything that would mean I wouldn't be following my patrol
            self.patrol() # patrol as usual

        if not self.states[3]: # if I'm not standing around for investigatory purposes
            self.goto(self.currentDest) # ... I suppose I ought to walk around

class Obstacle(pygame.sprite.Sprite, World_Object):
    """
    Those things we love to hit our heads against
    """
    def __init__(self, x = 0, y = 0, w = 250, h = 250, destructable = False):
        """
        Define the shape and destructability of the wall
        """
        super().__init__()

        self.width = w
        self.height = h
        self.destructable = destructable

        # Obstacle will be grey if you can break it
        if self.destructable:
            self.colour = grey
        else:
            self.colour = black

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cPos = Point(self.rect.x + self.width/2, self.rect.y + self.height/2)

        virtualDisplay = pygame.Surface((displayWidth, displayHeight))
        virtualDisplay.set_colorkey(white)
        virtualDisplay.fill(white)
        tempGroup = pygame.sprite.Group()
        tempGroup.add(self)
        tempGroup.draw(virtualDisplay)
        self.mask = pygame.mask.from_surface(virtualDisplay) # pre calculating masks on game load saves having to calculate them every frame

    def __str__(self):
        """
        Providing an str means that if you just type an object is called, this is what is returned
        """
        return "Obstacle at ({x}, {y}), with a width of {w} and height of {h}".format(x = self.rect.x, y = self.rect.y, w = self.width, h = self.height)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is returned
        """
        return "Obstacle at ({x}, {y}), with a width of {w} and height of {h}".format(x = self.rect.x, y = self.rect.y, w = self.width, h = self.height)

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
        self.xStep = mouse.x - x # finds difference in co-ords
        self.yStep = mouse.y - y

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

    def go(self, sprGroup, bulletPen = False):
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

        print("Registered hit.")

        for obj in collidedWith:
            obj.getShot() # registers hit for each object collided with in turn

        if not bulletPen or type(collidedWith[0]) == type(Obstacle()): # if there is no bullet penetration or the bullet hit a wall
            self.kill() # remove the bullet
        else:
            sprGroup.remove(collidedWith[0]) # remove the sprite just hit from the group, so it won't be hit again
            self.go(sprGroup, bulletPen) # recurse the function to allow bullet to continue travelling

def drawText(text, colour = (0,0,0), font = "Comic Sans MS", fontSize = 14):
    theFont = pygame.font.SysFont(font, fontSize)
    return theFont.render(str(text), True, colour)

def drawMask(mask, colour = (0,0,0)): # alternative name is destroyFPS()
    for i in range(displayWidth):
        for j in range(displayHeight):
            if mask.get_at((i, j)) != 0:
                pygame.gfxdraw.pixel(gameDisplay, i, j, colour)

def instance():
    running = True
    devMode = True

    RELOAD = pygame.USEREVENT + 1

    # Used to prevent player from leaving the screen
    gameBoundTop = Obstacle(0, -100, displayWidth, 100, False)
    gameBoundBottom = Obstacle(0, displayHeight, displayWidth, 100, False)
    gameBoundLeft = Obstacle(-100, 0, 100, displayHeight, False)
    gameBoundRight = Obstacle(displayWidth, 0, 100, displayHeight, False)

    player = Player()
    guard1 = Guard(500, 500, 15, 15, [Point(100,650), Point(1180, 650)], 1.2, dan)
    wall = Obstacle(200, 200, 300, 150, False)
    wall2 = Obstacle(700, 600, 200, 20, True)

    allSprites = pygame.sprite.Group() # used for drawing all visible sprites
    allSprites.add(guard1)
    allSprites.add(wall)
    allSprites.add(wall2)

    actors = pygame.sprite.Group()
    actors.add(player)
    actors.add(guard1)

    environmentSprites = pygame.sprite.Group() # add any sprites you don't want to walk through
    environmentSprites.add(wall)
    environmentSprites.add(wall2)
    environmentSprites.add(gameBoundTop)
    environmentSprites.add(gameBoundBottom)
    environmentSprites.add(gameBoundLeft)
    environmentSprites.add(gameBoundRight)

    guards = pygame.sprite.Group() # used to call their bot routines
    guards.add(guard1)

    lonelyPlayer = pygame.sprite.GroupSingle() # used to draw the player (again)
    lonelyPlayer.add(player)

    # hide mouse
    pygame.mouse.set_visible(False)

    # initialise done before anything is drawn to the screen
    playerView = pygame.mask.from_surface(gameDisplay)

    while running:
        mouse = pygame.mouse.get_pos()
        mouse = Point(mouse[0], mouse[1])

        for event in pygame.event.get():
            # Any pygame handled events should be put here #
            # Quit the game
            if event.type == pygame.QUIT:
                running = False

            # Key pressed (triggers once, even if held) #
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE: # close game if escape is pressed
                    running = False

                if event.key == pygame.K_r: # press R to reload
                    if player.currentMag < player.magSize:
                        if player.currentMag >= 1: # short reload
                            pygame.time.set_timer(RELOAD, player.shortReload) # start the reload
                            player.currentMag = 1 # immersion science
                        else: # long reload
                            pygame.time.set_timer(RELOAD, player.longReload) # start the reload

                if event.key == pygame.K_RIGHTBRACKET:
                    devMode = not devMode # python is magical sometimes

            if event.type == pygame.MOUSEBUTTONDOWN: # shoot the gun
                player.shoot(mouse, allSprites)
                pygame.time.set_timer(RELOAD, 0) # cancels a reload upon shooting

            if event.type == RELOAD:
                pygame.time.set_timer(RELOAD, 0) # prevents re-reloading chain (just pygame things)
                player.reload()
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

        # Rendering functions #
        playerView.clear()
        playerView.draw(player.cone(mouse, 90, 100, True), (0,0)) # this will whiteout the screen and put an arc on it, always clear screen after
        visibleSprites = player.selectToRender(playerView, allSprites) # decide what needs rendering

        #print(visibleSprites)

        gameDisplay.fill(white) # clean up arc drawings
        #print(playerView.count())

        #playerView.invert()
        #drawMask(playerView, lightgrey) # can be used to draw mask if needed, makes frame time go up to ~500

        # Continuous Functions #
        for guard in guards: # this is where the brain will be called from
            if guard.alive: # prevents the guard from moving if they're dead - quite useful
                #guard.goto(Point(player.virtualx, player.virtualy), environmentSprites) # brain will be called here
                guard.brain(player, guards, actors)
        ###

        # Text draws #
        gameDisplay.blit(drawText("{pewsLeft} / {pews}".format(pewsLeft = player.currentMag, pews = player.magSize)), (mouse.x + 10, mouse.y + 10)) # remaining bullets in mag are slapped just below the mouse
        gameDisplay.blit(drawText("FPS: {fps}".format(fps = round(clock.get_fps()))), (2,0)) # fps counter
        gameDisplay.blit(drawText("Frame Time: {ft}".format(ft = clock.get_rawtime())), (2,18)) # frame time
        ###

        if not devMode:
            visibleSprites.draw(gameDisplay)
        else:
            allSprites.draw(gameDisplay)

        player.cone(mouse, 90, 200)
        player.drawCrosshair(mouse)
        lonelyPlayer.draw(gameDisplay) # draw player so that they're over the top of the crosshair lines
        ###

        """
        collided = pygame.sprite.spritecollide(player, environmentSprites, False) # returns array of objects collided with
        guardHit = pygame.sprite.collide_rect(player, guard) # returns boolean
        """

        pygame.display.update()
        clock.tick(framerate) # manages fps game is displayed at

    pygame.quit()

if __name__ == "__main__":
    instance()
