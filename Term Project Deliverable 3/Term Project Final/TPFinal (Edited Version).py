# Barebones timer, mouse, and keyboard events

import pygame
from pygame.locals import *
import random
import math
import pickle
import time
from creditPage import displayCredit

GREEN = (47,171,51)
RED = (200,0,0)
GRAY = (55,55,55)
WHITE = (255,255,255)
WARMYELLOW = (255,255,85)

class CellWar(object):
    def __init__(self):
        # For statistics and achievement page purpose
        self.gamesPlayed = 0
        self.loses = 0
        self.enemyKilled = 0
        self.needleLeft = 3
        self.totalMerge = 0
        self.totalAssist = 0
        self.achievement = [self.gamesPlayed,self.loses,self.enemyKilled,\
                         self.needleLeft,self.totalMerge,self.totalAssist]
        self.fadeTime = 3000 # music fadeout time

    def saveLoad(self):
        self.achievement = [self.gamesPlayed,self.loses,self.enemyKilled,\
                         self.needleLeft,self.totalMerge,self.totalAssist]
        outFile1 = open('myLevelCleared.txt','wb')
        outFile2 = open('myAchievement.txt','wb')
        pickle.dump(self.levelCleared,outFile1)
############################ MAKE ACHIEVEMENT ###############################
############################ HIGH SCORE?? ###############################
        pickle.dump(self.achievement,outFile2)
        outFile1.close()
        outFile2.close()

    def readFile(self):
        inFile1 = open('myLevelCleared.txt','rb')
        inFile2 = open('myAchievement.txt','rb')
        self.levelCleared = pickle.load(inFile1)
        self.achievement = pickle.load(inFile2)
        [self.gamesPlayed,self.loses,self.enemyKilled,self.needleLeft,\
         self.totalMerge,self.totalAssist] = self.achievement

    ###################################################
    # SAVE AND LOAD PREVIOUS RECORD! IMPORTANT!
    ###################################################
    
    def mousePressed(self,event):
        if self.mode == "Running" or self.mode == "Tutorial":
            self.recordPos = None # refresh everytime with NEW click
            needlex,needley,imagex,imagey = 647,643,700,700
            x,y = self.mousePos
            if self.needleMode: # mouse is a needle now
                self.findInjectedCell((x,y))
                return
            if needlex <= x <= imagex and needley <= y <= imagey:
                self.mouseFigure = self.needleImg
                self.needleMode = True
                return
            self.lineDrawn = [(x,y),(x,y),False]
            for cell in self.cellList:
                if cell.color == GREEN:
                    if dist(x,y,cell.x,cell.y,cell.radius):
                        self.lineDrawn = [(cell.x,cell.y),(cell.x,cell.y),True]
                        self.dealCell = cell
                        break
            self.redrawAll()
        else:
            self.mouseOtherMode(event)

    def mouseOtherMode(self,event):
        if self.mode == "Choose Background":
            if self.bgchoice != None: # such that the choice is valid
                self.background = self.backgroundImages[self.bgchoice]
                pygame.mixer.Sound('Confirm.wav').play(0)
                self.mode = "Choose Level"
        elif self.mode == "Game Over":
            self.gameOverChoices(event)
        elif self.mode == "Win":
            self.winChoices(event)
        elif self.mode == "Choose Level":
            self.identifyLevelImg(event)
        #print "Mouse Pressed"

    def gameOverChoices(self,event):
        if self.gameOverchoice != None:
            self.gamesPlayed += 1
            self.loses += 1
            if self.gameOverchoice == 0:
                self.chooseLevel()
            elif self.gameOverchoice == 1:
                self.init(self.levelChosen)

    def winChoices(self,event):
        if self.winchoice != None:
            self.gamesPlayed += 1
            if self.levelChosen >= 4: self.needleLeft += 1
            #Completing level 4 or above get a needle award
            if self.winchoice == 0:
                self.chooseLevel()
            elif self.winchoice == 1:
                self.init(self.levelChosen)
            elif self.winchoice == 2: # click the third button
                self.levelCleared = range(self.levelChosen+1)
                totalLevel = 7
                if self.levelChosen != totalLevel:
                    self.levelChosen += 1
                    self.init(self.levelChosen)
                else:
                    self.doMainMenu()

    def identifyLevelImg(self,event):
        (x,y) = pygame.mouse.get_pos()
        if self.levelPage == "1-3":
            if 252 <= x <= 415 and 243 <= y <= 397:
                self.mode = "Choose Final Level"
                self.finalLevel1_3()
            elif 300 <= x <= 382 and 595 <= y <= 672:
                self.doMainMenu()
            elif 533 <= x <= 596 and 279 <= y <= 351:
                self.levelPage = "4-6"
                self.chooseLevel()
        elif self.levelPage == "4-6":
            prereqLength = 3
            if len(self.levelCleared[1:]) >= prereqLength:
                self.actLevel4_6(x,y)
            else:
                self.unactLevel4_6(x,y)
        else:
            prereqLength = 6
            if len(self.levelCleared[1:]) >= prereqLength:
                self.actLevel7(x,y)
            else:
                self.unactLevel7(x,y)



            
    def keyPressed(self,event):
        print "Key Pressed"
        totalLevel = 7
        if self.mode == "Running":
            if event.key == pygame.K_q:
                level = self.levelChosen
                if level not in self.levelCleared:
                    self.levelCleared.append(self.levelChosen)
                if level < totalLevel:
                    self.music.fadeout(self.fadeTime)
                    self.gamesPlayed += 1
                    self.init(level+1)
        if event.key == pygame.K_s:
            self.saveLoad()
        elif event.key == pygame.K_SPACE:
            self.readFile()
        elif event.key == pygame.K_p:
            print self.levelCleared
        elif event.key == pygame.K_m:
            self.doMainMenu() # for demo purpose, go back to main menu
            self.music.fadeout(self.fadeTime)
        self.keyPressedModeJudge(event)

    def keyPressedModeJudge(self,event):
        # different keyPress functions in different mode!
        if self.mode == "Main Menu":
            self.mainMenuKey(event)            
        elif self.mode == "Choose Background":
            print "Use your mouse to choose!"
        elif self.mode == "Choose Final Level":
            self.identifyLevel(event)
        elif self.mode == "Achievement":
            self.identifyAchievementPage(event)
        elif self.mode == "Credit":
            if event.key == pygame.K_r:
                self.doMainMenu()
        elif self.mode == "Help":
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

    def mainMenuKey(self,event):
        sound = pygame.mixer.Sound('Thip.wav')
        if event.key == pygame.K_DOWN:
            self.menuNumber += 1
            sound.play(0)
        elif event.key == pygame.K_UP:
            self.menuNumber -= 1
            sound.play(0)
        elif event.key == pygame.K_RETURN:
            self.runMenuOption(self.menuOption[self.menuNumber])
        self.menuNumber %= len(self.menuOption)
        if self.gameDisplayDepth == 1: # on main menu
            self.screen.blit(self.mainImages[self.menuNumber],(0,0))
            pygame.display.update()
                
    def identifyLevel(self,event):
        if event.key == K_r:
            self.chooseLevel()
        else:
            diff,totalLevel,fullLevelPage = 48,7,3
            if diff <= event.key <= diff+totalLevel:
                # account for 'unicode' in pygame
                self.levelText = "%s" %str(event.key-diff)
            if len(self.levelPage) == fullLevelPage:
                low,high = eval(self.levelPage[0]),self.levelCleared[-1]+1
            else:
                low = high = totalLevel
            if event.key == K_RETURN and len(self.levelText) == 1 and \
               low <= eval(self.levelText) <= high :
                self.init(eval(self.levelText))
            elif self.levelPage == "1-3":
                self.finalLevel1_3()
            elif self.levelPage == "4-6":
                self.finalLevel4_6()

    def identifyAchievementPage(self,event):
        if event.key == K_r:
            self.doMainMenu()
            return
        if self.achichoice == 0:
            if event.key == K_RIGHT:
                self.achichoice = 1
        elif self.achichoice == 1:
            if event.key == K_LEFT:
                self.achichoice = 0
        self.displayAchi()
        


        
    
    def isGameOver(self):
        for cell in self.cellList:
            if cell.name == "ATT" and cell.color == GREEN:
                return False
        return True # Game is over

    def isWin(self):
        for cell in self.cellList:
            if cell.name == "ATT" and cell.color != GREEN and cell.color != GRAY:
                # one enemy survives
                return False
        return True # Win

    def timerFiredElse(self):
        if self.mode == "Choose Background":
            self.doBackground()
        elif self.mode == "Credit":
            self.animateCount += 1
            self.runCredit()
        elif self.mode == "Achievement":
            self.displayAchi()
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

    
    def findInjectedCell(self,(x,y)):
        adjust = 20*math.sqrt(2) # the adjusted position of x and y
        for cell in self.cellList:
            if dist(cell.x,cell.y,x-adjust,y+adjust,30):
                if self.needleLeft > 0:
                    cell.getNeedle = True
                    self.needleLeft -= 1
                break
        self.needleMode = False

    def doInjection(self):
        maxInjectTime = 30
        for cell in self.cellList:
            if cell.getNeedle:
                cell.injectTime += 1
                if cell.injectTime <= maxInjectTime:
                    if cell.color == GREEN and cell.value < self.maximum:
                        cell.value += 1
                    else:
                        cell.value -= 1
                        if cell.value < 0: # turn to GREEN!
                            if cell.color == GRAY:
                                cell.value = 20
                            else:
                                cell.value = abs(cell.value)
                                self.forceMakeCollapse(cell)
                                self.enemyKilled += 1
                            cell.color = GREEN
                    #self.drawBubbleEffect(cell.x,cell.y)
                else:
                    cell.getNeedle = False
                    cell.injectTime = 0

    def doTimeAdjust(self):
        if self.mode == "Tutorial":
            self.displayTut()
        if self.animateCount % 58 == 0:
            self.shinex = self.shiney = None
            self.increaseValue(GREEN)
        if self.animateCount % 60 == 0:
            self.increaseValue(RED)
        if self.animateCount % 10 == 0 and self.mode == "Running":
            # No AI in tutorial
            self.AIControl()

    def doTimeThing(self):
        # do every time in timerFired()
        self.animateCount += 1
        self.doInjection()
        self.redrawAll()
        self.doTimeAdjust()            
        if self.AIEMB != None and self.mode == "Running":
            self.tryMoveAIEMB()
        if self.animateCount < 140:
            if self.levelChosen == 2:
                self.level2Text()
            elif self.levelChosen == 4:
                self.level4Text()
            elif self.levelChosen == 6:
                self.level6Text()
            elif self.levelChosen == 7:
                self.level7Text()
        self.fps = 22
        #print self.dealCell
        self.clock.tick(self.fps)
        self.testCollide()


    def level2Text(self):
        if self.animateCount < 60:
            note = "Welcome to level 2. You know how to control, now try!"
        else:
            note = "The GRAY cell is neutral. Enjoy!"
        font = pygame.font.SysFont("Calibri",20,True)
        textObj = font.render("%s" %note,True,(255,255,255))
        self.screen.blit(textObj,(80,160))
        pygame.display.flip()

    def level4Text(self):
        if self.animateCount < 40:
            note = "Now, the computer AI is getting smarter for level above!"
        elif 40 <= self.animateCount < 100:
            note = "Computer can also assist its own allies!"
        else:
            note = "Enjoy!"
        font = pygame.font.SysFont("Calibri",20,True)
        textObj = font.render("%s" %note,True,(255,255,255))
        self.screen.blit(textObj,(100,60))
        pygame.display.flip()

    def level6Text(self):
        if self.animateCount < 40:
            note = "Why not try some geometry?"
        elif 40 <= self.animateCount < 100:
            note = "The enemy is now surrounded! Assimilate it!"
        else:
            note = "Enjoy!"
        font = pygame.font.SysFont("Calibri",20,True)
        textObj = font.render("%s" %note,True,(255,255,255))
        self.screen.blit(textObj,(120,60))
        pygame.display.flip()

    def level7Text(self):
        if self.animateCount < 40:
            note = "Congrats! You have reached the FINAL CHALLENGE!"
        elif 40 <= self.animateCount < 100:
            note = "There are three camps of cells now. Do your best to win!"
        else:
            note = "Enjoy!"
        font = pygame.font.SysFont("Calibri",20,True)
        textObj = font.render("%s" %note,True,(255,255,255))
        self.screen.blit(textObj,(120,60))
        pygame.display.flip()

    def displayTut(self):
        if self.animateCount < 50:
            welcome = "Welcome to Tentacle World..."
            font = pygame.font.SysFont("Calibri",20,True)
            textObj = font.render("%s" %welcome,True,(255,255,255))
            self.screen.blit(textObj,(50,100))
        else:
            if 50 <= self.animateCount < 120:
                self.tutorialStep = 2
                caption = "The values on cells are their life values."
                font = pygame.font.SysFont("Calibri",20,True)
                textObj = font.render("%s" %caption,True,(255,255,255))
                self.screen.blit(textObj,(50,100))                
            elif self.animateCount >= 120:
                if self.tutorialStep == 2: self.tutorialStep += 1
                self.doTutorial()                      
            
        pygame.display.flip()



    def doTutorial(self):
        font = pygame.font.SysFont("Calibri",18,True)
        if self.tutorialStep == 3:
            caption1 = "Now, use your mouse to click your cell(GREEN) with tentacle."
            caption2 = "DRAG to the other cell. Wait for the tentacle"
            caption3 = "growth to complete."
            capList = [caption1,caption2,caption3]
            cellx,celly = 400,400
            Lock(cellx,celly).drawLock(self.screen)
        elif self.tutorialStep == 4:
            caption1 = "Good. You can now see the signal is being transported."
            caption2 = "Now, drag-click the mouse and cut the tentacle, and"
            caption3 = "see what happens."
            capList = [caption1,caption2,caption3]
        elif self.tutorialStep == 5:
            caption1 = "Indeed, cutting the tentacle breaks the tentacle into"
            caption2 = "two parts.Each part 'collapses' to one of the ends."
            caption3 = "How much collpase to the target cell is determined "
            caption4 = "by the location of your cutting. Now, feel free to try"
            caption5 = "the EMB cell. It has no tentacle. Try move anywhere"
            caption6 = "you want, then let it collide with the enemy cell."
            capList = [caption1,caption2,caption3,caption4,caption5,caption6]
            if self.findTutEMB() != None:
                cellx,celly = self.findTutEMB()
                Lock(cellx,celly).drawLock(self.screen)
        elif self.tutorialStep == 6:
            caption1 = "Great! Now try to use the needle at the bottom right"
            caption2 = "to eliminate the enemy left. You can earn a new"
            caption3 = "needle when you complete Level 4 or above."
            caption4 = "Finally, press 's' at any time to save your"
            caption5 = "game progress, and press 'space' to load!"
            capList = [caption1,caption2,caption3,caption4,caption5]
        for i in xrange(len(capList)):
                text = font.render("%s"%(capList[i]),True,WHITE)
                self.screen.blit(text,(50,100+25*i))      
        pygame.display.flip()

    def findTutEMB(self):
        for cell in self.cellList:
            if cell.name == "EMB" and cell.color == GREEN:
                return cell.x,cell.y
        return None
        

                        

    ##########################################
    # What should happen after win/game over
    ##########################################

    def timerFired(self):
        if self.mode != "Running":
            self.timerFiredElse()
        if (self.mode == "Running" or self.mode == "Tutorial")\
           and not self.isGameOver() and not self.isWin():
            self.doTimeThing()
            self.mousePos = pygame.mouse.get_pos()
            #manually manage the event queue
            if pygame.mouse.get_pressed()[0] == False and\
               len(self.lineDrawn) == 3:
                self.initial = self.lineDrawn[0]
                self.recordPos = self.lineDrawn[1]
                self.lineDrawn = []
            if self.recordPos != None:
                # first judges if EMB or ATT needs to move.
                
                do = self.tryMoveCell()
                if do == False: # means potentially a cut
                    self.tryConsiderCut()
                    self.recordPos = None
        if self.mode == "Running" or self.mode == "Tutorial":
            if self.isWin(): # Win!
                self.showWin()
        if self.mode == "Running" or self.mode == "Tutorial":
            if self.isGameOver(): # Lose!
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

    def tryConsiderCut(self):
        for chain in self.chains:
            if chain.color == GREEN and not chain.shouldGrow and\
               not chain.shouldCollapse:
                # only cut friendly chain...
                stx,sty = chain.startx,chain.starty
                endx,endy = chain.endx,chain.endy
                intersect = self.findIntersection(self.initial,\
                        self.recordPos,(stx,sty),(endx,endy))
                if intersect:
                    # that is, if there exist any intersection
                    (x0,y0) = intersect
                    breakInd = self.findBreakPoint(chain,x0,y0)
                    chain.shouldBreak = True
                    try:
                        chain.chainList[breakInd] = (0,0)
                        chain.breakInd = breakInd
                    except:
                        pass
                    if self.mode == "Tutorial":
                        self.tutorialStep = 5

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
            self.winImgy += 25
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
            self.winImgy += 25
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
    # Artificial Intelligence Part (Finite State Machine)
    #########################################################################
    #########################################################################

    #################################################
    # Acting as if we are controlling enemy cell
    #################################################

    def testCellInList(self,cell,L):
        # test if a cell is in a list (of chains) as a target
        for i in xrange(len(L)):
            chain = L[i]
            if dist(chain.endx,chain.endy,cell.x,cell.y,5):
                return True
        return False
    
    def AIControl(self):
        level = self.levelChosen
        for cell in self.cellList:
            do = random.randint(1,2) 
            # not move in every round, but just some (1/2 probability)
            if cell.color != GRAY and cell.color != GREEN and do == 1:
                # filter out enemy cells, excluding neutral ones.
                modifiedCellList = []
                for other in self.cellList:
                    try:
                        if not self.testCellInList(other,self.dic[cell]) and\
                           other.x != cell.x:
                            # current target
                            modifiedCellList.append(other)
                    except: # meaning self.dic[cell] = -1! NO CHAIN AT ALL!
                        modifiedCellList.append(other)
                if cell.name == "ATT":
                    # feed with the latest cellList and info
                    cell.update(modifiedCellList,self.animateCount)
                    if cell.state == "Attack":
                        self.AICellAttack(cell)
                    elif cell.state == "Defense":
                        self.AICellCollapse(cell)
                        pass   ################# for now #################
                    elif cell.state == "Attack and Assist" and level > 3:
                        self.AIAssist(cell)
                if cell.name == "EMB":
                    judge = random.randint(1,10)
                    if 1 <= judge <= 3:
                        cell.update(modifiedCellList,self.animateCount)
                        self.AIEMBcontrol(cell)
                    else:
                        pass

    def AIEMBcontrol(self,cell):
        # for EMB only
        targetList = cell.allOtherList
        if cell.state == "Attack":
            target = targetList.pop(0)[2]
            self.AIEMB = (cell,target)
            self.tryMoveAIEMB()

    def tryMoveAIEMB(self):
        cell = self.AIEMB[0]
        target = self.AIEMB[1]
        subtractMoves = 14
        if not dist(cell.x,cell.y,target.x,target.y,0.5):
                    # not yet at the destination
            cell.moveJudge = True
            cell.move(target.x,target.y,self.fps)
            if self.animateCount % subtractMoves == 0:
                cell.value -= 1
        else:
            self.AIEMB = None

    def AIShrinkTent(self,cell):
        for i in xrange(2):
            chain = self.dic[cell][i]
            chainEnd = self.findTarget(chain.endx,chain.endy)
            if chainEnd.color == GREEN or chainEnd.color.color ==GRAY:
                chain.shouldCollapse = True
                break # only break one of the tentacles

    def AIAssist(self,cell):
        alliesList = cell.alliesList
        try:
            emergency = cell.findEmergencyCell()
            emergency.withHelp = False
            # by default. It tells us if there is any existing help
            for allyInfo in alliesList:
                ally = allyInfo[2]
                if self.dic[ally] != -1:
                    for i in xrange(len(self.dic[ally])):
                        chain = self.dic[ally][i]
                        if dist(chain.endx,chain.endy,emergency.x,emergency.y,5):
                            emergency.withHelp = True
            if not emergency.withHelp:
                if len(self.dic[cell]) == 2:
                    self.AIShrinkTent(cell)
                if self.dic[cell] == -1 or len(self.dic[cell]) < 2:
                    target = emergency
                    # establish a chain between cell and the emergency cell
                    self.noRepeatChain(target,cell)
                    chain = Chain(cell.x,cell.y,target.x,target.y,cell.color)
                    self.chains.append(chain)
                    if self.dic[cell] == -1:
                        # newly created key, in essence
                        self.dic[cell] = [chain]
                    else:
                        # "experienced" enemy cell
                        self.dic[cell].append(chain)
            else:
                self.AICellAttack(cell)
        except:
            pass
                                                
                        

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
        minimumValue = 6
        if self.dic[cell] != -1:
            for chain in self.dic[cell]:
                if cell.value > minimumValue:
                    break
                if not chain.shouldGrow:
                    chain.shouldCollapse = True
            
            
            
                               
   
    ########################################################################
    # tryMoveCell is for moving GREEN. AIControl is for moving enemies
    ########################################################################
    def tryMoveCell(self):
        try:
            if self.dealCell.name == "EMB":             
                self.tryMoveEMB()
                return True
        except:
            return False
        try:
            if self.dealCell.name == "ATT":
                self.tryMoveATT()
                return True
                # set to None after finding once
        except:
            return False

    def tryMoveATT(self):
        for cell in self.cellList:
            if cell.name == "ATT" and \
                (cell.x,cell.y) != (self.dealCell.x,self.dealCell.y):
                if dist(self.recordPos[0],self.recordPos[1],cell.x,\
                        cell.y,cell.radius):
                    chain = Chain(self.dealCell.x,self.dealCell.y,\
                                cell.x,cell.y,self.dealCell.color)
                    self.testAddAssist(chain)
                    self.chains.append(chain)
                    if self.mode == "Tutorial":
                        self.tutorialStep = 4
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

    def tryMoveEMB(self):
        cycle = 14
        if not dist(self.dealCell.x,self.dealCell.y,\
                   self.recordPos[0],self.recordPos[1],0.5):
        # not yet at the destination
            self.dealCell.moveJudge = True
            self.dealCell.move(self.recordPos[0],\
                                self.recordPos[1],self.fps)
            if self.animateCount % cycle == 0:
                self.dealCell.value -= 1
        else:
            tutMoveEMBStep = 5
            if self.mode == "Tutorial":
                if self.tutorialStep == tutMoveEMBStep:
                    self.tutorialStep += 1
            self.recordPos = None
            self.dealCell = None

    def testAddAssist(self,chain): # test if self.totalAssist should add 1
        chainEnd = self.findTarget(chain.endx,chain.endy)
        self.noRepeatChain(chainEnd,self.dealCell)
        if chainEnd.value <= 10 and chainEnd.color == GREEN:
            if self.dic[chainEnd] != -1:
                for chain in self.dic[chainEnd]:
                    if chain.shouldGrow:
                        return
            self.totalAssist += 1

    def noRepeatChain(self,chainEnd,startCell):
        if self.dic[chainEnd] != -1 and chainEnd.color == startCell.color:
            # consider repetitive only if the same color
            for back in self.dic[chainEnd]:
                if self.findTarget(back.endx,back.endy) == startCell:
                    back.shouldCollapse = True
                    break # make sure no transport in 2 directions
                
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
                        self.totalMerge += 1
                        bounce = pygame.mixer.Sound("bounce.wav")
                        bounce.set_volume(80)
                        bounce.play(0)
                        target = cell2
                        self.adjustValue(target,subtract,turnColor)
                        cell.value = abs(cell.value)

                    
    def adjustValue(self,cell,minus,color):
        # dropping or strengthening cell!
        delta = -1 if cell.color == color else 1
        while minus != 0 and cell.value < self.maximum:
            cell.value -= delta
            minus -= 1
            self.redrawAll()
            if cell.value < 0:
                if cell.color == GRAY:
                    cell.value = 10 # bonus value for neutral occupy!
                else:
                    if cell.name == "ATT":
                        self.forceMakeCollapse(cell)
                    cell.value = abs(cell.value)
                    if cell.color == RED:
                        self.enemyKilled += 1
                cell.color = color
                delta = -1

    

    def increaseValue(self,color):
        for cell in self.cellList:
            if cell.color == color and cell.value < self.maximum: #9 is a max
                if cell.name == "ATT":
                    cell.value += 1
                else:
                    cell.increaseCount += 1
                    if cell.increaseCount % 2 == 0:
                        cell.value += 1
                        cell.increaseCount = 0

    def findIntersection(self,(x1,y1),(x2,y2),(stx,sty),(endx,endy)):
        # reflect the axis, and using mathematical method to find the slope
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
        # draw the yellow line by tracing the position of the mouse
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
        # determine the frequency of transporting based on source cell value
        if cell.value == 1:
            for chain in self.dic[cell]:
                chain.shiningInd = []
                chain.freq = 40
        elif 1 < cell.value < 15:
            for chain in self.dic[cell]:
                if len(chain.shiningInd) != 1:
                    chain.shiningInd = [-1]
                chain.freq = 25
        elif 15 <= cell.value < 35:
            for chain in self.dic[cell]:
                if len(chain.shiningInd) == 1:
                    chain.determineInd()
                chain.freq = 15
        elif 35 <= cell.value < 80:
            for chain in self.dic[cell]:
                if len(chain.shiningInd) == chain.IndNum:
                    chain.shiningInd.append(min(chain.shiningInd)-13)
                chain.freq = 10
                
    def traceTransfer(self):
        for cell in self.cellList:
            if cell.name == "ATT" and type(self.dic[cell]) != int:
                # meaning it is an object (i.e. a chain!)
                self.chainUpdate(cell)
                for i in xrange(len(self.dic[cell])):
                    # recall that self.dic[cell] returns the chains that "cell"
                    # currently has.
                    try:
                        currentChain = self.dic[cell][i]
                        chainEnd = self.findTarget(currentChain.endx,currentChain.endy)
                        if currentChain.shouldGrow:
                            self.doChainGrow(currentChain,cell)
                        else:
                            if currentChain.shouldBreak:
                                do = self.inBreakProcess(cell,chainEnd,currentChain)
                                if do == "done":
                                    break
                            else:
                                self.doCompleteChain(currentChain,cell,chainEnd)
                        if currentChain.shouldCollapse and \
                            len(currentChain.chainList) > 0:
                            self.doingCollapse(currentChain,cell)
                        elif len(currentChain.chainList) == 0:
                            self.dic[cell].remove(currentChain)
                            self.chains.remove(currentChain)
                            break # avoid changing list inside a loop
                    except:
                        pass

    def doingCollapse(self,currentChain,cell):
        currentChain.chainList.pop() # pop from the last one
        currentChain.shiningInd = []
        if len(currentChain.chainList)%2 == 0:
            if currentChain.color == cell.color and cell.value < self.maximum:
                cell.value += 1
            # same rule as when subtracting
        

    def doChainGrow(self,currentChain,cell):
        if currentChain.subtractCellValue:
            cell.value -= 1
            currentChain.subtractCellValue = False
        if cell.value == 0: # ehhh... not enough length!
            currentChain.shouldCollapse = True
            # so currentChain.grow() is no longer called

    def doCompleteChain(self,currentChain,cell,chainEnd):
        for i in xrange(len(currentChain.shiningInd)):
            currentChain.shiningInd[i] += 1                        
            if currentChain.shiningInd[i] >= currentChain.dotNum:
                # one signal ends
                delta = -1 if chainEnd.color == cell.color else 1
                if chainEnd.value < self.maximum:
                    chainEnd.value -= delta
                if chainEnd.value < 0:
                    if chainEnd.color == GRAY:
                        chainEnd.value = 10
                    else:
                        self.enemyKilled += 1
                        self.forceMakeCollapse(chainEnd)
                    chainEnd.color = cell.color
                    chainEnd.value = abs(chainEnd.value)
                currentChain.shiningInd[i] = 5-currentChain.freq
                    # every signal destroys one target life value
        

    def inBreakProcess(self,cell,chainEnd,currentChain):
        grayBonus = 10
        validLow,validHigh = self.collapseBothWays(currentChain)
        if max(validLow,validHigh) % 2 == 1: # for every two round, value drops
            if validHigh != 0 and chainEnd.value < self.maximum:
                delta = -1 if chainEnd.color != cell.color else +1
                chainEnd.value += delta
                if chainEnd.value < 1:
                    if chainEnd.color == GRAY:
                        chainEnd.value = grayBonus # bonus for gray!
                    else:
                        self.forceMakeCollapse(chainEnd)
                        self.enemyKilled += 1
                        chainEnd.value = abs(chainEnd.value)
                    chainEnd.color = cell.color                    
            if validLow != 0 and cell.value < self.maximum:
                cell.value += 1
            return "continue"
        elif (validLow + validHigh) == 0:# remove reference from current cell
            self.dic[cell].remove(currentChain)
            self.chains.remove(currentChain)
            return "done" 
    
    def forceMakeCollapse(self,cell):
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
            tempList[low] = (0,0) # turns an examined dot to (0,0)
        else:
            low = 0
        if chain.chainList[-1] != (0,0):
            for i in xrange(len(chain.chainList)-1,chain.breakInd-1,-1):
                if chain.chainList[i] == (0,0):
                    high = i+1 # high index shift by one
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


    def redrawShapes(self):
        self.traceLine()
        self.drawLock()
        self.traceTransfer() # trace the transfer through chains
        self.drawChain()
        self.drawLine()

        
    def redrawAll(self):
        cellImg = self.imageList[0]
        self.screen.blit(self.bgimage,(0,0))
        needlex,needley,textx,texty,needleFont = 647,643,610,650,25
        self.screen.blit(self.needleImg,(needlex,needley))
        font = pygame.font.SysFont("Franklin Gothic Demi",needleFont,False)
        textObj = font.render("%d x "%self.needleLeft,True,GREEN)
        self.screen.blit(textObj,(textx,texty))
        self.redrawShapes()
        maxFont = 15
        font = pygame.font.SysFont("Calibri",maxFont,False)
        textObj = font.render("Maximum life value: %s"%self.maximum,True,GREEN)
        self.screen.blit(textObj,(10,10))
        for cell in self.cellList:
            if cell.name == "ATT":
                cycle,backCycle,rd,adjustx,adjusty = 35,31,5,48,53
                if self.animateCount % len(self.imageList) == 0:
                    self.order = not self.order
                cellImg = self.imageList[(self.animateCount%cycle)/rd] \
                     if self.order else\
                     self.imageList[-(self.animateCount%backCycle)/rd - 1]
                self.screen.blit(cellImg,(cell.x-adjustx,cell.y-adjusty))
            cell.drawCell(self.screen)
        if self.needleMode:
            self.screen.blit(self.mouseFigure,self.getNeedlePos())
        try:self.playShine(self.shinex,self.shiney,True)
        except: pass
        pygame.display.flip()
        
        
    def getNeedlePos(self):
        (x,y) = pygame.mouse.get_pos()
        adjustx,adjusty = 53/2,57/2
        return (x-adjustx,y-adjusty)

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
        self.levelCleared = [0,1]
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
        self.creInitx,self.creInity = 320,100
        self.achichoice = 0
        self.screen.blit(self.mainImages[0],(0,0))
        self.gameDisplayDepth = 1 # the depth of game, main menu is 1
        #print "reach here"
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
        self.mode = "Win" # shift the self.mode to stop other running functions
        self.music.fadeout(self.fadeTime)
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
        textPos,fontSize = (314,295+self.winImgy),60
        font = pygame.font.SysFont("Courier",fontSize,True)
        textObj = font.render("%d"%self.levelChosen,True,(255,255,255))
        self.screen.blit(textObj,textPos)
        if self.levelChosen not in self.levelCleared:
            self.levelCleared.append(self.levelChosen)
        pygame.display.update()

    def doGameOver(self):
        self.mode = "Game Over" # shift the self.mode
        self.music.fadeout(self.fadeTime) # background music fading out
        self.screen.blit(pygame.image.load('result4.jpg'),(0,0))
        (x,y) = pygame.mouse.get_pos()
        if 225 <= x <= 305 and 558 <= y <= 631:
            self.gameOverchoice = 0
            self.screen.blit(self.gameOverImages[0],(0,0)) # button dim
        elif 357 <= x <= 436 and 558 <= y <= 631:
            self.gameOverchoice = 1
            self.screen.blit(self.gameOverImages[1],(0,0))
        else:
            self.gameOverchoice = None
        textPos,fontSize = (314,295+self.winImgy),60
        font = pygame.font.SysFont("Courier",fontSize,True)
        textObj = font.render("%d"%self.levelChosen,True,WHITE)
        self.screen.blit(textObj,textPos)
        pygame.display.update()
                        
        

    def openHelp(self):
        self.mode = "Help"
        self.helpInd = 0
        self.screen.blit(self.helpPages[self.helpInd],(0,0))
        pygame.display.update()

            
    def chooseLevel(self): # of depth 3
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
                self.doLevel7()
            else:
                self.screen.blit(pygame.image.load('level7unavailable.jpg'),(0,0))
                self.undoLevel7()
        pygame.display.update()

    def doLevel1_3(self):
        self.mode = "Choose Level"
        (x,y) = pygame.mouse.get_pos()
        if 252 <= x <= 415 and 243 <= y <= 397:
            self.screen.blit(pygame.image.load('level1-3sun.jpg'),(0,0))

        elif 300 <= x <= 382 and 595 <= y <= 672:
            self.screen.blit(pygame.image.load('level1-3button.jpg'),(0,0))

        elif 533 <= x <= 596 and 279 <= y <= 351:
            self.screen.blit(pygame.image.load('level1-3arrow.jpg'),(0,0))

        pygame.display.update()

    def finalLevel1_3(self):
        if len(self.levelCleared) == 1: #[0],initially
            self.screen.blit(pygame.image.load("level123(1).jpg"),(0,0))
        elif len(self.levelCleared) == 2: #[0,1]
            self.screen.blit(pygame.image.load("level123(2).jpg"),(0,0))
        else:
            self.screen.blit(pygame.image.load("level123.jpg"),(0,0))
        (text,tempLevelCleared,font2) = self.enterInterface()
        warning,maxLevel = (220,470),3
        # Unavailable level display
        if len(text) == 1 and ((eval(text) not in tempLevelCleared)\
           or eval(text) > maxLevel):
            textObj2 = font2.render("Unavailable Level",True,(2,2,2))
            self.screen.blit(textObj2,warning)
        pygame.display.update()

    def enterInterface(self):
        font1 = pygame.font.SysFont("Berlin Sans FB",36,True)
        font2 = pygame.font.SysFont("Berlin Sans FB",28,True)
        try:text = self.levelText
        except: text = ""
        textPos,warning = (110,420),(220,470)
        textObj1 = font1.render("Enter the level(Keyboard):  %s"%text,\
                                False,(2,2,2))
        self.screen.blit(textObj1,textPos)
        tempLevelCleared = self.levelCleared + [self.levelCleared[-1]+1]
        pygame.display.update()
        return (text,tempLevelCleared,font2)
                   

    def doLevel4_6(self):
        self.mode = "Choose Level"
        (x,y) = pygame.mouse.get_pos()
        if 87 <= x <= 154 and 279 <= y <= 355:
            self.screen.blit(pygame.image.load('level4-6available1.jpg'),(0,0))

        elif 252 <= x <= 415 and 243 <= y <= 397:
            # choose one of 4-6
            self.screen.blit(pygame.image.load('level4-6available3.jpg'),(0,0))

        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            self.screen.blit(pygame.image.load('level4-6available2.jpg'),(0,0))

        elif 533 <= x <= 596 and 279 <= y <= 351:
            self.screen.blit(pygame.image.load('level4-6available4.jpg'),(0,0))

        pygame.display.update()

    def doLevel7(self):
        self.mode = "Choose Level"
        (x,y) = pygame.mouse.get_pos()
        if 87 <= x <= 154 and 279 <= y <= 355:
            self.screen.blit(pygame.image.load('level7available1.jpg'),(0,0))
        elif 252 <= x <= 415 and 243 <= y <= 397:
            # choose one of 4-6
            self.screen.blit(pygame.image.load('level7available3.jpg'),(0,0))
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            self.screen.blit(pygame.image.load('level7available2.jpg'),(0,0))
        pygame.display.update()

    def actLevel4_6(self,x,y):
        # this is called when level 4 to 6 is available, in the main level page
        if 87 <= x <= 154 and 279 <= y <= 355:
            self.levelPage = "1-3"
            self.chooseLevel()
        elif 252 <= x <= 415 and 243 <= y <= 397:
            # choose one of 4-6
            self.mode = "Choose Final Level"
            self.finalLevel4_6()
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            self.doMainMenu()
        elif 533 <= x <= 596 and 279 <= y <= 351:
            self.levelPage = "7"

    def unactLevel4_6(self,x,y):
        if 87 <= x <= 154 and 279 <= y <= 355:
            self.levelPage = "1-3"
            self.chooseLevel()
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            self.doMainMenu()

    def finalLevel4_6(self):
        if len(self.levelCleared) == 4: #[0,1,2,3]
            self.screen.blit(pygame.image.load("level456(1).jpg"),(0,0))
        elif len(self.levelCleared) == 5: #[0,1,2,3,4]
            self.screen.blit(pygame.image.load("level456(2).jpg"),(0,0))
        else:
            self.screen.blit(pygame.image.load("level456.jpg"),(0,0))
        (text,tempLevelCleared,font2) = self.enterInterface()
        warning,limit1,limit2 = (220,470),6,4
        if len(text) == 1 and ((eval(text) not in tempLevelCleared)\
           or eval(text) > limit1 or eval(text) < limit2):
            textObj2 = font2.render("Unavailable Level",True,(2,2,2))
            self.screen.blit(textObj2,warning)
        pygame.display.update()

    def undoLevel4_6(self):
        self.mode = "Choose Level"
        (x,y) = pygame.mouse.get_pos()
        if 87 <= x <= 154 and 280 <= y <= 352:
            image = pygame.image.load('level4-6unavailable1.jpg')
            self.screen.blit(image,(0,0))
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            image = pygame.image.load('level4-6unavailable2.jpg')
            self.screen.blit(image,(0,0))
        pygame.display.update()

    def undoLevel7(self):
        self.mode = "Choose Level"
        (x,y) = pygame.mouse.get_pos()
        if 87 <= x <= 154 and 280 <= y <= 352:
            image = pygame.image.load('level7unavailable1.jpg')
            self.screen.blit(image,(0,0))
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            image = pygame.image.load('level7unavailable2.jpg')
            self.screen.blit(image,(0,0))
        pygame.display.update()

    

    def actLevel7(self,x,y):
        # this is called when level 7 is available, in the main level page
        if 87 <= x <= 154 and 279 <= y <= 355:
            self.levelPage = "4-6"
            self.chooseLevel()
        elif 252 <= x <= 415 and 243 <= y <= 397:
            self.init(7)
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            self.doMainMenu()

    def unactLevel7(self,x,y):
        if 87 <= x <= 154 and 279 <= y <= 355:
            self.levelPage = "4-6"
            self.chooseLevel()
        elif 300 <= x <= 382 and 595 <= y <= 672:
            # press the button
            self.doMainMenu()
            
        

    def runMenuOption(self,option): # choosing at depth 1
        pygame.mixer.Sound('Confirm.wav').play(0)
        if option == "Play":
            # Should choose level first
            self.doBackground()
            self.gameDisplayDepth += 1            
        elif option == "Help":
            self.openHelp()
            self.gameDisplayDepth = 2
        elif option == "Credit":
            self.runCredit()
        elif option == "Achievement":
            self.displayAchi()

    def runCredit(self):
        self.mode = "Credit"
        interface = pygame.image.load('GrayImage2.jpg')
        self.screen.blit(interface,(0,0))
        displayCredit(self.screen,self.creInitx,self.creInity)
        if self.animateCount % 2 == 0:
            self.creInity -= 1
        pygame.display.update()
            

    def displayAchi(self):
        self.mode = "Achievement"
        if self.achichoice == 0:
            self.doAchievement()
        elif self.achichoice == 1:
            self.doAchievementPage2()
        

    def doAchievement(self):
        self.achievement = [self.gamesPlayed,self.loses,self.enemyKilled,\
                     self.needleLeft,self.totalMerge,self.totalAssist]
        self.screen.blit(pygame.image.load("Achievement1.jpg"),(0,0))
        gamesPlayed = self.achievement[0]
        loses,enemyKilled = self.achievement[1],self.achievement[2]
        needleLeft,totalMerge = self.achievement[3],self.achievement[4]
        totalAssist = self.achievement[5]
        levelCompleted = len(self.levelCleared)-1
        font = pygame.font.SysFont("Arial",20,True)
        textObj1 = font.render("%d" %gamesPlayed,True,WARMYELLOW)
        textObj2 = font.render("%d" %levelCompleted,True,WARMYELLOW)
        textObj3 = font.render("%d" %loses,True,WARMYELLOW)
        textObj4 = font.render("%d" %enemyKilled,True,WARMYELLOW)
        textObj5 = font.render("x %d" %needleLeft,True,WARMYELLOW)
        (pos1,pos2,pos3,pos4,pos5) = self.getTextPos()
        self.screen.blit(textObj1,pos1)
        self.screen.blit(textObj2,pos2)
        self.screen.blit(textObj3,pos3)
        self.screen.blit(textObj4,pos4)
        self.screen.blit(textObj5,pos5)
        pygame.display.update()

    def getTextPos(self):
        # the positions of the texts on the Achievement Page
        return ((503,149),(503,205),(503,264),(503,323),(503,486))

    def doAchievementPage2(self):
        totalMerge = self.totalMerge
        totalAssist = self.totalAssist
        enemyKilled = self.enemyKilled
        title = []
        mergeNum,assistNum,killNum = 10,5,30
        if totalMerge >= mergeNum:title.append(1)
        if totalAssist >= assistNum: title.append(2)
        if enemyKilled >= killNum: title.append(3)
        titleCompleted = self.findTitleImg(title)
        self.screen.blit(titleCompleted,(0,0))
        pygame.display.update()

    def findTitleImg(self,title):
        titleImageList = [pygame.image.load("Achievement2(0).jpg"),\
                          pygame.image.load("Achievement2(1).jpg"),\
                          pygame.image.load("Achievement2(2).jpg"),\
                          pygame.image.load("Achievement2(3).jpg"),\
                          pygame.image.load("Achievement2(12).jpg"),\
                          pygame.image.load("Achievement2(13).jpg"),\
                          pygame.image.load("Achievement2(23).jpg"),\
                          pygame.image.load("Achievement2.jpg")]
        if title == []:
            return titleImageList[0]
        elif len(title) == 1:
            return titleImageList[title[0]] # 1,2 or 3
        elif len(title) == 2:
            return titleImageList[sum(title)+1] # [1,2],[1,3] or [2,3]
        else:
            return titleImageList[-1]
        
                          
  
    def runTutSetup(self):
        self.tutorialStep = 2 # welcome!

    def loadImageList(self):
        self.imageList = [pygame.image.load('GreenCell4.png'),\
                     pygame.image.load('GreenCell9.png'),\
                     pygame.image.load('GreenCell6.png'),\
                     pygame.image.load('GreenCell8.png'),\
                     pygame.image.load('GreenCell5.png'),\
                     pygame.image.load('GreenCell7.png'),\
                     pygame.image.load('GreenCell3.png'),]
        self.needleImg,self.needleMode = pygame.image.load('needle.png'),False

    def initImgAndMusic(self):
        self.winImgy = -700
        self.bgimage = self.bgImagePool[self.bgchoice]
        self.music = pygame.mixer.Sound("Christian.ogg")
        self.musicChannel = self.music.play(-1)
        self.loadImageList()       
        # set self.animateCount to zero again
        self.animateCount = 0

    def init(self,level): # level as a number
        self.mode = "Running" if level > 1 else "Tutorial"
        if self.mode == "Tutorial":
            self.runTutSetup()
        self.initImgAndMusic()
        self.potential = None # potential target pointing at
        self.lineDrawn,self.grayify = [],False # should we make bg gray?
        self.recordPos = None # a temporary position recorder
        self.order = True # left to right
        self.levelList = [Level_1(),Level_2(),Level_3(),Level_4(),Level_5(),\
                          Level_6(),Level_7()]
        self.levelChosen,self.AIEMB,self.chains = level,None,[]
        self.cellList = self.levelControl(self.levelList[level-1])
        self.maximum = self.levelList[level-1].maximum
        self.dic = dict() # same as above, to record.
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
            self.timerFired() 


        
                
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
        self.lastValue = self.value = value
        self.name = "ATT"
        self.state,self.loss = None,0
        self.d,self.avgDelta = dict(),[]
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

    def findEmergencyCell(self):
        alliesList = self.alliesList
        for (allyValue,allyName,ally) in alliesList:
            #print "allyinfo:",ally.x,ally.y
            if ally.state == "Alert" and allyName == "ATT":
                return ally
        return None
                

    def think(self,environment,animateCount):
        # the thinking process refers to the AI
        #####################################################################
        #     Later possibly use value drop in time also to determin. For
        # instance, consider d(C.V.)/dt
        #####################################################################
        enemyAvg = self.findEnemiesWithinDistance(environment)
        allyAvg = self.findAllies(environment)
        count,lowKey,highKey = animateCount,8,16
        delta = self.lastValue - self.value # loss of life in given time. Say 5.
        self.lastValue = self.value
        self.avgDelta.append(delta)
        if len(self.avgDelta) >= 15:
            self.loss = float(sum(self.avgDelta))/15
            self.avgDelta = []
            #print "loss",self.x,self.y,self.loss
        emergency = self.findEmergencyCell()
        #print "emergency:",emergency
        #print allyAvg,enemyAvg
        if animateCount < 100:
            self.state = "Defense"
        elif lowKey < self.value < highKey or 1.4 <= self.loss <=1.5 :
            # lose 6 value points per second
            self.state = "Defense"
        elif self.value <= lowKey or self.loss > 1.5:
            self.state = "Alert"
        elif self.value >= highKey:
            self.considerEmerg(emergency,allyAvg,enemyAvg)
            
                    
    def considerEmerg(self,emergency,allyAvg,enemyAvg):
        lowKey,highKey = 5,15
        if emergency != None:
            if self.value+90 >= enemyAvg:
                self.state = "Attack and Assist"
            elif self.value + allyAvg >= enemyAvg*3./2:
                self.state = "Attack and Assist"
            else:
                self.state = "Defense"
        else:
            if self.value+lowKey >= enemyAvg:
                self.state = "Attack"
            elif self.value + allyAvg >= enemyAvg*3./2:
                self.state = "Attack"
            else:
                self.state = "Defense"

    def update(self,environment,animateCount):
        # update every aspect: camp, current mode, etc.
        # ONLY ENEMY CELL NEEDS TO UPDATE.
        self.think(environment,animateCount)
        #print self.x,self.y,self.state
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


    ##################
    # Overriding
    ##################

    def findEnemiesWithinDistance(self,allCellList):
        """ return self.grayList and self.allOtherList as a tuple """
        # for AI use. 
        self.enemiesList = []
        grayList = [] # higher priority should be put in front
        enemyAvg = 0
        defaultReturn = 100
        for cell in allCellList:
            if cell.color != self.color:
                valueNeed = 2
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
            return defaultReturn # force the cell to be in defense mode

    def think(self,environment,animateCount):
        # the thinking process refers to the AI
        enemyAvg = self.findEnemiesWithinDistance(environment)
        allyAvg = self.findAllies(environment)
        remainAfter = 3
        count,highKey = animateCount,10
        # the bound is lower for EMB
        emergency = self.findEmergencyCell()
        #print allyAvg,enemyAvg
        if self.value < highKey or count < 240:
            # lose 6 value points per second
            # the initial state (before 240) is defense
            self.state = "Defense"
        elif self.value >= highKey:
            if emergency != None: # there is an emergency
                self.state == "Assist"
            elif self.value+remainAfter >= enemyAvg:
                self.state = "Attack"
            else:
                self.state = "Defense"

    def update(self,environment,animateCount):
        # update every aspect: camp, current mode, etc.
        # ONLY ENEMY CELL NEEDS TO UPDATE.
        self.think(environment,animateCount)
        # change mode,find friends,find enemies

            
