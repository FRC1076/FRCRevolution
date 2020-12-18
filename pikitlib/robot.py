import pikitlib

#### a gazillion imports from Revvy ###

# these are classes unaltered from the revvy code
from revvy.mcu.commands import BatteryStatus
from revvy.mcu.rrrc_control import RevvyTransportBase
from revvy.robot.imu import IMU
from revvy.robot.led_ring import RingLed
from revvy.robot.ports.motor import create_motor_port_handler
from revvy.robot.ports.sensor import create_sensor_port_handler
from revvy.robot.sound import Sound

# these are custom wrappers around the code that allow
# us to interact w/the object in a FRC-style way
from revvy.revvydcmotor import getRevvyMotor
from revvy.revvymotorgroup import RevvyMotorGroup

from smbus2 import SMBus

import time
from networktables import NetworkTables
# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.ERROR)

import robotmap

LEFT_HAND = 1
RIGHT_HAND = 0

class MyRobot():

    def robotInit(self):
        """Robot initialization function"""
        # object that handles basic drive operations

        ### Stolen from RevvyFramework's robot.py, don't edit this section ###
        self._comm_interface = RevvyTransportI2C(1)
        self._robot_control = self._comm_interface.create_application_control()
        self._ring_led = RingLed(self._robot_control)
        #self._sound = TBD

        self._status = RobotStatusIndicator(self._robot_control)
        self._status_updater = McuStatusUpdater(self._robot_control)
        self._battery = BatteryStatus(0, 0, 0)
        self._imu = IMU()
    
        self._motor_ports = create_motor_port_handler(self._robot_control)
        self._sensor_ports = create_sensor_port_handler(self._robot_control)
        ##########

        # define left and right motors
        self.left_motor = getRevvyMotor(self._motor_ports, robotmap.LEFT)
        self.right_motor = getRevvyMotor(self._motor_ports, robotmap.RIGHT)

        self.left = RevvyMotorGroup(self.left_motor)
        self.right = RevvyMotorGroup(self.right_motor)

        NetworkTables.initialize()
        self.driver = pikitlib.XboxController(0)

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
        forward = self.deadzone(forward, robotmap.DEADZONE)
        rotation_value = self.driver.getX(RIGHT_HAND)
        self.myRobot.arcadeDrive(forward, rotation_value)

if __name__ == "__main__":
    pikitlib.run(MyRobot)
