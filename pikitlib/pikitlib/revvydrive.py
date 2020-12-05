from revvy.robot.ports.motors.dc_motor import DcMotorController

# It looks like the valid Revvy DC motor speed values are -150 to 150.
SPEED_MULTIPLIER = 150

class RevvyDrive:

    def __init__(self, left: RevvyGroup, right: RevvyGroup):
        self.left = left
        self.right = right

    def tankDrive(self, leftSpeed: float, rightSpeed: float):
        '''
        Set speed of motors based on direct left and right inputs
        '''
        
        self.left.set_speed(leftSpeed * SPEED_MULTIPLIER)
        self.right.set_speed(rightSpeed * SPEED_MULTIPLIER)

    def arcadeDrive(self, xSpeed: float, zRotation: float):
        """Arcade drive method for differential drive platform.
        :param xSpeed: The robot's speed along the X axis `[-1.0..1.0]`. Forward is positive
        :param zRotation: The robot's zRotation rate around the Z axis `[-1.0..1.0]`. Clockwise is positive
        """
        
        left_speed = (xSpeed + zRotation) / 2 * SPEED_MULTIPLIER
        right_speed = (xSpeed - zRotation) / 2 * SPEED_MULTIPLIER
        self.left.set_speed(left_speed)
        self.right.set_speed(right_speed)
        
        