class Level_1(object):
    def __init__(self):
        self.c1 = Cell(400,400,30)
        self.c2 = Cell(200,500,10,RED)
        self.c3 = Cell(570,180,5,RED)
        self.c4 = Embracer(450,180,10)
        self.maximum = 70
        self.cellList = [self.c1,self.c2,self.c3,self.c4]

class Level_2(object):
    def __init__(self):
        self.c1 = Cell(600,200,5,(55,55,55))
        self.c2 = Cell(500,300,10)
        self.c3 = Cell(240,420,10,(200,0,0))
        self.maximum = 70
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
        self.maximum = 80
        self.cellList = [self.c1,self.c2,self.c3,self.c4,self.c5,self.c6,self.c7]

class Level_4(object):
    def __init__(self):
        self.c1 = Cell(350,300,0,(55,55,55))
        self.c2 = Cell(500,370,30)
        self.c3 = Cell(240,230,20,(200,0,0))
        self.c4 = Cell(200,550,15,(200,0,0))
        self.c5 = Embracer(230,125,10,GREEN)
        self.c6 = Cell(450,180,15,(200,0,0))
        self.c7 = Cell(560,500,10,(55,55,55))
        self.maximum = 80
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
            cell = Cell(x,750-x,28,(200,0,0))
            self.cellList.append(cell)
        self.maximum = 90

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
        self.maximum = 90

