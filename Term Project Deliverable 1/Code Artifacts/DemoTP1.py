# Barebones timer, mouse, and keyboard events

import pygame
from pygame.locals import *
import random
import math

GREEN = (47,171,51)
RED = (200,0,0)
GRAY = (55,55,55)

class CellWar(object):
    def mousePressed(self,event):
        self.recordPos = None # refresh everytime with NEW click
        self.count += 1
        x,y = self.mousePos
        self.lineDrawn = [(x,y),(x,y),False]
        for cell in self.cellList:
            if cell.color == GREEN:
                if dist(x,y,cell.x,cell.y,cell.radius):
                    self.lineDrawn = [(cell.x,cell.y),(cell.x,cell.y),True]
                    self.dealCell = cell
                    break
        print "Mouse Pressed"
        self.redrawAll()


            
    def keyPressed(self,event):
        print "Key Pressed"
        self.redrawAll()

    def timerFired(self):
        self.animateCount += 1
        self.redrawAll()
        if self.animateCount % 58 == 0:
            self.increaseValue(GREEN)
        if self.animateCount % 60 == 0:
            self.increaseValue(RED)
        self.fps = 20
        #print self.dealCell
        self.clock.tick(self.fps)
        self.mousePos = pygame.mouse.get_pos()     
        #manually manage the event queue
        if pygame.mouse.get_pressed()[0] == False and len(self.lineDrawn) == 3:
            self.recordPos = self.lineDrawn[1]
            self.lineDrawn = []
        if self.recordPos != None:
            try:
                if self.dealCell.name == "EMB":             
                    if not dist(self.dealCell.x,self.dealCell.y,\
                                    self.recordPos[0],self.recordPos[1],0.5):
                        self.dealCell.moveJudge = True
                        self.dealCell.move(self.recordPos[0],\
                                            self.recordPos[1],self.fps)
                    else:
                        self.recordPos = None
                        self.dealCell = None
            except:
                pass
            try:
                if self.dealCell.name == "ATT":
                    for cell in self.cellList:
                        if cell.name == "ATT":
                            if dist(self.recordPos[0],self.recordPos[1],cell.x,\
                                    cell.y,cell.radius):
                                chain = Chain(self.dealCell.x,self.dealCell.y,\
                                          cell.x,cell.y,self.dealCell.color)
                                self.chains.append(chain)
                                if self.dic[self.dealCell] == -1:
                                    # newly created key
                                    self.dic[self.dealCell] = [chain]
                                else:
                                    self.dic[self.dealCell].append(chain)
                            # note the direction is from self.dealCell to cell
                                break
                            # found the intended target
                    self.recordPos = None
                    self.dealCell = None
                    # set to None after finding once
            except:
                pass
            
  

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                self.mode = "Done"
            elif (event.type == pygame.MOUSEBUTTONDOWN):
                self.mousePressed(event)
            elif (event.type == pygame.KEYDOWN):
                self.keyPressed(event)

    def increaseValue(self,color):
        for cell in self.cellList:
            if cell.color == color:
                if cell.name == "ATT":
                    cell.value += 1
                else:
                    cell.increaseCount += 1
                    if cell.increaseCount % 2 == 0:
                        cell.value += 1
                        cell.increaseCount = 0


    def drawLine(self):
        lineDrawn = self.lineDrawn
        if len(lineDrawn) == 3:
            pygame.draw.line(self.screen,(255,255,0),lineDrawn[0],lineDrawn[1],3)
    
    def traceLine(self):
        if len(self.lineDrawn) == 3:
            self.lineDrawn.pop(1)
            self.lineDrawn.insert(1,self.mousePos)
            if self.lineDrawn[-1]:
                x,y = self.mousePos
                for cell in self.cellList:
                    if dist(x,y,cell.x,cell.y,cell.radius):
                        Lock(cell.x,cell.y).drawLock(self.screen)
                        

    def drawLock(self):
        lineDrawn = self.lineDrawn
        try:
            if self.lineDrawn[-1]: # True means indeed locked
                Lock(lineDrawn[0][0],lineDrawn[0][1]).drawLock(self.screen)
        except:
            pass

    def drawChain(self):
        for chain in self.chains:
            if chain.shouldGrow:
                chain.growNum += 1
                if chain.growNum % 2 == 0:
                    chain.grow()
            chain.drawChain(self.screen)
                
    def traceTransfer(self):
        for cell in self.cellList:
            if cell.name == "ATT" and type(self.dic[cell]) != int:
                # meaning it is an object (i.e. a chain!)
                for i in xrange(len(self.dic[cell])):
                    # recall that self.dic[cell] returns the chains that "cell"
                    # currently has.
                    ###############################################################
                    # Remember to delete chains from dictionary when crossed!
                    ###############################################################
                    if not self.dic[cell][i].shouldGrow:
                        self.dic[cell][i].shiningInd += 1
                        if self.dic[cell][i].shiningInd >= \
                           self.dic[cell][i].dotNum:
                            self.dic[cell][i].shiningInd = 5
                            self.traceTransfer()
                    #########################################################
                    # for each complete transfer, remember to weaken target
                    #########################################################
            
        
    def redrawAll(self):
        if self.animateCount == 700:
            self.animateCount = 0 # reset
        cellImg = self.imageList[0]
        self.screen.blit(self.bgimage,(0,0))
        #self.screen.set_clip(50,50,550,550)
        self.traceLine()
        self.drawLock()
        self.traceTransfer() # trace the transfer through chains
        self.drawChain()
        self.drawLine()
        for cell in self.cellList:
            if cell.name == "ATT":
                if self.animateCount % 7 == 0:
                    self.order = not self.order
                cellImg = self.imageList[(self.animateCount%10)/5] if self.order else\
                          self.imageList[-(self.animateCount%10)/5 - 1]
                self.screen.blit(cellImg,(cell.x-48,cell.y-53))
            cell.drawCell(self.screen)
        pygame.display.flip()

    def init(self):
        self.mode = "Running"
        self.imageList = [pygame.image.load('GreenCell4.png'),\
                     pygame.image.load('GreenCell9.png'),\
                     pygame.image.load('GreenCell6.png'),\
                     pygame.image.load('GreenCell8.png'),\
                     pygame.image.load('GreenCell5.png'),\
                     pygame.image.load('GreenCell7.png'),\
                     pygame.image.load('GreenCell3.png')]
        self.animateCount,self.count = 0,0
        # self.animateCount is for animation image use
        self.lineDrawn = []
        self.recordPos = None # a temporary position recorder
        self.order = True # left to right
        self.cellList = Level_3().cellList
        self.chains = []
        self.connections = [] # record which chain has been established.
        self.dic = dict() # same as above, to record.
        ##################################################################
        # temporarily, self.connections is kept, but currently of no use.
        ##################################################################
        for cell in self.cellList:
            if cell.name == "ATT":
                self.dic[cell] = -1 # by default
        self.redrawAll()

    def run(self):
        pygame.init()
        
        # initialize the screen
        self.screenSize = (600,600)
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("Game Window")
        self.bgimage = pygame.image.load("1_back6.jpg") 
        
        # initialize clock
        self.clock = pygame.time.Clock()
        # the cell we are dealing with
        self.dealCell = "ATT"
        self.init()
        self.timerFired()
        while (self.mode != "Done"):
            self.timerFired()

