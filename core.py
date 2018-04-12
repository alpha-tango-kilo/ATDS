import pygame
import pygame.gfxdraw # not always needed, but used in drawMask
import math as m
import random as rng
from sys import exit

pygame.init()
pygame.font.init()

# Global variables #
directions = ['u','l','d','r']
displayWidth = 1280
displayHeight = 720
framerate = 60
RELOAD          = pygame.USEREVENT + 1
CHECKWIN        = pygame.USEREVENT + 2
GUARDTHINK      = pygame.USEREVENT + 3
EMERGENCYSTOP   = pygame.USEREVENT + 4
virtualDisplay = pygame.Surface((displayWidth, displayHeight)) # always left dirty for the next process to clean it before use
virtualDisplay.set_colorkey((255,255,255))
# Textures #
guardAlive = pygame.image.load("./assets/Actor/Guard/alive.png")
guardDead = pygame.image.load("./assets/Actor/Guard/dead.png")
playerAlive = pygame.image.load("./assets/Actor/Player/alive.png")
# Colours #
black = (0,0,0)
grey = (105,105,105)
lightgrey = (230,230,230)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
dan = (42,117,225)
#########

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight), pygame.NOFRAME)
pygame.display.set_caption("ATDS")

clock = pygame.time.Clock()

class Level(): # I'd like to think this is pretty self explanatory
    def __init__(self): # create necessary variables ONLY, don't actually create the level, as we don't know where we're creating it from
        self.ID = 1
        self.running = False

        self.player = None
        self.guards = []
        self.obstacles = [Obstacle(0, -100, displayWidth, 100, False), Obstacle(0, displayHeight, displayWidth, 100, False), Obstacle(-100, 0, 100, displayHeight, False), Obstacle(displayWidth, 0, 100, displayHeight, False)]
        self.objective = None

        # all sprite groups can be created here!
        self.playerGroup        = pygame.sprite.GroupSingle()
        self.guardGroup         = pygame.sprite.Group()
        self.actorGroup         = pygame.sprite.Group() # any actors, player included
        self.environmentGroup   = pygame.sprite.Group() # anything you don't want to walk through
        self.allGroup           = pygame.sprite.Group() # everything except player
        self.visibleGroup       = pygame.sprite.Group()
        self.objectiveGroup     = pygame.sprite.GroupSingle() # where the objective is kept in its spare time

        for obstacle in self.obstacles: # could use self.updateGroups?
            self.environmentGroup.add(obstacle)
            self.allGroup.add(obstacle)

    def loadFromFile(self): # look examiner! file storage!
        """
        Returns True on successful load, False if file is not found
        File format is intended to work as follows, all parameters must be given and will be separated by a space/tab (depending on which I feel like, hopefully I'll update this comment):
        line 1 - player parameters (x, y)
        line 2 - guard parameters (x, y, patrolPoints, speed), all guards will be on this single line. Guard patrol points are sewn together by dashes (-), so they aren't separated until we're ready for that sweet O(n^2) processing
        line 3 - obstacle parameters (x, y, width, height, destructable), relying on the same basis as above
        line 4 - objective parameters (x, y, width, height)
        """
        self.clear()
        print("Loading level...\n\n")
        try:
            raw = open("./levels/{no}.level".format(no = str(self.ID)), "r").read().splitlines() # open the file as read only. Using read() and then splitlines() avoids Python putting \n at the end of the strings in the array, which occurs when using readlines() time complexity of level creation is not an issue, having things read as I want is more important. consider regexing?

        except FileNotFoundError: # If the level doesn't exist
            print("Level file (ID: {n}) not found, aborting.\n".format(n = self.ID))
            self.running = False
            pygame.quit()
            exit()
            return

        print("Level file read (ID: {n})\n".format(n = self.ID))

        for lineNo in range(len(raw)):
            raw[lineNo] = raw[lineNo].split(" ") # could use tabs instead for readability, this may change but is essentially unimportant
            # at this point raw should be a 2D list of lists, just how I like them

        self.player = Player(float(raw[0][0]), float(raw[0][1])) # create player
        print("Loaded player\n")

        for guardNo in range(0, len(raw[1]), 4): # loops for the number of guards
            rawPatrol = raw[1][guardNo + 2].split("-") # see docstring
            patrolPoints = [] # initialise variable
            for pointNo in range(0, len(rawPatrol), 2): # loops for the number of patrol points
                patrolPoints.append(Point(int(rawPatrol[pointNo]), int(rawPatrol[pointNo + 1]))) # adds each patrol point to the list, ensuring everything is an int first
            self.guards.append(Guard(int(raw[1][guardNo]), int(raw[1][guardNo + 1]), patrolPoints, float(raw[1][guardNo + 3]))) # creates guards, adding them to the list
            print("Loaded guard")
        print("Finished loading guards:\t{n} in total\n".format(n = str(int(len(raw[1]) / 4))))

        for obstacleNo in range(0, len(raw[2]), 5): # loops for the number of obstacles
            self.obstacles.append(Obstacle(int(raw[2][obstacleNo]), int(raw[2][obstacleNo + 1]), int(raw[2][obstacleNo + 2]), int(raw[2][obstacleNo + 3]), (raw[2][obstacleNo + 4] == "True"))) # creates obstacle objects, adding them to the list
            print("Loaded obstacle")
        print("Finished loading obstacles:\t{n} in total\n".format(n = str(int(len(raw[2]) / 5))))

        try:
            self.objective = Objective(int(raw[3][0]), int(raw[3][1]), int(raw[3][2]), int(raw[3][3]))
            print("Loaded objective\n")
        except IndexError: # objective isn't in the list
            print("No objective in level, skipping\n")

        print("Updating groups...\n")
        self.updateGroups()
        print("Groups updated\n\nLevel loaded")

        self.running = True

    def updateGroups(self):
        # empty all sprite groups first (playerGroup doesn't have to be done as it's a GroupSingle)
        self.guardGroup.empty()
        self.actorGroup.empty()
        self.environmentGroup.empty()
        self.allGroup.empty()
        self.visibleGroup.empty()
        self.objectiveGroup.empty()

        # start re-adding everything
        self.playerGroup.add(self.player)
        self.actorGroup.add(self.player)

        for guard in self.guards:
            self.guardGroup.add(guard)
            self.actorGroup.add(guard)
            self.allGroup.add(guard)

        for obstacleIndex in range(len(self.obstacles)): # runs for every wall, excluding the game bounds as they're already added
            self.environmentGroup.add(self.obstacles[obstacleIndex])
            self.allGroup.add(self.obstacles[obstacleIndex])

        if self.objective:
            self.allGroup.add(self.objective)
            self.objectiveGroup.add(self.objective)

    def checkWin(self, devMode = False):
        """
        The level has been won if the player reaches the objective or no guards remain standing, whichever happens first
        """

        wonByObjective = False

        try:
            wonByObjective = pygame.sprite.collide_rect(self.player, self.objective)
        except AttributeError: # if there is no objective
            pass

        if not wonByObjective: # no point in checking this if the game already has been won
            for guard in self.guards:
                if guard.alive:
                    return False

        print("Winner! Winner! Chicken dinner!\n")

        gameDisplay.fill(white)
        drawText("Winner! Winner! Chicken dinner!", (100,100), dan, "Comic Sans MS", 54)
        pygame.display.update()

        if not devMode:
            pygame.time.delay(10000)
        else:
            pygame.time.delay(2000)

        self.ID += 1
        self.loadFromFile()

        return True

    def printLevel(self): # see what's in the level, so it can be debugged (I wonder why I wrote this)
        print("~~ PRINT START ~~\n")
        print(self.player)
        print("\nGuards ({n1} in array, {n2} in guardGroup):".format(n1 = len(self.guards), n2 = len(self.guardGroup)))
        for guard in self.guards:
            print("\tSpawned at:\t({x},{y})".format(x = guard.rect.x, y = guard.rect.y))
            print("\tPatrol points:\t{pts}".format(pts = guard.patrolPoints))
            print("\tSpeed:\t{spd}\n".format(spd = guard.speed))
        print("Obstacles ({n1} in array, {n2} in environmentGroup):".format(n1 = len(self.obstacles), n2 = len(self.environmentGroup)))
        for obstacle in self.obstacles:
            print("\tPlaced at:\t({x},{y})".format(x = obstacle.rect.x, y = obstacle.rect.y))
            print("\tWidth:\t{w}\tHeight:\t{h}".format(w = obstacle.width, h = obstacle.height))
            print("\tDestructable:\t{yorn}\n".format(yorn = obstacle.destructable))
        print("Sprite groups:")
        print("\tguardGroup:\t\t{n}".format(n = len(self.guardGroup)))
        print("\tactorGroup:\t\t{n}".format(n = len(self.actorGroup)))
        print("\tenvironmentGroup:\t{n}".format(n = len(self.environmentGroup)))
        print("\tallGroup:\t\t{n}".format(n = len(self.allGroup)))
        print("\tvisibleGroup:\t\t{n}\n".format(n = len(self.visibleGroup)))
        print("~~ PRINT COMPLETE ~~")

    def clear(self):
        self.player = None
        self.guards = []
        self.obstacles = [Obstacle(0, -100, displayWidth, 100, False), Obstacle(0, displayHeight, displayWidth, 100, False), Obstacle(-100, 0, 100, displayHeight, False), Obstacle(displayWidth, 0, 100, displayHeight, False)]

        self.playerGroup.empty()
        self.guardGroup.empty()
        self.actorGroup.empty()
        self.environmentGroup.empty()
        self.allGroup.empty()
        self.visibleGroup.empty()
        self.objectiveGroup.empty()

        for obstacle in self.obstacles:
            self.environmentGroup.add(obstacle)
            self.allGroup.add(obstacle)

