from .speedcontroller import SpeedController
from .robotdrivebase import RobotDriveBase

import math

class DifferentialDrive(RobotDriveBase):

    def __init__(self, left: SpeedController, right:SpeedController):
        self.left = left
        self.right = right
        self.rightSideInvertMultiplier = -1.0
        self.deadband = 0.02
        self.maxOutput = 1

    def arcadeDrive(self, xspeed: float, zRotation: float):
        #some math to convert a rotation value to speed value per motor
        pass

    def tankDrive(
        self, leftSpeed: float, rightSpeed: float, squareInputs: bool = True
    ) -> None:
        """Provide tank steering using the stored robot configuration.
        :param leftSpeed: The robot's left side speed along the X axis `[-1.0..1.0]`. Forward is positive.
        :param rightSpeed: The robot's right side speed along the X axis`[-1.0..1.0]`. Forward is positive.
        :param squareInputs: If set, decreases the input sensitivity at low speeds
        """
        leftSpeed = RobotDriveBase.limit(leftSpeed)
        leftSpeed = RobotDriveBase.applyDeadband(leftSpeed, self.deadband)

        rightSpeed = RobotDriveBase.limit(rightSpeed)
        rightSpeed = RobotDriveBase.applyDeadband(rightSpeed, self.deadband)

        # square the inputs (while preserving the sign) to increase fine
        # control while permitting full power
        if squareInputs:
            leftSpeed = math.copysign(leftSpeed * leftSpeed, leftSpeed)
            rightSpeed = math.copysign(rightSpeed * rightSpeed, rightSpeed)

        self.left.set(leftSpeed * self.maxOutput)
        self.right.set(
            rightSpeed * self.maxOutput * self.rightSideInvertMultiplier
        )


    def arcadeDrive(self, xSpeed: float, zRotation: float, squareInputs: bool = True) -> None:
        """Arcade drive method for differential drive platform.
        :param xSpeed: The robot's speed along the X axis `[-1.0..1.0]`. Forward is positive
        :param zRotation: The robot's zRotation rate around the Z axis `[-1.0..1.0]`. Clockwise is positive
        :param squareInputs: If set, decreases the sensitivity at low speeds.
        """
        xSpeed = RobotDriveBase.limit(xSpeed)
        xSpeed = RobotDriveBase.applyDeadband(xSpeed, self.deadband)

        zRotation = RobotDriveBase.limit(zRotation)
        zRotation = RobotDriveBase.applyDeadband(zRotation, self.deadband)

        if squareInputs:
            # Square the inputs (while preserving the sign) to increase fine
            # control while permitting full power.
            xSpeed = math.copysign(xSpeed * xSpeed, xSpeed)
            zRotation = math.copysign(zRotation * zRotation, zRotation)

        maxInput = math.copysign(max(abs(xSpeed), abs(zRotation)), xSpeed)

        if xSpeed >= 0.0:
            if zRotation >= 0.0:
                leftMotorSpeed = maxInput
                rightMotorSpeed = xSpeed - zRotation
            else:
                leftMotorSpeed = xSpeed + zRotation
                rightMotorSpeed = maxInput
        else:
            if zRotation >= 0.0:
                leftMotorSpeed = xSpeed + zRotation
                rightMotorSpeed = maxInput
            else:
                leftMotorSpeed = maxInput
                rightMotorSpeed = xSpeed - zRotation

        leftMotorSpeed = RobotDriveBase.limit(leftMotorSpeed) * self.maxOutput
        rightMotorSpeed = RobotDriveBase.limit(rightMotorSpeed) * self.maxOutput

        self.left.set(leftMotorSpeed)
        self.right.set(rightMotorSpeed * self.rightSideInvertMultiplier)


    
