import enum
from networktables import NetworkTables
import time

from pikitlib import xboxconfig

class XboxController():


    class Hand(enum.IntEnum):

        kLeft = 0
        kRight = 1
    
    class Button(enum.IntEnum):
        kBumperLeft = 4
        kBumperRight = 5
        kA = 0
        kB = 1
        kX = 2
        kY = 3
        kBack = 6
        kStart = 7
        kBig = 8

    def __init__(self, id):
        self.id = id
        self.nt = NetworkTables.getTable("DriverStation/XboxController{}".format(id))

        # must initialize the state of all controls here, because
        # if the first inquiry asks if a button was pressed, then
        # it has to know if the state has changed since the last
        # time...
        # get and save button state
        
        #Linux Xbox Controller Values:
        # A, B, X, Y, L bumpter, R bumber, back, start, big shinny button
        # LHand Y, LHand X, L trigger, RHand X, RHand Y, R trigger
        
        self.buttons = self.nt.getBooleanArray("Buttons", [False])
        self.axis_values = self.nt.getNumberArray("Axis", [0])
        while self.axis_values == [0]:
            time.sleep(0.02)
            self.axis_values = list(self.nt.getNumberArray("Axis", [0]))


    def getRawButton(self, v) -> bool:
        newB = self.nt.getBooleanArray("Buttons", self.buttons)[v]
        self.buttons[v] = newB
        return newB

    def getRawButtonPressed(self, v) -> bool:
        newB = self.nt.getBooleanArray("Buttons", self.buttons)[v]
        pressed = newB and not self.buttons[v]
        self.buttons[v] = newB
        return pressed

    def getRawButtonReleased(self, v) -> bool:
        newB = self.nt.getBooleanArray("Buttons", self.buttons)[v]
        released =  not newB and self.buttons[v]
        self.buttons[v] = newB
        return released

    def getX(self, hand):
        """Get the x position of the controller.

        :param hand: which hand, left or right

        :returns: the x position
        """
        if hand == self.Hand.kLeft:
            self.axis_values[xboxconfig.LEFT_JOY_X] = self.nt.getNumberArray("Axis", self.buttons)[xboxconfig.LEFT_JOY_X]
            return self.axis_values[xboxconfig.LEFT_JOY_X]
        else:
            self.axis_values[xboxconfig.RIGHT_JOY_X] = self.nt.getNumberArray("Axis", self.buttons)[xboxconfig.RIGHT_JOY_X]
            return self.axis_values[xboxconfig.RIGHT_JOY_X]

    def getY(self, hand):
        """Get the y position of the controller.

        :param hand: which hand, left or right

        :returns: the y position
        """
        if hand == self.Hand.kLeft:
            self.axis_values[xboxconfig.LEFT_JOY_Y] = self.nt.getNumberArray("Axis", self.buttons)[xboxconfig.LEFT_JOY_Y]
            return self.axis_values[xboxconfig.LEFT_JOY_Y]
        else:
            self.axis_values[xboxconfig.RIGHT_JOY_Y] = self.nt.getNumberArray("Axis", self.buttons)[xboxconfig.RIGHT_JOY_Y]
            return self.axis_values[xboxconfig.RIGHT_JOY_Y]

    def getBumper(self, hand) -> bool:
        """Read the values of the bumper button on the controller.
        :param hand: Side of controller whose value should be returned.
        :return: The state of the button
        """
        if hand == self.Hand.kLeft:
            return self.getRawButton(self.Button.kBumperLeft)
        else:
            return self.getRawButton(self.Button.kBumperRight)

    def getBumperPressed(self, hand):
        """Whether the bumper was pressed since the last check.
        :param hand: Side of controller whose value should be returned.
        :returns: Whether the button was pressed since the last check.
        """
        if hand == self.Hand.kLeft:
            return self.getRawButtonPressed(self.Button.kBumperLeft)
        else:
            return self.getRawButtonPressed(self.Button.kBumperRight)
    
    def getBumperReleased(self, hand) -> bool:
        """Whether the bumper was released since the last check.
        :param hand: Side of controller whose value should be returned.
        :returns: Whether the button was released since the last check.
        """
        if hand == self.Hand.kLeft:
            return self.getRawButtonReleased(self.Button.kBumperLeft)
        else:
            return self.getRawButtonReleased(self.Button.kBumperRight)

    def getAButton(self) -> bool:
        """Read the value of the A button on the controller
        :return: The state of the A button
        """
        return self.getRawButton(self.Button.kA)

    def getAButtonPressed(self) -> bool:
        """Whether the A button was pressed since the last check.
        :returns: Whether the button was pressed since the last check.
        """
        return self.getRawButtonPressed(self.Button.kA)

    def getAButtonReleased(self) -> bool:
        """Whether the A button was released since the last check.
        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kA)

    def getBButton(self) -> bool:
        """Read the value of the B button on the controller
        :return: The state of the B button
        """
        return self.getRawButton(self.Button.kB)

    def getBButtonPressed(self) -> bool:
        """Whether the B button was pressed since the last check.
        :returns: Whether the button was pressed since the last check.
        """
        return self.getRawButtonPressed(self.Button.kB)

    def getBButtonReleased(self) -> bool:
        """Whether the B button was released since the last check.
        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kB)

    def getXButton(self) -> bool:
        """Read the value of the X button on the controller
        :return: The state of the X button
        """
        return self.getRawButton(self.Button.kX)

    def getXButtonPressed(self) -> bool:
        """Whether the X button was pressed since the last check.
        :returns: Whether the button was pressed since the last check.
        """
        return self.getRawButtonPressed(self.Button.kX)

    def getXButtonReleased(self) -> bool:
        """Whether the X button was released since the last check.
        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kX)

    def getYButton(self) -> bool:
        """Read the value of the Y button on the controller
        :return: The state of the Y button
        """
        return self.getRawButton(self.Button.kY)

    def getYButtonPressed(self) -> bool:
        """Whether the Y button was pressed since the last check.
        :returns: Whether the button was pressed since the last check.
        """
        return self.getRawButtonPressed(self.Button.kY)

    def getYButtonReleased(self) -> bool:
        """Whether the Y button was released since the last check.
        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kY)

    def getBackButton(self) -> bool:
        """Read the value of the Back button on the controller
        :return: The state of the Back button
        """
        return self.getRawButton(self.Button.kBack)

    def getBackButtonPressed(self) -> bool:
        """Whether the Back button was pressed since the last check.
        :returns: Whether the button was pressed since the last check.
        """
        return self.getRawButtonPressed(self.Button.kBack)

    def getBackButtonReleased(self) -> bool:
        """Whether the Back button was released since the last check.
        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kBack)

    def getStartButton(self) -> bool:
        """Read the value of the Start button on the controller
        :return: The state of the Start button
        """
        return self.getRawButton(self.Button.kStart)

    def getStartButtonPressed(self) -> bool:
        """Whether the Start button was pressed since the last check.
        :returns: Whether the button was pressed since the last check.
        """
        return self.getRawButtonPressed(self.Button.kStart)

    def getStartButtonReleased(self) -> bool:
        """Whether the Start button was released since the last check.
        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kStart)