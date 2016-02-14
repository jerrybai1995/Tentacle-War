import pygame
from pygame.locals import *
import random
import math
import pickle
import time
from levelClasses import *

GREEN = (47,171,51)
RED = (200,0,0)
GRAY = (55,55,55)
WHITE = (255,255,255)
WARMYELLOW = (255,255,85)

class Cell(object):
    def __init__(self,x,y,value=20,color=GREEN):
        self.x,self.y = x,y
        self.color = color # green by default
        self.radius = 23
        self.outerRadius = self.radius + 8
        self.value = value
        self.name = "ATT"
        self.state = None
        self.d = dict()
        self.getNeedle = False # being injected?
        self.injectTime = 0 # start counting the time during Injection from 0
        self.fakeNeedle = False # needle left is 0

    def drawCell(self,surface):
        center = (self.x,self.y)
        color = WHITE if not self.getNeedle else GREEN
        pygame.draw.circle(surface,color,center,self.outerRadius,3)
        pygame.draw.circle(surface,self.color,center,self.radius,0)
        ############# possibly a gradient effect ###############
        pygame.draw.circle(surface,(255,255,255),center,self.radius,2)
        self.drawValue(surface)
        if self.value >= 50:
            # more fashion drawing for larger cell
            for i in xrange(8):
                size = random.randint(2,6)
                self.drawSideCircle(surface,i,size)

    def drawSideCircle(self,surface,ang,radius):
        angle = ang*math.pi/4
        cx,cy = int(round(self.x+self.outerRadius*math.cos(angle))),\
                int(round(self.y+self.outerRadius*math.sin(angle)))
        pygame.draw.circle(surface,self.color,(cx,cy),radius,0)

    def drawValue(self,surface):
        my_font = pygame.font.SysFont("",21,True)
        textObj = my_font.render("%d"%self.value,True,(255,255,255))
        if len(str(self.value)) == 2:
            surface.blit(textObj,(self.x-8,self.y-10.5))
        else:
            surface.blit(textObj,(self.x-5,self.y-10.5))

    def findDistanceInChainUnits(self,targetx,targety):
        # for Artificial Intelligence use
        # chain unit (dot) is of length of 3
        geoDistance = ((targetx-self.x)**2+(targety-self.y)**2)**0.5
        dotNumber = geoDistance/(3*2) # diameter
        valueNeed = dotNumber/2
        return valueNeed


    def findAllies(self,allCellList):
        # in game, allCellList should be self.cellList
        self.alliesList = []
        embList = [] # temporary list for EMB
        allyAvg = 0
        for cell in allCellList:
            if cell.color == self.color: # possibly used for BLUE?
                if cell.name == "ATT" and cell.x != self.x:
                    self.alliesList.append((cell.value,cell.name,cell))
                else:
                    embList.append((cell.value,cell.name,cell))
                allyAvg += cell.value
        # EMB cells first, and then ATT cell, in cell value order
        self.alliesList = sorted(embList) + sorted(self.alliesList)
        if len(self.alliesList) != 0:
            return float(allyAvg)/len(self.alliesList)
        else:
            return 0 # force the cell to be in defense mode

    def findEnemiesWithinDistance(self,allCellList):
        """ return self.grayList and self.allOtherList as a tuple """
        # for AI use. 
        self.enemiesList = []
        grayList = [] # higher priority should be put in front
        enemyAvg = 0
        for cell in allCellList:
            if cell.color != self.color:
                valueNeed = self.findDistanceInChainUnits(cell.x,cell.y)
                if self.value - valueNeed > 10:
                # that is, after reaching out tentacle, value left is 10
                    # gray (neutral) cell should be of priority
                    if cell.color == GRAY:
                        # ATTENTION! No longer cell.name for index 1
                        grayList.append((cell.value,cell.color,cell))
                    elif cell.name == "ATT":
                        # the heuristic here is that estimated distance
                        # to travel plus target's value
                        enemyAvg += cell.value
                        self.enemiesList.append((cell.value+valueNeed,\
                                                 cell.color,cell))
        self.grayList = list(grayList) # just in case, so that no aliasing
        self.allOtherList = list(reversed(sorted(grayList)))+sorted(self.enemiesList)
        if len(self.enemiesList) != 0:
            return float(enemyAvg)/len(self.enemiesList)
        else:
            return 100 # force the cell to be in defense mode
                

    def think(self,environment,animateCount):
        # the thinking process refers to the AI
        #####################################################################
        #     Later possibly use value drop in time also to determin. For
        # instance, consider d(C.V.)/dt
        #####################################################################
        enemyAvg = self.findEnemiesWithinDistance(environment)
        allyAvg = self.findAllies(environment)
        count = animateCount
        #print allyAvg,enemyAvg
        if self.value < 15:
            self.state = "Defense"
        elif self.value >= 15:
            if self.value+5 >= enemyAvg:
                self.state = "Attack"
            elif self.value + allyAvg >= enemyAvg*3./2:
                self.state = "Attack"
            else:
                self.state = "Defense"

    def update(self,environment,animateCount):
        # update every aspect: camp, current mode, etc.
        # ONLY ENEMY CELL NEEDS TO UPDATE.
        self.think(environment,animateCount)
        # change mode,find friends,find enemies
            
        

    def __hash__(self):
        hashable = (self.x,self.y)
        return hash(hashable)

