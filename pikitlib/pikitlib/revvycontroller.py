from revvy.mcu.rrrc_control import RevvyControl
from revvy.mcu.rrrc_transport import RevvyTransport
from revvy.robot.ports.motors.dc_motor import DcMotorController
from revvy.hardware_dependent.rrrc_transport_i2c import RevvyTransportI2CDevice
from revvy.robot.ports.motor import create_motor_port_handler
from revvy.robot.configurations import Motors

from smbus2 import SMBus

MOTOR_PORTS = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']

class RevvyMotorController:
    '''
    A class that represents the motor ports on the Revvy
    Controller. Currently it's assumed that only the DC motors
    that come with the Revvy Robotics kit are being used. 

    When you instantiate the class, provide a list of ports (1-6)
    That have motors plugged in. You can then access the ports
    via the 'motors' attribute, a dict of DcMotorController
    objects keyed on port number.
    '''

    def __init__(self, active_ports):
        '''
        Instantiates the Revvy motor controller and configures the list
        of motor ports for the Revolution Robotics DC Motor.

        :active_ports: a list of ports on the
            revvy bot that actually have motors plugged into them, 
            ex: ['M1','M4'].
        '''
        
        # Remove duplicates
        active_ports = set(active_ports)

        # instantiate MCU controller and motor handler
        self.hw_controller = RevvyControl(RevvyTransport(RevvyTransportI2CDevice(0x2D,SMBus(1))))
        self.motor_handler = create_motor_port_handler(hw_controller)

        self.motors = {}

        # configure active ports for Revvy DC motpr
        for p in active_ports:
            if p in MOTOR_PORTS:
                port = self.motor_handler._ports[int(p.lstrip('M'))].configure(Motors.RevvyMotor)
                self.motors[p] = DcMotorController(port, Motors.RevvyMotor['config'])
            else
                raise ValueError(f'Invalid motor port {p}')



