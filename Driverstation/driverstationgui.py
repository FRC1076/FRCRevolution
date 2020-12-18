import pygame, sys, time    #Imports Modules
# pylint: disable=no-member

class RectItem():
    def __init__(self, color, x,y,width,height,  text='', fontSize=40, outline=None):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.selected = False
        self.fontSize = fontSize
        self.outline = outline
        

    def isSelected(self):
        return self.selected

    def setText(self, t):
        self.text = t

    def select(self):
        self.selected = True
        self.color = (0, 180, 0)
   
    def unselect(self):
        self.selected = False
        self.color = (0, 255, 0)

    def draw(self,win, outline=None):
        #Call this method to draw the button on the screen
        
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        if self.text != '':
            font = pygame.font.SysFont('comicsans', self.fontSize)
            text = font.render(self.text, 1, (0,0,0))
            # To center the text, add back in
            # + (self.width/2 - text.get_width()/2)
            win.blit(text, 
                (self.x ,
                 self.y + (self.height/2 - text.get_height()/2)))

    
 
class Button(RectItem):

    def __init__(self, color, x,y,width,height, text, fontSize=40, rValue=None):
        RectItem.__init__(self,color, x,y,width,height, text, fontSize)
        self.rValue = rValue
        

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                #self.onPressed()
                return True
            
        return False

    def returnValue(self):
        return {"action":self.rValue[0], "value":self.rValue[1]}

class rectIndicator(RectItem):
    def __init__(self, color, x,y,width,height):
        RectItem.__init__(self,color,x,y,width,height)
        

    def setColor(self, newColor):
        self.color = newColor





class DriverstationGUI():

    def __init__(self):
        pygame.init()#Initializes Pygame
        self.W = (255, 255, 255)
        self.G = (0, 255, 0)
        self.R = (255, 0, 0)
        

    def setup(self):
        # Initialize Window
        self.screen = pygame.display.set_mode((600, 320))
        pygame.display.set_caption('Driverstation')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        # lX,lY = location x, y
        # sX,sY = size x, y  
        

        
        # pygame setup                      lX  lY  sX   sY
        self.descriptionText = RectItem(self.G,  0,  0, 600,  40, "PiKitLib Driverstation", 50)
        self.batteryText     = RectItem(self.G,380, 50, 100,  30, "Voltage:", 20)
        self.batteryVal      = RectItem(self.G,380, 70, 100,  50, "NO DATA", 30)
        self.enableButton    = Button(self.G,   50,220, 100,  90, "Enable",  rValue=["Enable", True])
        self.disableButton   = Button(self.G,  160,220, 100,  90, "Disable", rValue=["Enable", False])
        self.teleopButton    = Button(self.G,   50, 50, 210,  30, "TeleOperated", 30, ["Mode", "Teleop"])
        self.autonButton     = Button(self.G,   50, 90, 210,  30, "Autonomous", 30, ["Mode", "Auton"])
        self.practiceButton  = Button(self.G,   50,130, 210,  30, "Practice (TODO)", 30, ["Mode", "Practice"])
        self.testButton      = Button(self.G,   50,170, 210,  30, "Test     (TODO)", 30, ["Mode", "Test"])
        #self.eStopButton     = Button(self.G,  270,220, 100,  90, "EStop",  rValue=["ESTOP", True])
        self.sendCodeButton  = Button(self.G,  270,220, 100,  90, "Send Code", 30, ["Code", True])
        self.commText        = RectItem(self.W,380,110, 100,  20, "Communication", 20, outline=1) #Is the robot connected?
        self.robotCodeText   = RectItem(self.W,380,130, 100,  20, "Robot Code", 20, outline=1)  #Is there code on the robot? (TODO)
        self.joystickText    = RectItem(self.W,380,150, 100,  20, "Joysticks", 20, outline=1) 
        
        
        self.commIndicator   = rectIndicator(self.R,480,110,40,18)
        self.codeIndicator   = rectIndicator(self.R,480,130,40,18)
        self.joyIndicator    = rectIndicator(self.R,480,150,40,18)

        self.indicators = [self.commIndicator, self.codeIndicator, self.joyIndicator]

        self.control_buttons = [self.testButton,self.practiceButton,
                                self.autonButton,self.teleopButton]
        self.enable_buttons = [self.enableButton,self.disableButton]
        
        self.exclusive_buttons = [self.enable_buttons, self.control_buttons]
        #self.regular_buttons = [self.sendCodeButton]
        self.pygame_buttons  = self.enable_buttons + self.control_buttons
        self.texts = [self.descriptionText, self.batteryVal, self.batteryText, self.commText,
                      self.robotCodeText, self.joystickText, self.joyIndicator, self.codeIndicator,
                      self.commIndicator]
    


    def redrawWindow(self):
        self.screen.fill((255,255,255))
        for bt in self.pygame_buttons:
            bt.draw(self.screen, 1)
        for t in self.texts:
            t.draw(self.screen, 0)
        #self.descriptionText.draw(self.screen)

    def update(self):
        self.redrawWindow()
        pygame.display.update()
        #self.clock.tick(30)
        #time.sleep(0.02)

    def setBatInfoText(self, txt: str):
        self.batteryVal.setText(txt)

    def getCurrentEvents(self):
        return pygame.event.get()

    def getPos(self):
        return pygame.mouse.get_pos()

    def updateIndicator(self, ind, value):
        self.indicators[ind].setColor(self.G if value else self.R)

    def getButtonPressed(self):
        """
        Returns button pressed, None if not
        """
        pos = self.getPos()
        for event in self.getCurrentEvents():
            if event.type == pygame.MOUSEMOTION:
                for b in self.pygame_buttons:
                    if not b.selected:
                        if b.isOver(pos):
                            b.color = (0, 180, 0)
                        else:
                            b.color = (0, 250, 0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btnSet in self.exclusive_buttons:
                    for btn in btnSet:
                        if btn.isOver(pos) and not btn.isSelected():
                            for jbtn in btnSet:
                                jbtn.unselect()
                            btn.select()
                            return btn.returnValue()
                #for btn in self.regular_buttons:
                #    if btn.isOver(pos):
                #        return btn.returnValue()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return {"action":"Quit", "value":True}
                if event.key == pygame.K_SPACE:
                    return {"action":"ESTOP", "value":True}
            if event.type == pygame.QUIT:
                return {"action":"Quit", "value":True}  
        return {"action":None, "value":None}

    

    