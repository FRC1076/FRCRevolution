# SPDX-License-Identifier: GPL-3.0-only

import collections
import struct

from revvy.robot.ports.common import FunctionAggregator

Vector3D = collections.namedtuple('Vector3D', ['x', 'y', 'z'])


class IMU:
    def __init__(self):
        self._acceleration = Vector3D(0, 0, 0)
        self._rotation = Vector3D(0, 0, 0)
        self._yaw_angle = 0
        self._relative_yaw_angle = 0

        self._change_callbacks = FunctionAggregator()

    @property
    def yaw_angle(self):
        return self._yaw_angle

    @property
    def relative_yaw_angle(self):
        return self._relative_yaw_angle  # TODO pinning is not yet implemented

    @property
    def acceleration(self):
        return self._acceleration

    @property
    def rotation(self):
        return self._rotation

    @staticmethod
    def _read_vector(data, lsb_value):
        (x, y, z) = struct.unpack('<hhh', data)
        return Vector3D(x * lsb_value, y * lsb_value, z * lsb_value)

    def update_yaw_angles(self, data):
        (self._yaw_angle, self._relative_yaw_angle) = struct.unpack('<ll', data)

    def update_axl_data(self, data):
        self._acceleration = self._read_vector(data, 0.061)

    def update_gyro_data(self, data):
        self._rotation = self._read_vector(data, 0.035*1.03)
