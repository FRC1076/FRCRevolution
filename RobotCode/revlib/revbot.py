# This class takes pieces of the RevvyFramework
# and instantiates important objects you can use in your
# robot.py.


from revvy.robot.status_updater import McuStatusUpdater
from revvy.mcu.commands import BatteryStatus
from revvy.mcu.rrrc_control import RevvyTransportBase
from revvy.robot.imu import IMU
from revvy.robot.led_ring import RingLed
from revvy.robot.ports.motor import create_motor_port_handler
from revvy.robot.ports.sensor import create_sensor_port_handler
from revvy.robot.sound import Sound
from revvy.hardware_dependent.rrrc_transport_i2c import RevvyTransportI2C

from revvy.robot.ports.motors.dc_motor import DcMotorController
from revvy.robot.configurations import Motors

MOTOR_PORTS = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']

class RevBot():

    def __init__(self): 

        self._comm_interface = RevvyTransportI2C(1)
        self._robot_control = self._comm_interface.create_application_control()
        self._ring_led = RingLed(self._robot_control)
        #self._sound = TBD

        #self._status = RobotStatusIndicator(self._robot_control)
        #self._status_updater = McuStatusUpdater(self._robot_control)
        self._battery = BatteryStatus(0, 0, 0)
        self._imu = IMU()
   
        self._motor_ports = create_motor_port_handler(self._robot_control)
        self._sensor_ports = create_sensor_port_handler(self._robot_control)

        self._disabled = False

    def configure_motor(self, port):
        '''
        Configures a revvy motor port and returns a DC motor
        controller object.

        :port: The port the motor is on (eg "M3")
        '''

        # verify port input
        if port not in MOTOR_PORTS:
            raise ValueError(f"Port {port} must be in {MOTOR_PORTS}")

        port_instance = self._motor_ports._ports[int(port.lstrip('M'))]
        port_instance.configure(Motors.RevvyMotor)

        return DcMotorController(port_instance, Motors.RevvyMotor['config'])

    @property
    def led(self):
        return self._ring_led

    def disable(self):
        for m in self._motor_ports:
            if(m._driver):
                m._driver.set_speed(0)

