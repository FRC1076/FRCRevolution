import pikitlib
import revlib

from revlib.revvy.robot.led_ring import RingLed

from smbus2 import SMBus

import time
from networktables import NetworkTables
# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.ERROR)

import robotmap

LEFT_HAND = 1
RIGHT_HAND = 0


class MyRobot(revlib.RevBot):

    def robotInit(self):

        """Robot initialization function"""
        # object that handles basic drive operations

        # define left and right motors
        self.left_motor = self.configure_motor(robotmap.LEFT)
        self.right_motor = self.configure_motor(robotmap.RIGHT)

        self.left = revlib.motor_group.MotorGroup(self.left_motor)
        self.right = revlib.motor_group.MotorGroup(self.right_motor)

        NetworkTables.initialize()
        self.driver = pikitlib.XboxController(0)

        self.myRobot = revlib.drive.Drive(self.left, self.right)

        self.led.start_animation(RingLed.BreathingGreen)

    def autonomousInit(self):
        self.myRobot.tankDrive(0.8, 0.8)
        self.led.start_animation(RingLed.BreathingGreen)

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