class Embracer(Cell):
    def __init__(self,x,y,value,color=(47,171,51)):
        super(Embracer,self).__init__(x,y,value,color)
        self.name = "EMB"
        self.increaseCount = 0
        self.moveJudge = False
    
    def drawCell(self,surface):
        #print self.name,self.x,self.y
        center = (x,y) = (self.x,self.y)
        add = int(round(2*self.radius/(3**0.5)))

        pygame.draw.polygon(surface,(255,255,255),((x,y-self.radius-8),\
                            (x+add,y+self.radius-8),\
                            (x-add,y+self.radius-8)))
        pygame.draw.circle(surface,self.color,center,self.radius,0)
        pygame.draw.circle(surface,(255,255,255),center,self.radius,2)
        self.drawValue(surface)

    def setTarget(self,targetx,targety,fps):
        distance = ((targetx-self.x)**2+(targety-self.y)**2)**0.5
        acce = (distance*2/3**2)/fps #acceleration. Complete in 3 sec
        self.speed = int(round((2*acce*distance)**0.5))
        self.speedx = int(round(((targetx-self.x)/distance)*self.speed))
        self.speedy = int(round(((targety-self.y)/distance)*self.speed))
        self.accex = ((targetx-self.x)/distance)*acce
        self.accey = ((targety-self.y)/distance)*acce

    def move(self,targetx,targety,fps):
        self.setTarget(targetx,targety,fps)
        if self.moveJudge:
            self.x += self.speedx
            self.y += self.speedy
            if dist(targetx,targety,self.x,self.y,0.5):
                self.speedx -= int(round(self.accex))
                self.speedy -= int(round(self.accey))
            else:
                self.moveJudge = False #stops
            self.sprite.rect.x = self.x
            self.sprite.rect.y = self.y
            
class Level_1(object):
    def __init__(self):
        self.c1 = Cell(300,400,2)
        self.c2 = Cell(500,400,2)
        self.c3 = Cell(630,460,100,(200,0,0))
        self.cellList = [self.c1,self.c2,self.c3]

class Level_2(object):
    def __init__(self):
        self.c1 = Cell(600,400,5,(55,55,55))
        self.c2 = Cell(500,500,10)
        self.c3 = Cell(240,620,10,(200,0,0))
        self.cellList = [self.c1,self.c2,self.c3]


class Level_3(object):
    def __init__(self):
        self.c1 = Cell(100,400,5,(55,55,55))
        self.c2 = Cell(500,370,46)
        self.c3 = Cell(240,230,7,(200,0,0))
        self.c4 = Embracer(520,80,3,(200,0,0))
        self.c5 = Embracer(230,125,10,GREEN)
        self.c6 = Cell(650,600,40,(200,0,0))
        self.c7 = Cell(560,500,60)
        self.cellList = [self.c1,self.c2,self.c3,self.c4,self.c5,self.c6,self.c7]

class Level_4(object):
    def __init__(self):
        self.c1 = Cell(350,300,0,(55,55,55))
        self.c2 = Cell(500,370,30)
        self.c3 = Cell(240,230,15,(200,0,0))
        self.c4 = Cell(150,600,15,(200,0,0))
        self.c5 = Embracer(230,125,10,GREEN)
        self.c6 = Cell(450,180,15,(200,0,0))
        self.c7 = Cell(560,500,10,(55,55,55))
        self.cellList = [self.c1,self.c2,self.c3,self.c4,self.c5,self.c6,self.c7]

class Level_5(object):
    def __init__(self):
        self.cellList = []
        for x in xrange(150,650,150):
            if x%300 == 0:
                cell = Cell(x,x,30,GREEN)
            else:
                cell = Cell(x,x,25,GREEN)
            self.cellList.append(cell)
        for x in xrange(150,650,150):
            cell = Cell(x,750-x,22,(200,0,0))
            self.cellList.append(cell)

class Level_6(object):
    def __init__(self):
        self.c1 = Cell(250,150,12,GREEN)
        self.c2 = Cell(450,150,12,GREEN)
        self.c3 = Cell(150,int(round(150+100*math.sqrt(3))),12,GREEN)
        self.c4 = Cell(550,int(round(150+100*math.sqrt(3))),12,GREEN)
        self.c5 = Cell(250,int(round(150+200*math.sqrt(3))),12,GREEN)
        self.c6 = Cell(450,int(round(150+200*math.sqrt(3))),12,GREEN)
        self.c7 = Cell(350,320,60,RED)
        self.cellList = [self.c1,self.c2,self.c3,self.c4,self.c5,\
                         self.c6,self.c7]
