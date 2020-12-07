from revvy.robot.ports.motors.dc_motor import DcMotorController

class RevvyMotorGroup():
    '''
    Class for grouping motors together.
    A subset of DcMotorController methods are defined
    that call that function on all ports.
    '''
    def __init__(self, *argv):

        self.ports = []
        for port in argv:
            if isinstance(port, DcMotorController):
                self.ports.append(port)
            else:
                raise TypeError(f'Port group inputs must be of type DcMotorController')

    def _do(self, function, inputs=None):
        '''
        Generic fuction that calls a DcMotorController method
        for all ports in the group
        '''
        results = []
        for port in self.ports:
            result = getattr(port, function)(inputs)
            results.append(result)

    def set_speed(self, speed):
        self._do('set_speed', inputs=speed)

