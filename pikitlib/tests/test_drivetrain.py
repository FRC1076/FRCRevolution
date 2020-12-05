import pikitlib

class GetSet:
    def __init__(self, state):
        self.state = state

    def get(self):
        return self.state

    def set(self, state):
        self.state = state


def test_tankdrive():
    left_motor = GetSet(0)
    right_motor = GetSet(0)
    drivetrain = pikitlib.DifferentialDrive(left_motor, right_motor)
    drivetrain.tankDrive(0.7, 0.7)
    assert left_motor.state > 0
    assert right_motor.state < 0

def test_arcadedrive():
    left_motor = GetSet(0)
    right_motor = GetSet(0)
    drivetrain = pikitlib.DifferentialDrive(left_motor, right_motor)
    drivetrain.tankDrive(0.7, 0.7)
    assert left_motor.state > 0
    assert right_motor.state < 0