class Level_1(object):
    def __init__(self):
        self.c1 = Cell(300,400,25)
        self.c2 = Cell(500,300,10)
        self.c3 = Cell(240,230,10,(200,0,0))
        self.cellList = [self.c1,self.c2,self.c3]

class Level_2(object):
    def __init__(self):
        self.c1 = Cell(300,400,5,(55,55,55))
        self.c2 = Cell(500,300,10)
        self.c3 = Cell(240,230,10,(200,0,0))
        self.cellList = [self.c1,self.c2,self.c3]


class Level_3(object):
    def __init__(self):
        self.c1 = Cell(100,400,5,(55,55,55))
        self.c2 = Cell(500,370,50)
        self.c3 = Cell(240,230,47,(200,0,0))
        self.c4 = Embracer(520,80,3,(200,0,0))
        self.c5 = Embracer(230,125,10,GREEN)
        self.cellList = [self.c1,self.c2,self.c3,self.c4,self.c5]


class Cell(object):
    def __init__(self,x,y,value=20,color=GREEN):
        self.x,self.y = x,y
        self.color = color # green by default
        self.radius = 23
        self.outerRadius = self.radius + 8
        self.value = value
        self.name = "ATT"
        self.d = dict()

    def drawCell(self,surface):
        center = (self.x,self.y)
        pygame.draw.circle(surface,(255,255,255),center,self.outerRadius,2)
        pygame.draw.circle(surface,self.color,center,self.radius,0)
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
        acce = (distance*2/1.6**2)/fps #acceleration. Complete in 3 sec
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


        
class Lock(object):
    def __init__(self,x,y):
        self.x,self.y = x,y
        self.radius = 30
        self.color = (255,255,0) # yellow

    def drawLock(self,surface):
        #self.drawCirc(surface)
        self.drawArr(surface)

    def drawCirc(self,surface):
        center = (self.x,self.y)
        pygame.draw.circle(surface,self.color,center,self.radius,2)

    def drawArr(self,surface):
        self.drawArrAng(surface,0)
        self.drawArrAng(surface,1)
        self.drawArrAng(surface,2)
        self.drawArrAng(surface,3)

    def drawArrAng(self,surface,angle):
        ang = angle*math.pi/2 + 3*math.pi/4

        if angle % 2 == 1: # topRight/bottomLeft
            tip1 = (self.x+self.radius*math.cos(ang),\
                    self.y-self.radius*math.sin(ang))
            delta = +30 if angle == 1 else -30
            tip2 = (tip1[0]-delta-5,tip1[1]+delta-5)
            tip3 = (tip1[0]-delta+5,tip1[1]+delta+5)

        else:
            tip1 = (self.x+self.radius*math.cos(ang),\
                    self.y-self.radius*math.sin(ang))
            delta = +30 if angle == 2 else -30
            tip2 = (tip1[0]+delta-5,tip1[1]+delta+5)
            tip3 = (tip1[0]+delta+5,tip1[1]+delta-5)
        pygame.draw.polygon(surface,self.color,(tip1,tip2,tip3))

