# SPDX-License-Identifier: GPL-3.0-only

import binascii
import os
import time
import traceback
from contextlib import suppress
from json import JSONDecodeError

from revvy.robot.robot import Robot
from revvy.utils.file_storage import IntegrityError
from revvy.utils.logger import get_logger
from revvy.utils.stopwatch import Stopwatch
from revvy.utils.version import Version
from revvy.utils.functions import split, bytestr_hash, read_json
from revvy.mcu.rrrc_control import McuOperationMode


class McuUpdater:
    def __init__(self, robot: Robot):
        self._robot = robot.robot_control
        self._bootloader = robot.bootloader_control
        self._stopwatch = Stopwatch()

        self._log = get_logger('McuUpdater')

    def _read_operation_mode(self):
        self._stopwatch.reset()
        while self._stopwatch.elapsed < 10:
            with suppress(OSError):
                return self._robot.read_operation_mode()

            with suppress(OSError):
                return self._bootloader.read_operation_mode()

            self._log("Failed to read operation mode. Retrying")
            time.sleep(0.5)

        raise TimeoutError('Could not determine operation mode')

    def _finalize_update(self):
        """
        Finalize firmware and reboot to application
        """
        # noinspection PyBroadException
        try:
            self._bootloader.finalize_update()
            # at this point, the bootloader shall start the application
        except OSError:
            self._log('MCU restarted before finishing communication')
        except Exception:
            self._log(traceback.format_exc())

    def _request_bootloader_mode(self):
        try:
            self._log("Rebooting to bootloader")
            self._robot.reboot_bootloader()
        except OSError:
            self._log('MCU restarted before finishing communication')

    def is_update_needed(self, fw_version: Version, fw_crc):
        """
        Compare firmware version to the currently running one
        """
        mode = self._read_operation_mode()
        if mode == McuOperationMode.APPLICATION:
            fw = self._robot.get_firmware_version()
            if fw != fw_version:  # allow downgrade as well
                return True
            elif fw_version.branch == 'stable':
                return False  # avoid rebooting to bootloader on production robots
            else:
                self.reboot_to_bootloader()
                crc = self._bootloader.read_firmware_crc()
                return crc != fw_crc
        else:
            # in bootloader mode, probably no firmware, request update
            return True

    def reboot_to_bootloader(self):
        """
        Start the bootloader on the MCU

        This function checks the operating mode. Reboot is only requested when in application mode
        """
        mode = self._read_operation_mode()
        if mode == McuOperationMode.APPLICATION:
            self._request_bootloader_mode()
            # wait for the reboot to complete
            mode = self._read_operation_mode()
            assert mode == McuOperationMode.BOOTLOADER

    def upload_binary(self, checksum, data):
        self.reboot_to_bootloader()

        self._log(f"Image info: size: {len(data)} checksum: {checksum}")

        # init update
        self._log("Initializing update")
        self._bootloader.send_init_update(len(data), checksum)

        # split data into chunks
        chunks = split(data, chunk_size=255)

        # send data
        self._log('Sending data')
        self._stopwatch.reset()
        for chunk in chunks:
            self._bootloader.send_firmware(chunk)
        self._log(f'Data transfer took {round(self._stopwatch.elapsed, 1)} seconds')

    def finalize(self):
        if self._read_operation_mode() == McuOperationMode.BOOTLOADER:
            self._finalize_update()

            assert self._read_operation_mode() == McuOperationMode.APPLICATION


class FirmwareLoader:
    def __init__(self, fw_dir):
        self._fw_dir = fw_dir

        self.log = get_logger('FirmwareLoader')

    def get_firmware(self, hw_version):
        try:
            fw_metadata = read_json(os.path.join(self._fw_dir, 'catalog.json'))
            version = str(hw_version)

            data = {
                'file': os.path.join(self._fw_dir, fw_metadata[version]['filename']),
                'md5': fw_metadata[version]['md5'],
                'length': fw_metadata[version]['length'],
            }
            return Version(fw_metadata[version]['version']), self._read_firmware(data)

        except (IOError, JSONDecodeError, KeyError) as e:
            self.log(traceback.format_exc())
            raise KeyError from e

    def _read_firmware(self, fw_data):
        with open(fw_data['file'], "rb") as f:
            firmware_binary = f.read()

        if len(firmware_binary) != fw_data['length']:
            self.log('Firmware file length check failed, aborting')
            raise IntegrityError("Firmware file length does not match")

        checksum = bytestr_hash(firmware_binary)
        if checksum != fw_data['md5']:
            self.log('Firmware file integrity check failed, aborting')
            raise IntegrityError("Firmware file checksum does not match")

        return firmware_binary


def update_firmware(fw_dir, robot: Robot):
    loader = FirmwareLoader(fw_dir)

    try:
        try:
            fw_version, fw_binary = loader.get_firmware(robot.hw_version)
            checksum = binascii.crc32(fw_binary)

            updater = McuUpdater(robot)

            if updater.is_update_needed(fw_version, checksum):
                updater.upload_binary(checksum, fw_binary)

            updater.finalize()
        except Exception:
            loader.log(traceback.format_exc())
            raise

    except KeyError:
        loader.log(f'No firmware for the hardware ({robot.hw_version})')

    except IOError:
        loader.log('Firmware file does not exist or is not readable')

    except IntegrityError:
        loader.log('Firmware file corrupted')
