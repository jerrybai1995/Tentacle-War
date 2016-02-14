# Barebones timer, mouse, and keyboard events

import pygame
from pygame.locals import *
import random
import math
import pickle
import time

GREEN = (47,171,51)
RED = (200,0,0)
GRAY = (55,55,55)

class CellWar(object):
    def __init__(self):
        self.levelCleared = [1]

    def saveLoad(self):
        outFile1 = open('myLevelCleared.txt','wb')
        #outFile2 = open('myAchievement.txt','wb')
        pickle.dump(self.levelCleared,outFile1)
############################ MAKE ACHIEVEMENT ###############################
############################ HIGH SCORE?? ###############################
        #pickle.dump(self.achievement,outFile2)
        outFile1.close()
        #outFile2.close()

    def readFile(self):
        inFile1 = open('myLevelCleared.txt','rb')
        #inFile2 = open('myAchievement.txt','rb')
        self.levelCleared = pickle.load(inFile1)
        #self.achievement = pickle.load(inFile2)

    ###################################################
    # SAVE AND LOAD PREVIOUS RECORD! IMPORTANT!
    ###################################################
    
    def mousePressed(self,event):
        if self.mode == "Running":
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
            self.redrawAll()
        if self.mode == "Choose Background":
            if self.bgchoice != None: # such that the choice is valid
                self.background = self.backgroundImages[self.bgchoice]
                self.chooseLevel()
        if self.mode == "Game Over":
            if self.gameOverchoice != None:
                if self.gameOverchoice == 0:
                    self.chooseLevel()
                if self.gameOverchoice == 1:
                    self.init(self.levelChosen)
        if self.mode == "Win":
            if self.winchoice != None:
                if self.winchoice == 0:
                    self.chooseLevel()
                if self.winchoice == 1:
                    self.init(self.levelChosen)
                if self.winchoice == 2:
                    self.levelCleared = range(self.levelChosen+1)
                    self.levelCleared.pop(0)
                    self.init(self.levelChosen+1)
        print "Mouse Pressed"
        


            
    def keyPressed(self,event):
        print "Key Pressed"
        if event.key == pygame.K_s:
            self.saveLoad()
        if event.key == pygame.K_SPACE:
            self.readFile()
        if event.key == pygame.K_p:
            print self.levelCleared
        if self.mode == "Main Menu":
            if event.key == pygame.K_DOWN:
                self.menuNumber += 1
            elif event.key == pygame.K_UP:
                self.menuNumber -= 1
            elif event.key == pygame.K_RETURN and self.mode == "Main Menu":
                self.runMenuOption(self.menuOption[self.menuNumber])
            self.menuNumber %= len(self.menuOption)
            if self.gameDisplayDepth == 1: # on main menu
                self.screen.blit(self.mainImages[self.menuNumber],(0,0))
                pygame.display.update()
        if self.mode == "Choose Background":
            print "Use your mouse to choose!"
        if self.mode == "Choose Final Level":
            self.identifyLevel(event)

        if self.mode == "Help":
            if event.key == pygame.K_r:
                self.doMainMenu() # if r is pressed in "help", get back to main menu
            elif event.key == pygame.K_RIGHT:
                if self.helpInd < 4:
                    self.helpInd += 1 # maximum is 4
                    self.screen.blit(self.helpPages[self.helpInd],(0,0))
            elif event.key == pygame.K_LEFT:
                if self.helpInd > 0:
                    self.helpInd -= 1 # minimum is 0
                    self.screen.blit(self.helpPages[self.helpInd],(0,0))
            pygame.display.update()
                
    def identifyLevel(self,event):
        if event.key == K_ESCAPE:
            self.chooseLevel()
        else:
            if 49 <= event.key <= 55:
                self.levelText = "%s" %str(event.key-48)
            if len(self.levelPage) == 3:
                low,high = eval(self.levelPage[0]),eval(self.levelPage[2])
            else:
                low = high = 7
            if event.key == K_RETURN and low <= eval(self.levelText) <= high:
                self.init(eval(self.levelText))
            elif self.levelPage == "1-3":
                self.finalLevel1_3()
            elif self.levelPage == "4-6":
                self.finalLevel4_6()


        
    
    def isGameOver(self):
        for cell in self.cellList:
            if cell.name == "ATT" and cell.color == GREEN:
                return False
        return True # Game is over

    def isWin(self):
        for cell in self.cellList:
            if cell.name == "ATT" and cell.color != GREEN:
                # one enemy survives
                return False
        return True # Win

    def timerFiredElse(self):
        if self.mode == "Choose Background":
            self.doBackground()
        elif self.mode == "Win":
            self.doWin()
        elif self.mode == "Game Over":
            self.doGameOver()
        elif self.mode == "Choose Level":
            self.chooseLevel()
        elif self.mode == "Loading":
            self.animateCount += 1
            self.fps = 22
            #print self.dealCell
            self.clock.tick(self.fps)

    ##########################################
    # What should happen after win/game over
    ##########################################

    def timerFired(self):
        if self.mode != "Running":
            self.timerFiredElse()
        if self.mode == "Running" and not self.isGameOver() and not self.isWin():
            self.animateCount += 1
            self.redrawAll()
            if self.animateCount % 58 == 0:
                self.shinex = self.shiney = None
                self.increaseValue(GREEN)
            if self.animateCount % 60 == 0:
                self.increaseValue(RED)
            if self.animateCount % 10 == 0:
                self.AIControl()
            self.fps = 22
            #print self.dealCell
            self.clock.tick(self.fps)
            self.testCollide()
            self.mousePos = pygame.mouse.get_pos()
            #manually manage the event queue
            if pygame.mouse.get_pressed()[0] == False and len(self.lineDrawn) == 3:
                self.initial = self.lineDrawn[0]
                self.recordPos = self.lineDrawn[1]
                self.lineDrawn = []
            if self.recordPos != None:
                # first judges if EMB or ATT needs to move.
               do = self.tryMoveCell()
               if do == False: # means potentially a cut
                   for chain in self.chains:
                       if chain.color == GREEN and not chain.shouldGrow:
                           # only cut friendly chain...
                           stx,sty = chain.startx,chain.starty
                           endx,endy = chain.endx,chain.endy
                           intersect = self.findIntersection(self.initial,\
                                   self.recordPos,(stx,sty),(endx,endy))
                           if intersect:
                               # that is, if there exist any intersection
                               (x0,y0) = intersect
                               breakInd = self.findBreakPoint(chain,x0,y0)
                               #print breakInd
                               chain.shouldBreak = True
                               chain.chainList[breakInd] = (0,0)
                               chain.breakInd = breakInd
                   self.recordPos = None
        if self.mode == "Running" and self.isWin(): # Win!
            self.showWin()
        if self.mode == "Running" and self.isGameOver(): # Lose!
            self.showGameOver()
                                              
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                self.mode = "Done"
            elif (event.type == pygame.MOUSEBUTTONDOWN):
                self.mousePressed(event)
            elif (event.type == pygame.KEYDOWN):
                self.keyPressed(event)

    ######################### END OF TIMERFIRED ##########################            
    ######################### END OF TIMERFIRED ##########################
    ######################### END OF TIMERFIRED ##########################

    def makeGray(self):
        for x in xrange(700):
            for y in xrange(700):
                (R,G,B,A) = self.background.get_at((x,y))
                gray = (R+G+B)/3
                self.background.set_at((x,y),(gray,gray,gray,255))
        self.grayify = True
            
    def showGameOver(self):
        self.clock.tick(self.fps)
        winImg = pygame.image.load('result4.jpg')
        self.screen.blit(winImg,(0,self.winImgy))
        font = pygame.font.SysFont("Courier",60,True)
        textObj = font.render("%d"%self.levelChosen,True,(255,255,255))
        self.screen.blit(textObj,(310,300+self.winImgy))
        if self.winImgy <= -1:
            self.winImgy += 15
        else:
            self.mode = "Game Over" # so no longer run in timerFired
            self.doGameOver()
        pygame.display.update()

    def showWin(self):
        self.clock.tick(self.fps)
        winImg = pygame.image.load('result3.jpg')
        self.screen.blit(winImg,(0,self.winImgy))
        font = pygame.font.SysFont("Courier",60,True)
        textObj = font.render("%d"%self.levelChosen,True,(255,255,255))
        self.screen.blit(textObj,(314,295+self.winImgy))
        if self.winImgy <= -1:
            self.winImgy += 15
        else:
            self.mode = "Win"
            if self.levelChosen not in self.levelCleared:
                self.levelCleared.append(self.levelChosen)
            self.doWin()
        pygame.display.update()

        

    def findBreakPoint(self,chain,x0,y0):
        for i in xrange(len(chain.chainList)):
            (dotx,doty) = chain.chainList[i]
            if dist(x0,y0,dotx,doty,3.5):
                # there must be such a point
                return i # notice: an index is returned!
    
    #########################################################################
    #########################################################################
    # Artificial Intelligence Part
    #########################################################################
    #########################################################################

    #################################################
    # Acting as if we are controlling enemy cell
    #################################################
    
    def AIControl(self):
        for cell in self.cellList:
            if cell.color != GRAY and cell.color != GREEN:
                # filter out enemy cells, excluding neutral ones.
                modifiedCellList = []
                for other in self.cellList:
                    try:
                        if other not in self.dic[cell]: # current target
                            modifiedCellList.append(other)
                    except: # meaning self.dic[cell] = -1! NO CHAIN AT ALL!
                        modifiedCellList.append(other)
                if cell.name == "ATT":
                    # feed with the latest cellList and info
                    cell.update(modifiedCellList)
                    if cell.state == "Attack":
                        self.AICellAttack(cell)
                    if cell.state == "Defense":
                        self.AICellCollapse(cell)
                        pass   ################# for now #################
                if cell.name == "EMB":
                    pass   ################# for now #################

    def AICellAttack(self,enemyCell):
        alliesList = enemyCell.alliesList
        targetList = enemyCell.allOtherList
        if self.dic[enemyCell] == -1 or len(self.dic[enemyCell]) < 2:
            # maxmimum two tentacles, by far
            target = targetList.pop(0)[2]
            # recall that what get popped out is (cell.value,cell.color,cell)
            chain = Chain(enemyCell.x,enemyCell.y,target.x,target.y,\
                          enemyCell.color)
            self.chains.append(chain) ##### important #####
            if self.dic[enemyCell] == -1:
                # newly created key, in essence
                self.dic[enemyCell] = [chain]
            else:
                # "experienced" enemy cell
                self.dic[enemyCell].append(chain)

    def AICellCollapse(self,cell):
        if self.dic[cell] != -1:
            for chain in self.dic[cell]:
                if cell.value > 4:
                    break
                if not chain.shouldGrow:
                    chain.shouldCollapse = True
            
            
        
        
                               
   
    ########################################################################
    # tryMoveCell is for moving GREEN. AIControl is for moving enemies
    ########################################################################
    def tryMoveCell(self):
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
                return True
        except:
            return False
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
                return True
                # set to None after finding once
        except:
            return False

    def findTarget(self,x,y):
        # find the closest ATT cell or EMB cell
        self.target = None
        curdist = 10000
        for cell in self.cellList:
            dist = ((cell.x-x)**2+(cell.y-y)**2)**0.5
            if dist < curdist:
                curdist = dist
                self.target = cell
        return self.target

    def playShine(self,x,y,do=False):

        if do:
            image = pygame.image.load("BOOM.png").convert_alpha()
            self.screen.blit(image,(x-90,y-64)) # Adjust the center of BOOM
        
    def isCollide(self,s1,s2):
        return dist(s1.rect.x,s1.rect.y,s2.rect.x,s2.rect.y,30)
    
    def testCollide(self):
        # test if any EMB is colliding with anything
        for cell in self.cellList:
            if cell.name == "EMB":
                for cell2 in self.cellList:
                    if cell != cell2 and dist(cell.x,cell.y,cell2.x,cell2.y,43): #collide!
                        subtract,turnColor = cell.value,cell.color
                        self.shinex,self.shiney = cell.x,cell.y
                        self.playShine(cell.x,cell.y,True)
                        self.cellList.remove(cell)
                        target = cell2
                        self.adjustValue(target,subtract,turnColor)

                    
    def adjustValue(self,cell,minus,color):
        # dropping or strengthening cell!
        delta = -1 if cell.color == color else 1
        while minus != 0 and cell.value < 100:
            cell.value -= delta
            minus -= 1
            self.redrawAll()
        if cell.value == 0:
            cell.color = GRAY
        if cell.value < 0:
            cell.color = color
            self.forceMakeCollapse(cell)
            cell.value = abs(cell.value)

    

    def increaseValue(self,color):
        for cell in self.cellList:
            if cell.color == color and cell.value < 100: #100 is a max
                if cell.name == "ATT":
                    cell.value += 1
                else:
                    cell.increaseCount += 1
                    if cell.increaseCount % 2 == 0:
                        cell.value += 1
                        cell.increaseCount = 0

    def findIntersection(self,(x1,y1),(x2,y2),(stx,sty),(endx,endy)):
        # reflect the axis
        if x2 != x1:
            l = curslope = float(y2-y1)/(x2-x1)
        elif min(stx,endx) <= x2 <= max(stx,endx) and min(y1,y2) <= \
             endy-float(endy-sty)/(endx-stx)*(x2-endx) <= max(y1,y2):
            k = float(endy-sty)/(endx-stx)
            return (x1,k*x1-k*endx+endy)
        else:
            return False
        if endx != stx:
            k = tarslope = float(endy-sty)/(endx-stx)
        elif min(x1,x2) <= stx <= max(x1,x2) and \
             min(sty,endy) <= (y1+y2)/2. <= max(sty,endy):
            l=float(y2-y1)/(x2-x1)
            return (stx,l*stx-l*x1+y1)
        else:
            return False
        if k == l: return False # parallel
        x0 = (k*endx-l*x1+y1-endy)/(k-l)
        y0 = k*x0-k*endx+endy
        if min(stx,endx) <= x0 <= max(stx,endx) and \
           min(sty,endy) <= y0 <= max(sty,endy) and \
           min(x1,x2) <= x0 <= max(x1,x2) and \
           min(y1,y2) <= y0 <= max(y1,y2):
           # in correct range
            return (x0,y0)
        else:
            return False
        
    
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
                        self.potential = cell
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
            if chain.shouldGrow and not (chain.shouldCollapse or chain.shouldBreak):
                chain.growNum += 1
                if chain.growNum % 2 == 0:
                    chain.grow()
            chain.drawChain(self.screen)

    def chainUpdate(self,cell):
        if cell.value == 1:
            for chain in self.dic[cell]:
                chain.shiningInd = []
        elif 1 < cell.value < 10:
            for chain in self.dic[cell]:
                chain.shiningInd = []
        elif 10 <= cell.value < 30:
            for chain in self.dic[cell]:
                if len(chain.shiningInd) == 2:
                    chain.shiningInd.pop()
                if len(chain.shiningInd) == 0:
                    chain.shiningInd.append(-1)
        elif 30 <= cell.value < 80:
            for chain in self.dic[cell]:
                if len(chain.shiningInd) == 1:
                    chain.shiningInd.append(chain.shiningInd[0]-18)
                elif len(chain.shiningInd) == 3:
                    chain.shiningInd.pop()
        elif cell.value >= 80: # superpower transferer for value over 80!
            for chain in self.dic[cell]:
                if len(chain.shiningInd) == 2:
                    chain.shiningInd.append(chain.shiningInd[0]-9)
                
    def traceTransfer(self):
        for cell in self.cellList:
            if cell.name == "ATT" and type(self.dic[cell]) != int:
                # meaning it is an object (i.e. a chain!)
                self.chainUpdate(cell)
                for i in xrange(len(self.dic[cell])):
                    # recall that self.dic[cell] returns the chains that "cell"
                    # currently has.
                    ###############################################################
                    # Remember to delete chains from dictionary when crossed!
                    ###############################################################
                    try:
                        currentChain = self.dic[cell][i]
                        chainEnd = self.findTarget(currentChain.endx,currentChain.endy)
                        if currentChain.shouldGrow:
                            if currentChain.subtractCellValue:
                                cell.value -= 1
                                currentChain.subtractCellValue = False
                            if cell.value == 0: # ehhh... not enough length!
                                currentChain.shouldCollapse = True
                                # so currentChain.grow() is no longer called
                        else:
                            if currentChain.shouldBreak:
                                do = self.inBreakProcess(cell,chainEnd,currentChain)
                                if do == "done":
                                    break
                            else:
                                for i in xrange(len(currentChain.shiningInd)):
                                    currentChain.shiningInd[i] += 1                        
                                    if currentChain.shiningInd[i] >= currentChain.dotNum:
                                        # one signal ends
                                        currentChain.shiningInd[i] = 5
                                        self.adjustValue(chainEnd,1,cell.color)
                                        # every signal destroys one target life value
                        if currentChain.shouldCollapse and \
                            len(currentChain.chainList) > 0:
                            currentChain.chainList.pop() # pop from the last one
                            currentChain.shiningInd = []
                            if len(currentChain.chainList)%2 == 0:
                                if currentChain.color == cell.color:
                                    cell.value += 1
                                # same rule as when subtracting
                        elif len(currentChain.chainList) == 0:
                            self.dic[cell].remove(currentChain)
                            self.chains.remove(currentChain)
                            break # avoid changing list inside a loop
                    except:
                        pass
                    #########################################################
                    # tentacles collapse back when life value drops to zero!
                    #########################################################

    def inBreakProcess(self,cell,chainEnd,currentChain):
        validLow,validHigh = self.collapseBothWays(currentChain)
        if (validLow + validHigh) % 2 == 1:
            if validHigh != 0 and chainEnd.value < 100:
                delta = -1 if chainEnd.color != cell.color else +1
                chainEnd.value += delta
                if chainEnd.value < 1:
                    chainEnd.color = cell.color
                    self.forceMakeCollapse(chainEnd)
                    chainEnd.value = abs(chainEnd.value)
            if validLow != 0 and cell.value < 100:
                cell.value += 1
            return "continue"
        elif (validLow + validHigh) == 0:
            # remove reference from current cell
            self.dic[cell].remove(currentChain)
            self.chains.remove(currentChain)
            return "done" 
    
    def forceMakeCollapse(self,cell):
        print "here"
        
        if self.dic[cell] != -1:
            for chain in self.dic[cell]:
                chain.shouldCollapse = True

    def collapseBothWays(self,chain):
        # i is the breaking point index
        tempList = list(chain.chainList)
        if chain.chainList[0] != (0,0):
            for i in xrange(chain.breakInd+1):
                if chain.chainList[i] == (0,0):
                    low = i-1
                    break
            tempList[low] = (0,0)
        else:
            low = 0
        if chain.chainList[-1] != (0,0):
            for i in xrange(len(chain.chainList)-1,chain.breakInd-1,-1):
                if chain.chainList[i] == (0,0):
                    high = i+1
                    break
            tempList[high] = (0,0)
        else:
            high = len(chain.chainList)-1
        chain.chainList = tempList
        return low,len(chain.chainList)-high-1
    
    def collapseChain(self,currentChain):
        currentChain.chainList.pop()
        currentChain.shiningInd = []
        if len(currentChain.chainList)%2 == 0:
            cell.value += 1
        
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
                cellImg = self.imageList[(self.animateCount%35)/5] if self.order else\
                          self.imageList[-(self.animateCount%31)/5 - 1]
                self.screen.blit(cellImg,(cell.x-48,cell.y-53))
            cell.drawCell(self.screen)
        try:self.playShine(self.shinex,self.shiney,True)
        except: pass
        pygame.display.flip()

    def menuInit(self):
        # The first thing that runs:
        while self.animateCount < 40:
            self.mode = "Loading"
            self.clock.tick(20)
            self.animateCount += 1
            self.screen.blit(pygame.image.load('HeadPhone.jpg'),(0,0))
            pygame.display.update()
        self.mode = "Main Menu"
        # start playing music in the mainMenu
        self.musicChannel = self.music.play(-1)
        self.menuOption = ["Play","Help","Credit","Achievement"]
        self.mainImages = [pygame.image.load('TPMenu1.jpg'),\
                           pygame.image.load('TPMenu2.jpg'),\
                           pygame.image.load('TPMenu3.jpg'),\
                           pygame.image.load('TPMenu4.jpg')]
        
        # this is for when choosing backgrounds
        self.backgroundImages = [pygame.image.load('Skyland.jpg'),\
                                 pygame.image.load('StoneAge.jpg'),\
                                 pygame.image.load('Universe.jpg')]
        
        # this is for background
        self.bgImagePool = [pygame.image.load('Skyland2.jpg'),\
                            pygame.image.load('StoneAge2.jpg'),\
                            pygame.image.load('Universe2.jpg')]
        
        self.helpPages = [pygame.image.load('help1.jpg'),\
                          pygame.image.load('help2.jpg'),\
                          pygame.image.load('help3.jpg'),\
                          pygame.image.load('help4.jpg'),\
                          pygame.image.load('help5.jpg')]
        
        self.winImages = [pygame.image.load('result31.jpg'),\
                          pygame.image.load('result32.jpg'),\
                          pygame.image.load('result33.jpg')]

        self.gameOverImages = [pygame.image.load('result41.jpg'),\
                               pygame.image.load('result42.jpg')]
        self.levelPage = "1-3"
        self.doMainMenu()

    def doMainMenu(self):
        self.mode = "Main Menu"
        self.menuNumber = 0
        self.levelCleared = [0,1]
        self.screen.blit(self.mainImages[0],(0,0))
        self.gameDisplayDepth = 1 # the depth of game, main menu is 1
        pygame.display.update()

    def doBackground(self): # of depth 2
        self.mode = "Choose Background"
        self.screen.blit(pygame.image.load('BGdefault.jpg'),(0,0))
        (x,y) = pygame.mouse.get_pos()
        if 37 <= x <= 215 and 35 <= y <= 220:
            self.bgchoice = 0
            self.screen.blit(self.backgroundImages[0],(0,0))
        elif 248 <= x <= 424 and 172 <= y <= 355:
            self.bgchoice = 1
            self.screen.blit(self.backgroundImages[1],(0,0))
        elif 480 <= x <= 652 and 322 <= y <= 500:
            self.bgchoice = 2
            self.screen.blit(self.backgroundImages[2],(0,0))
        else:
            self.bgchoice = None
        pygame.display.update()

    def doWin(self):
        self.mode = "Win"
        self.screen.blit(pygame.image.load('result3.jpg'),(0,0))
        (x,y) = pygame.mouse.get_pos()
        if 162 <= x <= 244 and 558 <= y <= 631:
            self.winchoice = 0
            self.screen.blit(self.winImages[0],(0,0))
        elif 281 <= x <= 362  and 558 <= y <= 631:
            self.winchoice = 1
            self.screen.blit(self.winImages[1],(0,0))
        elif 394 <= x <= 476 and 558 <= y <= 631:
            self.winchoice = 2
            self.screen.blit(self.winImages[2],(0,0))
        else:
            self.winchoice = None
        font = pygame.font.SysFont("Courier",60,True)
        textObj = font.render("%d"%self.levelChosen,True,(255,255,255))
        self.screen.blit(textObj,(314,295+self.winImgy))
        if self.levelChosen not in self.levelCleared:
            self.levelCleared.append(self.levelChosen)
        #print self.levelCleared
        pygame.display.update()

    def doGameOver(self):
        self.mode = "Game Over"
        self.screen.blit(pygame.image.load('result4.jpg'),(0,0))
        (x,y) = pygame.mouse.get_pos()
        if 225 <= x <= 305 and 558 <= y <= 631:
            self.gameOverchoice = 0
            self.screen.blit(self.gameOverImages[0],(0,0))
        elif 357 <= x <= 436 and 558 <= y <= 631:
            self.gameOverchoice = 1
            self.screen.blit(self.gameOverImages[1],(0,0))
        else:
            self.gameOverchoice = None
        font = pygame.font.SysFont("Courier",60,True)
        textObj = font.render("%d"%self.levelChosen,True,(255,255,255))
        self.screen.blit(textObj,(314,295+self.winImgy))
        pygame.display.update()
                        
        

    def openHelp(self):
        self.mode = "Help"
        self.helpInd = 0
        self.screen.blit(self.helpPages[self.helpInd],(0,0))
        pygame.display.update()

            
    def chooseLevel(self): # of depth 3
        self.mode = "Choose Level"
        pool = self.levelCleared + [self.levelCleared[-1]+1]
        if self.levelPage == "1-3":
            self.screen.blit(pygame.image.load('level1-3.jpg'),(0,0))
            self.doLevel1_3()
        elif self.levelPage == "4-6":
            if len(pool) > 4: #[0,1,2,3,4]
                self.screen.blit(pygame.image.load('level4-6available.jpg'),(0,0))
                self.doLevel4_6()
            else:
                self.screen.blit(pygame.image.load('level4-6unavailable.jpg'),(0,0))
                self.undoLevel4_6()
        elif self.levelPage == "7":
            if len(pool) == 8: #[0...7]
                self.screen.blit(pygame.image.load('level7available.jpg'),(0,0))
            else:
                self.screen.blit(pygame.image.load('level7unavailable.jpg'),(0,0))
        pygame.display.update()

    def doLevel1_3(self):
        (x,y) = pygame.mouse.get_pos()
        if 252 <= x <= 415 and 243 <= y <= 397:
            self.screen.blit(pygame.image.load('level1-3sun.jpg'),(0,0))
            if pygame.mouse.get_pressed()[2]:
                self.mode = "Choose Final Level"
                self.finalLevel1_3()
        elif 300 <= x <= 382 and 595 <= y <= 672:
            self.screen.blit(pygame.image.load('level1-3button.jpg'),(0,0))
            if pygame.mouse.get_pressed()[0]:
                self.menuInit()
        elif 533 <= x <= 596 and 279 <= y <= 351:
            self.screen.blit(pygame.image.load('level1-3arrow.jpg'),(0,0))
            if pygame.mouse.get_pressed()[0]:
                self.levelPage = "4-6"
        pygame.display.update()

    def finalLevel1_3(self):
        pygame.draw.rect(self.screen,(0,0,0),(0,0,700,700))
        font1 = pygame.font.SysFont("Times",50,True)
        font2 = pygame.font.SysFont("Times",28,True)
        try:text = self.levelText
        except: text = ""
        textObj1 = font1.render("Enter the level:  %s"%text,True,(255,255,255))
        self.screen.blit(textObj1,(180,350))
        tempLevelCleared = self.levelCleared + [self.levelCleared[-1]+1]
        if len(text) == 1 and ((eval(text) not in tempLevelCleared)\
           or eval(text) > 3):
            textObj2 = font2.render("Unavailable Level",True,(255,255,255))
            self.screen.blit(textObj2,(240,480))
        pygame.display.update()
                   

    def doLevel4_6(self):
        (x,y) = pygame.mouse.get_pos()
        if 87 <= x <= 154 and 279 <= y <= 355:
            self.screen.blit(pygame.image.load('level4-6available1.jpg'),(0,0))
            if pygame.mouse.get_pressed()[0]:
                self.levelPage = "1-3"
                self.chooseLevel()
        elif 252 <= x <= 415 and 243 <= y <= 397:
            # choose one of 4-6
            self.screen.blit(pygame.image.load('level4-6available3.jpg'),(0,0))
            if pygame.mouse.get_pressed()[2]:
                self.mode = "Choose Final Level"
                self.finalLevel4_6()
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            self.screen.blit(pygame.image.load('level4-6available2.jpg'),(0,0))
            if pygame.mouse.get_pressed()[0]:
                self.menuInit()
        elif 533 <= x <= 596 and 279 <= y <= 351:
            self.screen.blit(pygame.image.load('level4-6available4.jpg'),(0,0))
            if pygame.mouse.get_pressed()[0]:
                self.levelPage = "7"
        pygame.display.update()

    def finalLevel4_6(self):
        pygame.draw.rect(self.screen,(0,0,0),(0,0,700,700))
        font1 = pygame.font.SysFont("Times",50,True)
        font2 = pygame.font.SysFont("Times",28,True)
        try:text = self.levelText
        except: text = ""
        textObj1 = font1.render("Enter the level:  %s"%text,True,(255,255,255))
        self.screen.blit(textObj1,(180,350))
        tempLevelCleared = self.levelCleared + [self.levelCleared[-1]+1]
        if len(text) == 1 and ((eval(text) not in tempLevelCleared)\
           or eval(text) > 6 or eval(text) < 4):
            textObj2 = font2.render("Unavailable Level",True,(255,255,255))
            self.screen.blit(textObj2,(240,480))
        pygame.display.update()

    def undoLevel4_6(self):
        (x,y) = pygame.mouse.get_pos()
        if 87 <= x <= 154 and 280 <= y <= 352:
            image = pygame.image.load('level4-6unavailable1.jpg')
            self.screen.blit(image,(0,0))
            if pygame.mouse.get_pressed()[0]:
                # choose the level again
                self.levelPage = "1-3"
                self.chooseLevel()
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            image = pygame.image.load('level4-6unavailable2.jpg')
            self.screen.blit(image,(0,0))
            if pygame.mouse.get_pressed()[0]:
                self.menuInit()
        pygame.display.update()
            
        

    def runMenuOption(self,option): # choosing at depth 1
        if option == "Play":
            # Should choose level first
            self.doBackground()
            self.gameDisplayDepth += 1            
        elif option == "Help":
            self.openHelp()
            self.gameDisplayDepth = 2
        elif option == "Credit":
            pass
        elif option == "Achievement":
            pass


                            
        

    def init(self,level): # level as a number
        self.mode = "Running"
        self.winImgy = -700
        self.bgimage = self.bgImagePool[self.bgchoice]
        self.gameDisplayDepth = 4
        self.imageList = [pygame.image.load('GreenCell4.png'),\
                     pygame.image.load('GreenCell9.png'),\
                     pygame.image.load('GreenCell6.png'),\
                     pygame.image.load('GreenCell8.png'),\
                     pygame.image.load('GreenCell5.png'),\
                     pygame.image.load('GreenCell7.png'),\
                     pygame.image.load('GreenCell3.png'),]
        # set self.animateCount to zero again
        self.animateCount,self.count = 0,0 
        self.potential = None # potential target pointing at
        # self.animateCount is for animation image use
        self.lineDrawn,self.grayify = [],False # should we make bg gray?
        self.recordPos = None # a temporary position recorder
        self.order = True # left to right
        self.levelList = [Level_1(),Level_2(),Level_3(),Level_4(),Level_5()]
        self.levelChosen = level
        self.cellList = self.levelControl(self.levelList[level-1])
        #self.block_list = pygame.sprite.Group()
        self.chains = []
        self.connections = [] # record which chain has been established.
        self.dic = dict() # same as above, to record.
        ##################################################################
        # temporarily, self.connections is kept, but currently of no use.
        ##################################################################
        for cell in self.cellList:
            cell.sprite = Target()
            cell.sprite.rect.x = cell.x-cell.radius
            cell.sprite.rect.y = cell.y-cell.radius
            #self.block_list.add(cell.sprite)
            if cell.name == "ATT":
                self.dic[cell] = -1 # by default
        self.redrawAll()

    def levelControl(self,level): # which level?
        return level.cellList
    
    def run(self):
        pygame.mixer.pre_init(44010,16,2,4096) # setting the music environment
        pygame.init()
        self.music = pygame.mixer.Sound("Fabrizio.wav")
        
        # initialize the screen
        self.screenSize = (700,700)
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("Tentacle Wars")
        
        # initialize clock
        self.clock = pygame.time.Clock()
        # the cell we are dealing with
        self.dealCell = "ATT"
        self.animateCount = 0
        self.menuInit()
        while (self.mode != "Done"):
            self.timerFired()  ######################### HERE ########################

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
                
