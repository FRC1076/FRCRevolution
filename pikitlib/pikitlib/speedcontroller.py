from pikitlib import pca_motor

__all__ = ["SpeedController"]

class SpeedController():
    def __init__(self, channel):
        """
        Takes in motor channel, on kit 1 2 3 4
        """
        self.motor = pca_motor.PCA9685(0x40, debug=True)
        self.motor.setPWMFreq(50)
        self.current_val = 0
        self.isInverted = False

        
        self.achannel = (channel * 2) - 2
        self.bchannel = self.achannel + 1

        if channel == 2:
            temp = self.achannel
            self.achannel = self.bchannel
            self.bchannel = temp
        

    def convert(self, value, scale=2000):
        #TODO: perhaps make this math a bit better, might not be needed
        return int(value * scale)

    def set(self, value) -> None:
        """
        Set the motor at the specified channel to the inputed value
        """
        speed = self.convert(value)
        if self.isInverted:
            speed *= -1

        self.current_val = speed
        
        if speed > 0:
            self.motor.setMotorPwm(self.achannel, 0)
            self.motor.setMotorPwm(self.bchannel, speed)
        elif speed < 0:
            self.motor.setMotorPwm(self.bchannel, 0)
            self.motor.setMotorPwm(self.achannel, abs(speed))
        else:
            self.motor.setMotorPwm(self.achannel, 4095)
            self.motor.setMotorPwm(self.bchannel, 4095)

    def get(self) -> float:
        return self.current_val

    def setInverted(self, isInverted):
        """
        bool isInverted
        """
        self.isInverted = isInverted

    def getInverted(self) -> bool:
        return self.isInverted
