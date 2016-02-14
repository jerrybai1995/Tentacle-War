import pygame

def displayCredit(screen,initialx,initialy):
    WHITE = (255,255,255)
    note0 = "---------------------------------------"
    note1 = "   I would like to express my gratitude"
    note2 = "to all those who helped me and encoura-"
    note3 = "ged me during this whole process of"
    note4 = "completing Tentacle Wars. In particular,"
    note5 = "I want to thank Professor David Kosbie,"
    note6 = "whose excellent teaching and guiding"
    note7 = "enables me to finish this amazing"
    note8 = "(though a bit difficult) game. Also, I"
    note9 = "would very much like to thank my"
    note10 = "mentor,Yidan, whose creative ideas"
    note11 = "always inspired me to be better."
    note12 = "                                     "
    note13 = "  I am also grateful to my friends,"
    note14 = "who helped me to keep improving this"
    note15 = "project, including:"
    note16 = "Jun Yan Seow,Li Hongyu,Lu Samuel,"
    note17 = "Stuart Guertin (CA),Xu Jiayuan,"
    note18 = "Yang Yuxuan,Zhao Chengcheng,Zhu Xiran."
    note19 = note12
    note20 = "Tentacle War by Shaojie Bai"
    note21 = "Spring 2014 15-112 Term Project"
    note22 = "--------------------------------------"
    totalNotes = [note0,note1,note2,note3,note4,note5,note6,note7,note8,\
                  note9,note10,note11,note12,note13,note14,note15,note16,\
                  note17,note18,note19,note20,note21,note22]
    for i in xrange(len(totalNotes)):
        note = totalNotes[i]
        if i == 20 or i == 21:
            size = 25
            ita = True
        else:
            size = 20
            ita = False
        font = pygame.font.SysFont("Calibri",size,True,ita)
        textObj = font.render("%s"%note,True,WHITE)
        x,y = initialx,initialy+i*30
        if not (-25 <= y <= 700):
            y %= 700
        screen.blit(textObj,(x,y))


