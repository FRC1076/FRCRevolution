# SPDX-License-Identifier: GPL-3.0-only

import os
import struct
import traceback

from pybleno import Bleno, BlenoPrimaryService, Characteristic, Descriptor
from revvy.bluetooth.longmessage import LongMessageError, LongMessageProtocol
from revvy.utils.functions import bits_to_bool_list
from revvy.robot.remote_controller import RemoteControllerCommand
from revvy.utils.logger import get_logger


class BleService(BlenoPrimaryService):
    def __init__(self, uuid, characteristics: dict):

        self._named_characteristics = characteristics

        super().__init__({
            'uuid':            uuid,
            'characteristics': list(characteristics.values())
        })

    def characteristic(self, item):
        return self._named_characteristics[item]


class Observable:
    def __init__(self, value):
        self._value = value
        self._observers = []

    def update(self, value):
        self._value = value
        self._notify_observers(value)

    def get(self):
        return self._value

    def subscribe(self, observer):
        self._observers.append(observer)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    def _notify_observers(self, new_value):
        for observer in self._observers:
            observer(new_value)


# Device communication related services


class LongMessageCharacteristic(Characteristic):
    def __init__(self, handler):
        super().__init__({
            'uuid':       'd59bb321-7218-4fb9-abac-2f6814f31a4d',
            'properties': ['read', 'write'],
            'value':      None
        })
        self._handler = LongMessageProtocol(handler)

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        else:
            try:
                value = self._handler.handle_read()
                callback(Characteristic.RESULT_SUCCESS, value)

            except LongMessageError:
                callback(Characteristic.RESULT_UNLIKELY_ERROR, None)

    @staticmethod
    def _translate_result(result):
        if result == LongMessageProtocol.RESULT_SUCCESS:
            return Characteristic.RESULT_SUCCESS
        elif result == LongMessageProtocol.RESULT_INVALID_ATTRIBUTE_LENGTH:
            return Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH
        else:
            return Characteristic.RESULT_UNLIKELY_ERROR

    def onWriteRequest(self, data, offset, without_response, callback):
        result = Characteristic.RESULT_UNLIKELY_ERROR
        try:
            if offset:
                result = Characteristic.RESULT_ATTR_NOT_LONG

            elif len(data) < 1:
                result = Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH

            else:
                result = self._translate_result(self._handler.handle_write(data[0], data[1:]))

        except LongMessageError:
            print(traceback.format_exc())
        finally:
            callback(result)


class LongMessageService(BlenoPrimaryService):
    def __init__(self, handler):
        super().__init__({
            'uuid':            '97148a03-5b9d-11e9-8647-d663bd873d93',
            'characteristics': [
                LongMessageCharacteristic(handler),
            ]})


class MobileToBrainFunctionCharacteristic(Characteristic):
    def __init__(self, uuid, min_length, max_length, description, callback):
        self._callbackFn = callback
        self._minLength = min_length
        self._maxLength = max_length
        super().__init__({
            'uuid':        uuid,
            'properties':  ['write'],
            'value':       None,
            'descriptors': [
                Descriptor({
                    'uuid':  '2901',
                    'value': description
                }),
            ]
        })

    def onWriteRequest(self, data, offset, without_response, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        elif not (self._minLength <= len(data) <= self._maxLength):
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)
        elif self._callbackFn(data):
            callback(Characteristic.RESULT_SUCCESS)
        else:
            callback(Characteristic.RESULT_UNLIKELY_ERROR)


class BrainToMobileFunctionCharacteristic(Characteristic):
    def __init__(self, uuid, description):
        self._value = []
        self._updateValueCallback = None
        super().__init__({
            'uuid':        uuid,
            'properties':  ['read', 'notify'],
            'value':       None,
            'descriptors': [
                Descriptor({
                    'uuid':  '2901',
                    'value': description
                }),
            ]
        })

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            callback(Characteristic.RESULT_SUCCESS, self._value)

    def onSubscribe(self, max_value_size, update_value_callback):
        self._updateValueCallback = update_value_callback

    def onUnsubscribe(self):
        self._updateValueCallback = None

    def update(self, value):
        self._value = value

        callback = self._updateValueCallback
        if callback:
            callback(value)


class SensorCharacteristic(BrainToMobileFunctionCharacteristic):
    def update(self, value):
        # FIXME: prefix with data length is probably unnecessary
        super().update([len(value), *value])