class Target(pygame.sprite.Sprite):
    """ Fake cells to test collision"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprite.jpg").convert()

        self.rect = self.image.get_rect()
    

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

    def drawCell(self,surface):
        center = (self.x,self.y)
        pygame.draw.circle(surface,(255,255,255),center,self.outerRadius,2)
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
                

    def think(self,environment):
        # the thinking process refers to the AI
        #####################################################################
        #     Later possibly use value drop in time also to determin. For
        # instance, consider d(C.V.)/dt
        #####################################################################
        enemyAvg = self.findEnemiesWithinDistance(environment)
        allyAvg = self.findAllies(environment)
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

    def update(self,environment):
        # update every aspect: camp, current mode, etc.
        # ONLY ENEMY CELL NEEDS TO UPDATE.
        self.think(environment) # change mode,find friends,find enemies
            
        

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
        if endx != startx:
            self.tan = float(starty-endy)/(endx-startx)
            if self.tan > 0:
                self.direction = math.atan(self.tan)
                if starty < endy:
                    self.direction += math.pi
            else:
                self.direction = math.atan(self.tan)+math.pi
                if startx < endx:
                    self.direction += math.pi
        else:
            self.direction = math.pi/2 if starty > endy else 3*math.pi/2
        self.chainFinalLen = ((endx-startx)**2+(endy-starty)**2)**0.5
        self.dotNum = (self.chainFinalLen-23)/(3*2) # 23 is cell radius
        # 3 is the radius of the small dot,so 3*2 is the diameter
        self.chainInit = 1 # initially of length (dot) 1.
        self.chainList = [(startx,starty)]
        self.shouldBreak,self.breakInd = False,None
        self.shouldCollapse = False
        self.shouldGrow = True # at first, every chain should grow
        self.growNum = 0 # to control the speed of the growth
        self.lineHalfLength = 5.5
        self.subtractCellValue = False # growing chain costs life value
        self.shiningInd = [-1,-19] # the dot on the chain that shines
        # two dots have distance difference of 18
    
    def grow(self):
        startx = self.chainList[-1][0]
        starty = self.chainList[-1][1]
        newx = startx + 6*math.cos(self.direction)
        newy = starty - 6*math.sin(self.direction)
        self.chainList.append((newx,newy))
        if len(self.chainList)%2 == 0: # two dots worth one life value of cell
            self.subtractCellValue = True
        if dist(newx,newy,self.endx,self.endy,1):
            self.shouldGrow = False
            self.subtractCellValue = False

    def drawChain(self,surface):
        length = self.lineHalfLength
        angle = self.direction
        for i in xrange(len(self.chainList)):
            dot = self.chainList[i]
            dotx = int(round(dot[0]))
            doty = int(round(dot[1]))
            color = self.color
            for index in self.shiningInd:
                if index == i:
                    color = (255,255,0)
                    break
                    
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


my_CellWar = CellWar()
my_CellWar.run()

##############################################
# 1. Tentacles in curly and wavy fashion?
# 2. Draw Ghost Embracer?
# 3. Possibly a gradient effect for cell?
