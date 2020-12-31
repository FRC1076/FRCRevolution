from revvy.robot.ports.motors.dc_motor import DcMotorController
from revvy.robot.configurations import Motors

MOTOR_PORTS = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']

def getRevvyMotor(mh, port):
    '''
    Configures a revvy motor port and returns a DC motor
    controller object.

    :mh: Revvy motor handler object
    :port: The port the motor is on (eg "M3")
    '''
       
    # verify port input
    if port not in MOTOR_PORTS:
        raise ValueError(f"Port {port} must be in {MOTOR_PORTS}")

    port = mh._ports[int(p.lstrip('M'))]
    port.configure(Motors.RevvyMotor)

    return DcMotorController(port, Motors.RevvyMotor['config'])        
