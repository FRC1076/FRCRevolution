from .speedcontroller import SpeedController

class SpeedControllerGroup(SpeedController):

    def __init__(self, *argv):
        self.motors = []
        for motor in argv:
            self.motors.append(motor)
        self.current_speed = 0
        self.isInverted = False

    def set(self, value):
        self.current_speed = value
        for m in self.motors:
            m.set(value)

    def setInverted(self, isInverted):
        """
        bool isInverted
        """
        self.isInverted = isInverted
        for m in self.motors:
            m.setInverted(isInverted)
    
    def getInverted(self) -> bool:
        return self.isInverted

    def get(self):
        return self.current_speed