class MotorCharacteristic(BrainToMobileFunctionCharacteristic):
    pass


class LiveMessageService(BlenoPrimaryService):
    def __init__(self):
        self._message_handler = None

        self._sensor_characteristics = [
            SensorCharacteristic('135032e6-3e86-404f-b0a9-953fd46dcb17', b'Sensor 1'),
            SensorCharacteristic('36e944ef-34fe-4de2-9310-394d482e20e6', b'Sensor 2'),
            SensorCharacteristic('b3a71566-9af2-4c9d-bc4a-6f754ab6fcf0', b'Sensor 3'),
            SensorCharacteristic('9ace575c-0b70-4ed5-96f1-979a8eadbc6b', b'Sensor 4'),
        ]

        self._motor_characteristics = [
            MotorCharacteristic('4bdfb409-93cc-433a-83bd-7f4f8e7eaf54', b'Motor 1'),
            MotorCharacteristic('454885b9-c9d1-4988-9893-a0437d5e6e9f', b'Motor 2'),
            MotorCharacteristic('00fcd93b-0c3c-4940-aac1-b4c21fac3420', b'Motor 3'),
            MotorCharacteristic('49aaeaa4-bb74-4f84-aa8f-acf46e5cf922', b'Motor 4'),
            MotorCharacteristic('ceea8e45-5ff9-4325-be13-48cf40c0e0c3', b'Motor 5'),
            MotorCharacteristic('8e4c474f-188e-4d2a-910a-cf66f674f569', b'Motor 6'),
        ]

        super().__init__({
            'uuid':            'd2d5558c-5b9d-11e9-8647-d663bd873d93',
            'characteristics': [
                MobileToBrainFunctionCharacteristic('7486bec3-bb6b-4abd-a9ca-20adc281a0a4', 20, 20, b'simpleControl',
                                                    self.simple_control_callback),
                *self._sensor_characteristics,
                *self._motor_characteristics
            ]
        })

    def register_message_handler(self, callback):
        self._message_handler = callback

    def simple_control_callback(self, data):
        analog_values = data[1:11]
        button_values = bits_to_bool_list(data[11:15])

        message_handler = self._message_handler
        if message_handler:
            message_handler(RemoteControllerCommand(analog=analog_values, buttons=button_values))
        return True

    def update_sensor(self, sensor, value):
        if 0 < sensor <= len(self._sensor_characteristics):
            self._sensor_characteristics[sensor - 1].update(value)

    def update_motor(self, motor, power, speed, position):
        if 0 < motor <= len(self._motor_characteristics):
            data = list(struct.pack(">flb", speed, position, power))
            self._motor_characteristics[motor - 1].update(data)

# Device Information Service


class ReadOnlyCharacteristic(Characteristic):
    def __init__(self, uuid, value):
        super().__init__({
            'uuid':       uuid,
            'properties': ['read'],
            'value':      value
        })


class SerialNumberCharacteristic(ReadOnlyCharacteristic):
    def __init__(self, serial):
        super().__init__('2A25', serial.encode())


class ManufacturerNameCharacteristic(ReadOnlyCharacteristic):
    def __init__(self, name):
        super().__init__('2A29', name)


class ModelNumberCharacteristic(ReadOnlyCharacteristic):
    def __init__(self, model_no):
        super().__init__('2A24', model_no)


class VersionCharacteristic(Characteristic):
    version_max_length = 20

    def __init__(self, uuid):
        super().__init__({
            'uuid':       uuid,
            'properties': ['read'],
            'value':      None
        })
        self._version = []

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            callback(Characteristic.RESULT_SUCCESS, self._version)

    def update(self, version):
        if len(version) > self.version_max_length:
            version = version[:self.version_max_length]
        self._version = version.encode("utf-8")