class Level_7(object):
    def __init__(self):
        blueY = random.randint(350,450)
        self.c1 = Cell(260,180,25)
        self.c2 = Cell(230,280,25)
        self.c3 = Cell(230,500,30)
        self.c4 = Cell(260,600,30)
        self.c5 = Cell(500,200,50,RED)
        self.c6 = Cell(500,550,40,RED)
        self.c7 = Embracer(640,640,15,RED)
        self.c8 = Embracer(640,60,15,RED)
        self.c9 = Cell(550,blueY,80,(0,0,255))
        self.c10 = Embracer(50,350,10,(0,0,255))
        self.c11 = Embracer(100,100,5,(0,0,255))
        self.c12 = Embracer(350,650,8,GREEN)
        self.cellList = [self.c1,self.c2,self.c3,self.c4,self.c5,\
                         self.c6,self.c7,self.c8,self.c9,self.c10,\
                         self.c11,self.c12]
        self.maximum = 90

        
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
        self.lineHalfLength,self.freq = 5.5,20
        self.subtractCellValue = False # growing chain costs life value
        self.determineInd()

    def determineInd(self):
        cutoff1,cutoff2 = 280,450
        if cutoff1 <= self.chainFinalLen <= cutoff2:
            self.IndNum = 3
            self.shiningInd = [-1,-14,-27] # the dot on the chain that shines
        elif self.chainFinalLen > cutoff2:
            self.IndNum = 4
            self.shiningInd = [-1,-14,-27,-40]
        else:
            self.IndNum = 2
            self.shiningInd = [-1,-19]
        # two dots have distance difference of 18
    
    def grow(self):
        startx = self.chainList[-1][0]
        starty = self.chainList[-1][1]
        cycle = 8
        index = len(self.chainList)%cycle
        if index == 0:
            angle = math.atan(1/2.)
        elif index == 1:
            angle = math.atan(math.sqrt(2)/4)
        elif index == 2:
            angle = 0
        elif index == 3:
            angle = math.atan(-math.sqrt(2)/4)
        elif index == 4:
            angle = math.atan(-1/2.)
        elif index == 5:
            angle = math.atan(-math.sqrt(2)/4)
        elif index == 6:
            angle = 0
        elif index == 7:
            angle = math.atan(math.sqrt(2)/4)
        direction,regularRad = self.direction + angle,12
        newx = startx + 6*math.cos(direction)
        newy = starty - 6*math.sin(direction)
        self.chainList.append((newx,newy))
        if len(self.chainList)%2 == 0: # two dots worth one life value of cell
            self.subtractCellValue = True
        if dist(newx,newy,self.endx,self.endy,regularRad):
            self.shouldGrow = False
            collide = pygame.mixer.Sound('Collide.ogg')            
            collide.play(0)
            collide.set_volume(30)
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

############################
# Test function
############################

testWar = CellWar()

def testFindIntersection():
    print "Testing findIntersection()...",
    assert(testWar.findIntersection((0,0),(2,2),(0,2),(2,0)) == (1,1))
    assert(testWar.findIntersection((1,1),(3,1),(5,5),(2,2)) == False)
    assert(testWar.findIntersection((1,1),(3,1),(2,-1),(2,4)) == (2,1))
    assert(testWar.findIntersection((4,0),(0,2),(2,0),(2,2)) == (2,1))
    print "Passed!"

def testDist():
    print "Testing dist()...",
    assert(dist(1,1,2,2,10) == True)
    assert(dist(1,1,5,5,1) == False)
    assert(dist(0,0,3,0,2) == True)
    assert(dist(1,3,2,4,2) == True)
    print "Passed!"

testFindIntersection()
testDist()

