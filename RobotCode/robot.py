import pikitlib
import revlib
from time import sleep
import os

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

SOUNDS_DIR = os.path.dirname(os.path.realpath(__file__)) + '/sounds/'

class MyRobot(revlib.RevBot):

    def robotInit(self):

        """Robot initialization function"""
        # object that handles basic drive operations

        # define left and right motors
        self.left_motor = self.get_motor(robotmap.LEFT)
        self.right_motor = self.get_motor(robotmap.RIGHT)

        self.left = revlib.motor_group.MotorGroup(self.left_motor)
        self.right = revlib.motor_group.MotorGroup(self.right_motor)

        NetworkTables.initialize()
        self.driver = pikitlib.XboxController(0)

        self.myRobot = revlib.drive.Drive(self.left, self.right)
        
        self.bumper = self.get_sensor(robotmap.BUMPER, 'bumper_switch')
        self.ultra = self.get_sensor(robotmap.ULTRA, 'hcsr04')

    def autonomousInit(self):
        #self.myRobot.tankDrive(0.8, 0.8)
        pass

    def autonomousPeriodic(self):
        #self.myRobot.tankDrive(1, 0.5)

        if(self.bumper.value):
            self.set_led_color(0xffff00)

        if not self.bumper.value:
            self.set_led_color(0xB333FF)

        print(f"BUMPER: {self.bumper.value}")
        print(f"ULTRA: {self.ultra.value}")

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
       
        forward = self.driver.getX(LEFT_HAND)
        forward = self.deadzone(forward, robotmap.DEADZONE)
        rotation_value = self.driver.getY(RIGHT_HAND)
        self.myRobot.arcadeDrive(forward, rotation_value)

        if(self.driver.getRawButtonPressed(0)):
            self.play_sound(f'{SOUNDS_DIR}yee-haw.mp3')

if __name__ == "__main__":
    pikitlib.run(MyRobot)