class SystemIdCharacteristic(Characteristic):
    def __init__(self, system_id: Observable):
        super().__init__({
            'uuid':       '2A23',
            'properties': ['read', 'write'],
            'value':      None
        })
        self._system_id = system_id

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            callback(Characteristic.RESULT_SUCCESS, self._system_id.get().encode('utf-8'))

    def onWriteRequest(self, data, offset, without_response, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        else:
            try:
                name = data.decode('ascii')
                if 0 < len(name) <= 15:
                    self._system_id.update(name)
                    callback(Characteristic.RESULT_SUCCESS)
                else:
                    callback(Characteristic.RESULT_UNLIKELY_ERROR)
            except UnicodeDecodeError:
                callback(Characteristic.RESULT_UNLIKELY_ERROR)


class RevvyDeviceInformationService(BleService):
    def __init__(self, device_name: Observable, serial):
        hw = VersionCharacteristic('2A27')
        fw = VersionCharacteristic('2A26')
        sw = VersionCharacteristic('2A28')
        serial = SerialNumberCharacteristic(serial)
        manufacturer_name = ManufacturerNameCharacteristic(b'RevolutionRobotics')
        model_number = ModelNumberCharacteristic(b'RevvyAlpha')
        system_id = SystemIdCharacteristic(device_name)

        super().__init__('180A', {
            'hw_version': hw,
            'fw_version': fw,
            'sw_version': sw,
            'serial_number': serial,
            'manufacturer_name': manufacturer_name,
            'model_number': model_number,
            'system_id': system_id
        })


class CustomBatteryLevelCharacteristic(Characteristic):
    """Custom battery service that contains 2 characteristics"""
    def __init__(self, uuid, description):
        super().__init__({
            'uuid':        uuid,
            'properties':  ['read', 'notify'],
            'value':       None,  # needs to be None because characteristic is not constant value
            'descriptors': [
                Descriptor({
                    'uuid':  '2901',
                    'value': description
                })
            ]
        })

        self._updateValueCallback = None
        self._value = 99  # initial value only

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            callback(Characteristic.RESULT_SUCCESS, [self._value])

    def onSubscribe(self, max_value_size, update_value_callback):
        self._updateValueCallback = update_value_callback

    def onUnsubscribe(self):
        self._updateValueCallback = None

    def update_value(self, value):
        self._value = value

        update_value_callback = self._updateValueCallback
        if update_value_callback:
            update_value_callback([value])


class CustomBatteryService(BleService):
    def __init__(self):
        main = CustomBatteryLevelCharacteristic('2A19', b'Main battery percentage')
        motor = CustomBatteryLevelCharacteristic('00002a19-0000-1000-8000-00805f9b34fa', b'Motor battery percentage')

        super().__init__('180F', {
            'main_battery': main,
            'motor_battery': motor,
        })


class RevvyBLE:
    def __init__(self, device_name: Observable, serial, long_message_handler):
        self._deviceName = device_name.get()
        self._log = get_logger('RevvyBLE')
        os.environ["BLENO_DEVICE_NAME"] = self._deviceName
        self._log(f'Initializing BLE with device name {self._deviceName}')

        device_name.subscribe(self._device_name_changed)

        dis = RevvyDeviceInformationService(device_name, serial)
        bas = CustomBatteryService()
        live = LiveMessageService()
        long = LongMessageService(long_message_handler)

        self._named_services = {
            'device_information_service': dis,
            'battery_service': bas,
            'long_message_service': long,
            'live_message_service': live
        }

        self._advertised_uuid_list = [
            live['uuid']
        ]

        self._bleno = Bleno()
        self._bleno.on('stateChange', self._on_state_change)
        self._bleno.on('advertisingStart', self._on_advertising_start)

    def __getitem__(self, item):
        return self._named_services[item]

    def _device_name_changed(self, name):
        self._deviceName = name
        os.environ["BLENO_DEVICE_NAME"] = self._deviceName
        self._bleno.stopAdvertising(self._start_advertising)

    def _on_state_change(self, state):
        self._log(f'on -> stateChange: {state}')

        if state == 'poweredOn':
            self._start_advertising()
        else:
            self._bleno.stopAdvertising()

    def _start_advertising(self):
        self._log('Start advertising as {}'.format(self._deviceName))
        self._bleno.startAdvertising(self._deviceName, self._advertised_uuid_list)

    def _on_advertising_start(self, error):
        def _result(result):
            return "error " + str(result) if result else "success"

        self._log(f'on -> advertisingStart: {_result(error)}')

        if not error:
            self._log('setServices')

            # noinspection PyShadowingNames
            def on_set_service_error(error):
                self._log(f'setServices: {_result(error)}')

            self._bleno.setServices(list(self._named_services.values()), on_set_service_error)

    def on_connection_changed(self, callback):
        self._bleno.on('accept', lambda _: callback(True))
        self._bleno.on('disconnect', lambda _: callback(False))

    def start(self):
        self._bleno.start()

    def stop(self):
        self._bleno.stopAdvertising()
        self._bleno.disconnect()
