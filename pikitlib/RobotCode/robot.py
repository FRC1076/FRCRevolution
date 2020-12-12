from pikitlib import XboxController
from revvy.revvycontroller import RevvyMotorController, MOTOR_PORTS, SENSOR_PORTS
from revvy.revvymotorgroup import RevvyMotorGroup
from revvy.revvydrive import RevvyDrive

import time
from networktables import NetworkTables
# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.ERROR)

import robotmap

LEFT_HAND = 1
RIGHT_HAND = 0

class MyRobot():
    def _get_revvy_ports(self, robotmap):
        """
        pulls the revvy motor and sensor ports out of robotmap
        and stores them as lists
        """

        self.motor_ports = [x for x in robotmap.__dict__.values() if x in MOTOR_PORTS ]
        self.sensor_ports = [x for x in robotmap.__dict__.values() if x in SENSOR_PORTS ]


    def robotInit(self):
        """Robot initialization function"""
        # object that handles basic drive operations

        # generate lists of sensor and motor ports from robotmap
        self._get_revvy_ports(robotmap)

        # instantiate motors (tbd: sensors)
        print(f"Motor ports {self.motor_ports}")
        self.motors = RevvyMotorController(self.motor_ports)

        self.left = RevvyMotorGroup(self.motors.ports[robotmap.LEFT])
        self.right = RevvyMotorGroup(self.motors.ports[robotmap.RIGHT])

        print("Done with motor groups")
        NetworkTables.initialize()
        print("initialized network tables")
        self.driver = XboxController(0)
        print("done w xbox controller")

        self.myRobot = RevvyDrive(self.left, self.right)
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
        rotation_value = self.driver.getX(RIGHT_HAND)
        self.myRobot.arcadeDrive(forward, rotation_value)

    def disable(self):
        
        if(self.motors):
            self.motors.disable()