class Chain(object):
    def __init__(self,startx,starty,endx,endy,color=GREEN):
        self.color = color
        self.startx,self.starty = startx,starty
        self.endx,self.endy = endx,endy
        self.direction = math.atan(float(starty-endy)/(endx-startx))
        self.chainFinalLen = ((endx-startx)**2+(endy-starty)**2)**0.5
        self.dotNum = (self.chainFinalLen-23)/(3*2) # 23 is cell radius
        # 3 is the radius of the small dot,so 3*2 is the diameter
        self.chainInit = 1 # initially of length (dot) 1.
        self.chainList = [(startx,starty)]
        self.shouldGrow = True # at first, every chain should grow
        self.growNum = 0 # to control the speed of the growth
        self.lineHalfLength = 5.5
        self.shiningInd = -1 # the dot on the chain that shines

    def grow(self):
        startx = self.chainList[-1][0]
        starty = self.chainList[-1][1]
        newx = startx - 6*math.cos(self.direction)
        newy = starty + 6*math.sin(self.direction)
        self.chainList.append((newx,newy))
        if dist(newx,newy,self.endx,self.endy,1):
            self.shouldGrow = False

    def drawChain(self,surface):
        length = self.lineHalfLength
        angle = self.direction
        for i in xrange(len(self.chainList)):
            dot = self.chainList[i]
            dotx = int(round(dot[0]))
            doty = int(round(dot[1]))
            color = (255,255,0) if i == self.shiningInd else self.color
            # the dot that should shine shines.
            pygame.draw.circle(surface,color,(dotx,doty),3,0)
            linestx = int(round(dotx-length*math.sin(math.pi-angle)))
            linesty = int(round(doty+length*math.cos(math.pi-angle)))
            lineEndx = int(round(dotx+length*math.sin(math.pi-angle)))
            lineEndy = int(round(doty-length*math.cos(math.pi-angle)))           
            pygame.draw.line(surface,color,(linestx,linesty),\
                             (lineEndx,lineEndy),2)
            

    def __str__(self):
        return """Chain starting from (%.1f,%.1f) and ending at (%.1f,%.1f),
        with angle %.1f"""\
               %(self.startx,self.starty,self.endx,self.endy,self.direction)
                        
        
        
            

def dist(x1,y1,x2,y2,r):
    return ((x1-x2)**2+(y1-y2)**2)**(0.5) <= r+3

CellWar().run()
