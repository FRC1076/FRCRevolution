import pikitlib
import revlib

from smbus2 import SMBus

import time
from networktables import NetworkTables
# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.ERROR)

import robotmap

LEFT_HAND = 1
RIGHT_HAND = 0

# The RevBot class instantiates important objects 
# you'll need to 

class MyRobot(revlib.RevBot):

    def robotInit(self):

        """Robot initialization function"""
        # object that handles basic drive operations

        # define left and right motors
        self.left_motor = self.configure_motor(robotmap.LEFT)
        self.right_motor = self.configure_motor(robotmap.RIGHT)

        self.left = revlib.motor_group.RevvyMotorGroup(self.left_motor)
        self.right = revlib.motor_group.RevvyMotorGroup(self.right_motor)

        NetworkTables.initialize()
        self.driver = pikitlib.XboxController(0)

        self.myRobot = revlib.differential_drive.RevvyDrive(self.left, self.right)
        print("done with robot init")

    def autonomousInit(self):
        self.myRobot.tankDrive(0.8, 0.8)

    def autonomousPeriodic(self):
        self.myRobot.tankDrive(1, 0.5)

    def teleopInit(self):
        """
        Configures appropriate robot settings for teleop mode
        """
        pass
        
    def deadzone(self, val, deadzone):
        if abs(val) < deadzone:
            return 0
        return val

    def teleopPeriodic(self):
       
        forward = self.driver.getY(LEFT_HAND)
        forward = self.deadzone(forward, robotmap.DEADZONE)
        rotation_value = self.driver.getX(RIGHT_HAND)
        self.myRobot.arcadeDrive(forward, rotation_value)

if __name__ == "__main__":
    pikitlib.run(MyRobot)
