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
from revvy.robot.configurations import Sensors
from revvy.robot.ports.sensors.simple import bumper_switch, hcsr04

MOTOR_PORTS = ['motor_1','motor_2','motor_3','motor_4','motor_5','motor_6']
SENSOR_PORTS = ['sensor_1','sensor_2','sensor_3','sensor_4']

class RevBot():

    def __init__(self): 

        self._comm_interface = RevvyTransportI2C(1)
        self._robot_control = self._comm_interface.create_application_control()
        self._ring_led = RingLed(self._robot_control)

        #self._sound = TBD

        #self._status = RobotStatusIndicator(self._robot_control)
        self._status_updater = McuStatusUpdater(self._robot_control)
        self._battery = BatteryStatus(0, 0, 0)
        self._imu = IMU()
   
        self._motor_ports = create_motor_port_handler(self._robot_control)
        self._sensor_ports = create_sensor_port_handler(self._robot_control)

        self.disabled = False

        # Need to enable battery and IMU
        self._status_updater.enable_slot("battery", self._process_battery_slot)
        self._status_updater.enable_slot("axl", self._imu.update_axl_data)
        self._status_updater.enable_slot("gyro", self._imu.update_gyro_data)
        self._status_updater.enable_slot("yaw", self._imu.update_yaw_angles)

    def set_led_color(self, color_code):
        '''
        Sets the ring LED to a specific color.
        color_code :hex number: an HTML color code 
        '''

        colors = [color_code for i in range(0,12)]
        self._ring_led.display_user_frame(colors)

    def disable(self):
        '''
        This disables all configured motor ports
        '''
        for m in self._motor_ports:
            if(m._driver):
                m.set_speed(0)
                self._status_updater.disable_slot(f"motor_{m.id}")

        self.disabled = True

    def enable(self):
        '''
        Enable all configured motor ports
        '''
        for m in self._motor_ports:
            if(m._driver):
                self._status_updater.enable_slot(f"motor_{m.id}", m.update_status)

        self.disabled = False

    def get_motor(self, port):

        # verify port input
        if port not in MOTOR_PORTS:
            raise ValueError(f"Port {port} must be in {MOTOR_PORTS}")

        # configure port
        port_instance = self._motor_ports._ports[int(port.lstrip('motor_'))]
        port_instance.configure(Motors.RevvyMotor)

        # instantiate motor object
        motor = DcMotorController(port_instance, Motors.RevvyMotor['config'])

        # enable port on status updater
        self._status_updater.enable_slot(port, motor.update_status)

        return motor

    def get_sensor(self, port, type):

        # verify port input
        if port not in SENSOR_PORTS:
            raise ValueError(f"Port {port} must be in {SENSOR_PORTS}")

        port_instance = self._sensor_ports._ports[int(port.lstrip('sensor_'))]

        if type == 'bumper_switch':
            port_instance.configure(Sensors.BumperSwitch)
            sensor = bumper_switch(port_instance, {})

        elif type == 'hcsr04':
            port_instance.configure(Sensors.Ultrasonic)
            sensor = hcsr04(port_instance, {})
        
        else:
            raise ValueError(f"Sensor type must be 'bumper_switch' or 'hcsr04'")

        self._status_updater.enable_slot(port, sensor.update_status)

        return sensor

    def update_status(self):
        self._status_updater.read()

    def _process_battery_slot(self, data):
        assert len(data) == 4
        main_status, main_percentage, _, motor_percentage = data

        self._battery = BatteryStatus(chargerStatus=main_status, main=main_percentage, motor=motor_percentage)

    @property
    def battery(self):
        return self._battery[1]