class World_Object(): # any object that is visible to and interactive with the player should inherit from this class, as an insurance policy
    def getShot(self): # a default case for any object rendered to the screen being shot, needed otherwise projectiles will error
        print("World_Object says 'ow!'")

class Point():
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return "({x}, {y})".format(x = self.x, y = self.y)

    def __repr__(self):
        return "({x}, {y})".format(x = self.x, y = self.y)

    def distance(self, point):
        """
        Returns the distance between itself and another given point.
        Type returned: float
        """
        return m.sqrt((self.x - point.x)**2 + (self.y - point.y)**2)

    def round(self):
        """
        Returns a Point of the rounded co-ordinates of the Point calling the method.
        Type returned: Point
        """
        return Point(round(self.x), round(self.y))

class Actor(pygame.sprite.Sprite, World_Object):
    def __init__(self, x = 10, y = 10, speed = 1, magSize = 6, shortReload = 2000, longReload = 2500, bulletPen = False):
        super().__init__() # inits pygame.sprite.Sprite

        """
        Parameters provided allow for a better customisation of the player "model"
        """

        self.width = 15
        self.speed = speed
        self.bannedDirs = [False for _ in range(4)] # used with collision detection to determine directions in which the actor can't move ULDR

        self.image = pygame.Surface([self.width, self.width], pygame.SRCALPHA, 32)
        self.image.fill((0,0,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = round(x) # accounts for float inputs
        self.rect.y = round(y)

        self.virtualx = x # allows for decimal movement
        self.virtualy = y
        self.cPos = Point(self.virtualx + self.width/2, self.virtualy + self.width/2) # uses floats

        self.magSize = magSize # number of bullets in a full magazine
        self.currentMag = magSize # number of bullets left in magazine
        self.shortReload = shortReload # delay in milliseconds
        self.longReload = longReload # delay in milliseconds
        self.bulletPen = bulletPen # whether or not bullets carry on after hitting target

    def __str__(self):
        """
        Providing an str means that if you just type an object is called, this is what is returned.
        """
        return "Actor is at ({x},{y}), and is {w} x {w} pixels.".format(x = self.rect.x, y = self.rect.y, w = self.width)

    def __repr__(self):
        """
        Providing an str means that if you just type an object is called, this is what is returned.
        """
        return "Actor is at ({x},{y}), and is {w} x {w} pixels.".format(x = self.rect.x, y = self.rect.y, w = self.width)

    def posUpdate(self):
        self.rect.x = round(self.virtualx) # update physical (pixel) co-ordinates
        self.rect.y = round(self.virtualy)
        self.cPos = Point(self.virtualx + self.width/2, self.virtualy + self.width/2)

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
        tActor = Actor(self.virtualx, self.virtualy, self.speed) # create a clone of the actor being tested, with the same key characteristics
        for test in range(4): # iterates from 0 to 3
            tActor.virtualx = self.virtualx # resets all co-ordinates to the sprite running it for each test
            tActor.virtualy = self.virtualy
            tActor.posUpdate()
            tActor.simpleMove(directions[test], self.speed) # uses movement function without collision checking
            self.bannedDirs[test] = len(pygame.sprite.spritecollide(tActor, sprGroup, False)) > 0 # bans direction if there are collisions, otherwise it unbans the direction

    def move(self, direction, sprGroup = None):
        if direction == 'u' and not self.bannedDirs[0]: # up
            self.virtualy -= self.speed
        elif direction == 'd' and not self.bannedDirs[2]: # down
            self.virtualy += self.speed
        elif direction == 'l' and not self.bannedDirs[1]: # left
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

    def cone(self, mouse, fov, distance, drawCone = False, returnMask = False):
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

        xDiff = corner1.x - self.cPos.x # work out difference from point to actor
        yDiff = self.cPos.y - corner1.y
        angFromVert = 0.0 # initialise as float

        if yDiff != 0: # to prevent 0 division errors
            if corner1.y < self.cPos.y: # I don't know, it just works
                angFromVert = -1 * m.atan(xDiff / yDiff)
            else:
                angFromVert = -1 * m.atan(xDiff / yDiff) + m.pi
        elif xDiff > 0: # looking exactly right
            angFromVert = 0.5 * m.pi
        elif xDiff < 0: # looking exactly left
            angFromVert = 1.5 * m.pi

        arcRect = pygame.Rect(round(self.cPos.x - distance), round(self.cPos.y - distance), distance * 2, distance * 2) # creates a square such that the player is at the center and the side length is the arc's diameter

        if drawCone:
            pygame.draw.arc(gameDisplay, black, arcRect, angFromVert, angFromVert + fov, 1)
            pygame.draw.aaline(gameDisplay, black, (self.cPos.x, self.cPos.y), (corner1.x, corner1.y))
            pygame.draw.aaline(gameDisplay, black, (self.cPos.x, self.cPos.y), (corner2.x, corner2.y))

        if returnMask:
            #fov = m.degrees(fov)
            #angFromVert = m.degrees(angFromVert)
            virtualDisplay.fill(white)
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
    def __init__(self, x = 10, y = 10):
        super().__init__(x, y, 1)
        self.image.blit(playerAlive, (0,0))
        self.image = self.image.convert_alpha()

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

        for spr in allSprites:
            try:
                if spr.mask.overlap_area(playerViewMask, (0,0)) > 0: # tries to use sprites own premade mask, if it has one
                    visibleSprites.add(spr)
                    #print("Mask from memory")
                #print("Used sprite mask from memory")

            except AttributeError: # if the object doesn't have the attribute mask, whip one up real fast
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
    def __init__(self, x = 10, y = 10, patrolPoints = [Point(10,10)], speed = 1.2):
        super().__init__(x, y, speed)

        self.image.blit(guardAlive, (0,0))
        self.image = self.image.convert_alpha()

        self.alive = True

        # Navigation related variables
        self.wantToGoHere = [False for _ in range(4)] # udlr
        self.wantToGoStack = [] # stack of direction indexes
        self.lastCoords = Point(self.virtualx, self.virtualy)
        self.problemSolvingDirection = rng.choice([-1,1])
        self.oldDest = Point()
        self.dirToTry = 0 # udlr indexes

        # Brain variables
        self.states = [False for _ in range(5)]
        self.lastSeenCorpse = None # uses rect.x and rect.y
        self.lastSeenPlayer = None # uses rect.x and rect.y
        self.lastSeenGuards = []
        self.patrolPoints = patrolPoints
        self.currentDest = rng.choice(self.patrolPoints)
        self.waitPingSent = False # used with investigating
        self.investigatedCorpses = []

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
        self.image.fill((0,0,0,0)) # make image blank
        self.image.blit(guardDead, (0,0)) # draw on dead guard texture

        pygame.time.set_timer(CHECKWIN, 1) # triggers a win check when a guard dies

    def altRoute(self):
        if self.states[4] == False: # if this is the first time altRoute() has been called...
            self.oldDest = self.currentDest # ... save the old destination
            self.dirToTry = (self.wantToGoStack[len(self.wantToGoStack) - 1] + self.problemSolvingDirection) % 4
        elif self.bannedDirs[self.dirToTry]: # if the way I'm currently trying to go is blocked
            self.wantToGoStack.append(self.dirToTry)
            self.dirToTry = (self.dirToTry + self.problemSolvingDirection) % 4
        elif len(self.wantToGoStack) == 0 or not self.bannedDirs[self.wantToGoStack[len(self.wantToGoStack) - 1]]: # if the latest direction I've been trying is now free
            try:
                self.dirToTry = self.wantToGoStack.pop()
            except IndexError:
                pass
            if len(self.wantToGoStack) == 0: # if the original direction I wanted to go is free and I've finished navigating around all obstacles
                if self.cPos.distance(self.currentDest) < 1:
                    self.states[4] = False # alt routing is no longer needed
                    self.currentDest = self.oldDest
                return # return early to prevent the below if statements from changing the destination

        if self.dirToTry == 0: # up
            self.currentDest = Point(self.cPos.x, self.cPos.y - self.width - self.speed)
        elif self.dirToTry == 1: # left
            self.currentDest = Point(self.cPos.x - self.width - self.speed, self.cPos.y)
        elif self.dirToTry == 2: # down
            self.currentDest = Point(self.cPos.x, self.cPos.y + self.width + self.speed)
        elif self.dirToTry == 3: # right
            self.currentDest = Point(self.cPos.x + self.width + self.speed, self.cPos.y)

    def walk(self, sprGroup = None, avoidRecurse = False):

        """
        Always check where to go using cPos, but move using virtual co-ordinates
        Guards will always try and stand directly on top of their destination
        """
        self.wantToGoHere = [False, False, False, False] # ULDR

        # x co-ordinate #
        if abs(self.cPos.x - self.currentDest.x) > self.speed:
            if self.currentDest.x < self.cPos.x: # left
                self.wantToGoHere[1] = True
                if not self.bannedDirs[1]:
                    self.virtualx -= self.speed
            elif self.currentDest.x > self.cPos.x: # right
                self.wantToGoHere[3] = True
                if not self.bannedDirs[3]:
                    self.virtualx += self.speed
        else: # fine adjusment
            if self.currentDest.x < self.cPos.x: # left
                self.wantToGoHere[1] = True
                if not self.bannedDirs[1]:
                    self.virtualx = self.currentDest.x - self.width / 2
            elif self.currentDest.x > self.cPos.x: # right
                self.wantToGoHere[3] = True
                if not self.bannedDirs[3]:
                    self.virtualx = self.currentDest.x - self.width / 2
        ###

        # y co-ordinate #
        # could change such that moving up/down is determined before the distance moved is
        if abs(self.cPos.y - self.currentDest.y) > self.speed:
            if self.currentDest.y < self.cPos.y: # up
                self.wantToGoHere[0] = True
                if not self.bannedDirs[0]:
                    self.virtualy -= self.speed
            elif self.currentDest.y > self.cPos.y: # down
                self.wantToGoHere[2] = True
                if not self.bannedDirs[2]:
                    self.virtualy += self.speed
        else: # fine adjustment
            if self.currentDest.y < self.cPos.y: # up
                self.wantToGoHere[0] = True
                if not self.bannedDirs[0]:
                    self.virtualy = self.currentDest.y - self.width / 2
            elif self.currentDest.y > self.cPos.y: # down
                self.wantToGoHere[2] = True
                if not self.bannedDirs[2]:
                    self.virtualy = self.currentDest.y - self.width / 2
        ###

        self.posUpdate()

        if sprGroup:
            self.collisionCheck(sprGroup)

            if not avoidRecurse: # used to stop altRoute calling walk calling altRoute etc.
                for thisWay in range(4):
                    self.wantToGoStack = []

                    if self.bannedDirs[thisWay] and self.wantToGoHere[thisWay]: # last clause to prevent repeat appending
                        self.wantToGoStack.append(thisWay) # if found to be blocked, direction added as somewhere the guard originally wanted to go

                    if len(self.wantToGoStack) >= 2 or sum(self.wantToGoHere) == len(self.wantToGoStack): # if I'm not going anywhere that isn't blocked
                        self.altRoute()
                        self.states[4] = True # must be left after the above to prevent the original destination being overwritten

    def patrol(self):
        if self.currentDest.distance(Point(self.cPos.x, self.cPos.y)) < self.width / 2 and len(self.patrolPoints) > 1: # if I'm close to my destination  (and there are multiple patrol points to choose from)...
            self.currentDest = self.patrolPoints[(self.patrolPoints.index(self.currentDest) + 1) % len(self.patrolPoints)] # ... set the destination to be next point in patrol points list
        elif self.currentDest not in self.patrolPoints: # if not currently heading towards a patrol point...
            self.currentDest = self.patrolPoints[rng.randint(0, len(self.patrolPoints) - 1)] # ... pick a random one and start heading there

    def generatePatrol(self, focus, radius):
        # method creates a random 3 point patrol given a central point and radius
        # currently does not check to ensure the path is possible
        focus = focus.round()
        udlr = [rng.choice([-1,1]), rng.choice([-1,1])] # chooses -1 or 1 randomly
        self.patrolPoints = [Point(focus.x + (radius * udlr[0]), focus.y + (radius * udlr[1])), focus, Point(focus.x - (radius * udlr[0]), focus.y - (radius * udlr[1]))]

    def lookAround(self, viewMask, actors):
        alreadySeenAGuard = False

        actors.remove(self) # don't look at yourself silly (also saves an iteration in the below for loop)

        for actor in actors:
            virtualDisplay.fill(white)
            virtualDisplay.blit(actor.image, (actor.rect.x, actor.rect.y)) # this has to remain as is, don't change things to cPos
            if viewMask.overlap(pygame.mask.from_surface(virtualDisplay), (0,0)):
                try: # EAFP for checking if actor is guard or player
                    if actor.alive: # if the guard is alive - will throw AttributeError if this is the player
                        if not alreadySeenAGuard: # if it's the first guard I've seen...
                            self.lastSeenGuards = [] # ... jettison all other previously know guard locations, to avoid duplicates
                            alreadySeenAGuard = True
                        self.lastSeenGuards.append(Point(actor.cPos.x, actor.cPos.y))
                    elif actor.cPos not in self.patrolPoints and self.states[1] == False and actor.cPos not in self.investigatedCorpses: # if the corpse isn't one I'm patrolling around already, and I'm not already taking a shuftie at another corpse already, oh and I haven't already investigated this corpose
                        self.lastSeenCorpse = actor.cPos
                        self.states[1] = True
                except AttributeError: # must be the player
                    self.lastSeenPlayer = Point(actor.cPos.x, actor.cPos.y)
                    self.states[0] = True

        actors.add(self) # so you don't bamboozle the next guard running this loop

    def quickLook(self, viewMask, actor):
        virtualDisplay.fill(white)
        virtualDisplay.blit(actor.image, (actor.rect.x, actor.rect.y))
        return viewMask.overlap(pygame.mask.from_surface(virtualDisplay), (0,0))

    def brain(self, player, allyGroup, actorGroup, envGroup, amVisible, devMode = False):

        self.lastCoords = Point(self.cPos.x, self.cPos.y)

        if self.states[3]:
            view = (180, 40) # angle, distance
        else:
            view = (90, 150)

        viewMask = self.cone(self.currentDest, view[0], view[1], devMode or amVisible, True)
        """
        Cone is drawn with a viewing angle and distance dependent on what the guard is doing. This is drawn to the game screen if the guard can be seen or devMode is True.
        The mask of this cone is saved so it can be used again if necessary (sometimes it's used again with .quickLook())
        """

        #drawMask(viewMask, lightgrey)

        self.lookAround(viewMask, actorGroup)

        if pygame.sprite.collide_rect(player, self): # if guard is touching the player
            print("Game Over!")

        if self.states[4]: # navigating around an obstacle to get to destination
            if self.bannedDirs[self.dirToTry]: # if I can't move...
                self.wantToGoStack.append(self.dirToTry) # ... the direction I just tried to move in must be blocked by something
            self.altRoute() # Must be called every time
            if devMode:
                drawText("Alt-routing", (self.rect.x + 10, self.rect.y + 14))

        elif self.states[0]: # gotta go get the player! Grrrr
            self.currentDest = self.lastSeenPlayer

            if self.rect.x == self.lastSeenPlayer.x and self.rect.y == self.lastSeenPlayer.y and self.quickLook(viewMask, player) == False: # lost the player
                self.states[0] = True # no longer aware of player
                self.states[3] = True # investigate around last known point
                self.generatePatrol(self.currentDest, rng.randint(100,300)) # generate a new patrol centering on the player's last known location
                if devMode:
                    drawText("Searching for player", (self.rect.x + 10, self.rect.y + 28))
            elif devMode:
                drawText("Chasing player", (self.rect.x + 10, self.rect.y + 28))

        elif self.states[1]: # upon seeing a guard's corpse
            self.currentDest = self.lastSeenCorpse # go to the last seen corpse

            if abs(self.cPos.x - self.currentDest.x) <= self.width and abs(self.cPos.y - self.currentDest.y) <= self.width: # if within a body length of the corpse
                self.states[3] = True # investigating around a point
                self.generatePatrol(self.currentDest, rng.randint(100,300)) # generate a new patrol centering on the corpse
                self.states[1] = False # stops this routine running next frame
                if devMode:
                    drawText("At corpse, new patrol made", (self.rect.x + 10, self.rect.y + 42))
            elif devMode:
                drawText("Seen corpse", (self.rect.x + 10, self.rect.y + 42))

        if self.states[3]: # if investigating a point, assuming self.currentDest is the thing we're interested in
            if devMode:
                drawText("Investigating here", (self.rect.x + 10, self.rect.y + 56))
            if not self.waitPingSent:
                pygame.time.set_timer(GUARDTHINK, rng.randint(1000, 5000)) # guard waits for a random amount of time between 1 and 5 seconds
                self.waitPingSent = True
            return

        elif not self.states[0] and not self.states[1] and not self.states[4]: # if I'm not doing anything that would mean I wouldn't be following my patrol
            self.patrol() # patrol as usual
            if devMode:
                drawText("Patrolling normally", (self.rect.x + 10, self.rect.y + 70))

        self.walk(envGroup, self.states[4]) # ... I suppose I ought to walk around

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
        self.rect.x = round(x)
        self.rect.y = round(y)
        self.cPos = Point(self.rect.x + self.width/2, self.rect.y + self.height/2)

        virtualDisplay.fill(white)
        tempGroup = pygame.sprite.GroupSingle()
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

    def posUpdate(self):
        self.cPos = Point(self.rect.x + self.width/2, self.rect.y + self.height/2)

    def getShot(self):
        if self.destructable: # wall breaks
            self.kill() # removes sprite
            print("Wall shot. Wall dead.")
        else:
            print("Wall shot. Wall smiles.")

class Objective(Obstacle):
    def __init__(self, x = 0, y = 0, w = 250, h = 250):
        super().__init__(x, y, w, h, False)
        self.colour = green
        self.image.fill(self.colour)

    def getShot(self):
        print("Shooting the objective won't win you the game, but it might feel satisfying")

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

        self.image = pygame.Surface([2, 2]) # does a projectile even need an image?
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
                print("Bullet out of bounds. Removing")
                self.kill()
                return

        collidedWith = pygame.sprite.spritecollide(self, sprGroup, False) # list of all objects collided with from within the specified sprGroup

        print("Registered hit")

        for obj in collidedWith:
            obj.getShot() # registers hit for each object collided with in turn

        if not bulletPen or type(collidedWith[0]) == type(Obstacle()): # if there is no bullet penetration or the bullet hit a wall || 2ND CLAUSE MAY NOT WORK
            self.kill() # remove the bullet
        else:
            sprGroup.remove(collidedWith[0]) # remove the sprite just hit from the group, so it won't be hit again || THIS MAY CAUSE ISSUES IF NOT READDED
            self.go(sprGroup, bulletPen) # recurse the function to allow bullet to continue travelling

def drawText(text, loc, colour = (0,0,0), font = "Comic Sans MS", fontSize = 14):
    theFont = pygame.font.SysFont(font, fontSize) # cache this maybe?
    textRender = theFont.render(str(text), True, colour)
    gameDisplay.blit(textRender, loc)
    return textRender

def drawMask(mask, colour = (0,0,0)): # alternative name is destroyFPS()
    for i in range(displayWidth):
        for j in range(displayHeight):
            if mask.get_at((i, j)) != 0:
                pygame.gfxdraw.pixel(gameDisplay, i, j, colour)

def instance():
    level = Level()
    level.loadFromFile()
    devMode = True

    # hide mouse
    pygame.mouse.set_visible(False)
    # check for wins
    pygame.time.set_timer(CHECKWIN, 25)

    # initialise done before anything is drawn to the screen
    playerView = pygame.mask.from_surface(gameDisplay)

    while level.running:
        mouse = pygame.mouse.get_pos()
        mouse = Point(mouse[0], mouse[1]) # for sake of consistency throughout program

        for event in pygame.event.get():
            # Any pygame handled events should be put here #
            # Quit the game
            if event.type == pygame.QUIT or event.type == EMERGENCYSTOP:
                level.running = False

            # Key pressed (triggers once, even if held) #
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE: # close game if escape is pressed
                    level.running = False

                if event.key == pygame.K_r: # press R to reload
                    if level.player.currentMag < level.player.magSize:
                        if level.player.currentMag >= 1: # short reload
                            pygame.time.set_timer(RELOAD, level.player.shortReload) # start the reload
                            level.player.currentMag = 1 # immersion science
                        else: # long reload
                            pygame.time.set_timer(RELOAD, level.player.longReload) # start the reload

                if event.key == pygame.K_RIGHTBRACKET:
                    devMode = not devMode # python is magical sometimes

                if event.key == pygame.K_l and devMode: # prints out the level debug into console if the user is in devMode
                    level.printLevel()
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN: # shoot the gun
                level.player.shoot(mouse, level.allGroup)
                pygame.time.set_timer(RELOAD, 0) # cancels a reload upon shooting

            if event.type == RELOAD:
                pygame.time.set_timer(RELOAD, 0) # prevents re-reloading chain (just pygame things)
                level.player.reload()

            if event.type == CHECKWIN:
                pygame.time.set_timer(CHECKWIN, 25)
                level.checkWin(devMode)

            if event.type == GUARDTHINK:
                pygame.time.set_timer(GUARDTHINK, 0)
                for guard in level.guards:
                    if guard.states[3] and guard.waitPingSent:
                        guard.investigatedCorpses.append(guard.currentDest)
                        guard.states[3] = False
                        guard.waitPingSent = False
            ###

        # Keys being held #
        keys = pygame.key.get_pressed()

        # W
        if keys[pygame.K_w]:
            level.player.move('u', level.environmentGroup)
        # A
        if keys[pygame.K_a]:
            level.player.move('l', level.environmentGroup)
        # S
        if keys[pygame.K_s]:
            level.player.move('d', level.environmentGroup)
        # D
        if keys[pygame.K_d]:
            level.player.move('r', level.environmentGroup)
        ###

        gameDisplay.fill(white) # clean up arc drawings

        #playerView.invert()
        #drawMask(playerView, lightgrey) # can be used to draw mask if needed, makes frame time go up to ~500

        # Text draws #
        drawText("{pewsLeft} / {pews}".format(pewsLeft = level.player.currentMag, pews = level.player.magSize), (mouse.x + 10, mouse.y + 10)) # remaining bullets in mag are slapped just below the mouse
        drawText("FPS: {fps}".format(fps = round(clock.get_fps())), (2,0)) # fps counter
        if devMode:
            drawText("Frame Time: {ft}".format(ft = clock.get_rawtime()), (2,18)) # frame time
        ###

        # Rendering functions #
        playerView = level.player.cone(mouse, 90, 200, True, True)
        level.visibleGroup = level.player.selectToRender(playerView, level.allGroup) # decide what needs rendering

        for guard in level.guards: # this is where the brain should be called from
            if guard.alive: # prevents the guard from moving if they're dead - quite useful
                guard.brain(level.player, level.guardGroup, level.actorGroup, level.environmentGroup, (guard in level.visibleGroup), devMode)

        if not devMode:
            level.visibleGroup.draw(gameDisplay)
        else:
            level.allGroup.draw(gameDisplay)

        level.player.drawCrosshair(mouse)
        level.playerGroup.draw(gameDisplay) # draw player so that they're over the top of the crosshair lines
        try:
            level.objectiveGroup.draw(gameDisplay) # draw the objective
        except: # if there is no objective, no worries
            pass
        ###

        """
        collided = pygame.sprite.spritecollide(player, environmentSprites, False) # returns array of objects collided with
        guardHit = pygame.sprite.collide_rect(player, guard) # returns boolean
        """

        pygame.display.update()
        clock.tick(framerate) # manages fps game is displayed at

    pygame.quit()
    print("\nPygame window closed")
    exit()

if __name__ == "__main__":
    instance()
