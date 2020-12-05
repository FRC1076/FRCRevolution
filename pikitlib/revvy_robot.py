import pikitlib
from pikitlib.revvycontroller import RevvyMotorController, MOTOR_PORTS, SENSOR_PORTS
from pikitlib.revvydrive import RevvyDrive

import time
from networktables import NetworkTables
# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

import robotmap

LEFT_HAND = 1
RIGHT_HAND = 0

class RevvyRobot():
    def _get_revvy_ports(self, robotmap):
        """
        pulls the revvy motor and sensor ports out of robotmap
        and stores them as lists
        """

        self.motor_ports = [x for x in robotmap.__dict__ if x in MOTOR_PORTS ]
        self.sensor_ports = [x for x in robotmap.__dict__ if x in SENSOR_PORTS ]


    def robotInit(self):
        """Robot initialization function"""
        # object that handles basic drive operations

        # generate lists of sensor and motor ports from robotmap
        _get_revvy_ports(robotmap)

        # instantiate motors (tbd: sensors)
        self.motors = RevvyMotorContoller(self.motor_ports)

        self.leftMotors = RevvyMotorGroup([self.motors[robotmap.LEFT]])
        self.rightMotors = RevvyMotorGroup(self.motors[robotmap.RIGHT]

        NetworkTables.initialize()
        self.driver = pikitlib.XboxController(0)

        self.myRobot = RevvyDrive(self.left, self.right)

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
        rotation_value = self.driver.getX(RIGHT_HAND)
        self.myRobot.arcadeDrive(forward, rotation_value)

