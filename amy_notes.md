## Hacking the Robot
The RR robot has a Raspberry Pi under the hood and is running Raspbian. You can take out the SD card, put it on another Pi, and it will boot. However, the default username/password has been changed by Revolution Robotics.

Because we'd rather not mess with code that already works the ideal thing to do is get another SD card with Raspbian on it, put code on it that can talk to the robot, and put it into the RR's brain. 

Revolution Robotics [publishes instructions](https://revolutionrobotics.org/pages/robot-framework-on-raspbian) on how to do this with their own software, however they are slightly incorrect. Below are the instructions with the one tweak needed to actually make it work:

```
1. Download Raspbian and write it onto an SD card
2. Connect to wifi
3. Execute sudo raspi-config:

enable SSH
enable I2C
change Hostname if you want (it's easier to find your Raspberry on the network)
Force Audio to 3.5mm jack (if you don’t want to have sound from your HDMI monitor)
4. Update your Raspberry and run apt-get update, apt-get upgrade
5. Download and install our framework:

sudo apt-get install mpg123
cd ~
mkdir temp
cd temp
git clone https://github.com/RevolutionRobotics/RevvyLauncher.git
git clone https://github.com/RevolutionRobotics/RevvyFramework.git
cp -r RevvyLauncher/src/. "/home/pi/RevvyFramework"
cd RevvyFramework
python3 -m dev_tools.create_package
mkdir -p /home/pi/RevvyFramework/user/ble
mkdir -p /home/pi/RevvyFramework/user/data
cp install/framework.data "/home/pi/RevvyFramework/user/ble/2.data"
cp install/framework.meta "/home/pi/RevvyFramework/user/ble/2.meta"
cd ../..
rm -rf temp
cd RevvyFramework
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
python3 launch_revvy.py
6. Make sure that pip3 is working and it’s able to download packages. If you get errors after starting our framework that packages are missing (e.g. pybleno) pip3 couldn’t install the required packages.
```

I did this using the SD card from the freenova kit with rasbian already installed. I built the basic Revvy robot and was able to drive it just fine with my phone! The one catch is if you reboot or turn off the device, you need to connect to the robot and run "python3 launch_revvy.py" manually. I tried adding this command to /etc/rc.local so that it'd run upon boot, but it didn't work properly.

## Leveraging the Revvy Framework for RobotKitLib
The Revvy code doesn't talk directly to motors or sensors - it talks to a [hardware controller](https://github.com/RevolutionRobotics/RevvyFramework/tree/master/revvy/mcu). While there are [motor](https://github.com/RevolutionRobotics/RevvyFramework/blob/master/revvy/robot/ports/motors/dc_motor.py) and [sensor](https://github.com/RevolutionRobotics/RevvyFramework/blob/master/revvy/robot/ports/sensors/ev3.py) objects, to instantiate them you must first instantiate an object that represents the hardware controller as well as a 'handler' that talks to the controller. Only then can you configure the individual motor and sensor ports.

If you were to clone the RevvyFramework repo and copy the "revvy" folder from it into the same directory as your robotkitlib code, below is the code you can use to instantiate a DC motor on "port 1" of the device. I encourage you to mess around in a python console with this code to see if you can get it to move motors:

```
from revvy.mcu.rrrc_control import RevvyControl
from revvy.mcu.rrrc_transport import RevvyTransport
from revvy.robot.ports.motors.dc_motor import DcMotorController
from revvy.hardware_dependent.rrrc_transport_i2c import RevvyTransportI2CDevice
from revvy.robot.ports.motor import create_motor_port_handler
from revvy.robot.configurations import Motors

# You'll need to do a "pip install smbus2" if it's not already installed
from smbus2 import SMBus

# Instantiate controller. 0x2D is defined as a constant "ROBOT_I2C_ADDRESS" in the Revvy framework.
# Also - apparently "port 1" on the I2C bus is tied to the hardware controller - this is hardcoded in the framework
mcu_controller = RevvyControl(RevvyTransport(RevvyTransportI2CDevice(0x2D,SMBus(1))))

# instantiate motor handler. There is a similar handler for sensors in revvy.robot.ports.sensor
motor_handler = create_motor_port_handler(mcu_controller)

# The handler has a _ports attribute that is a dict of ports keyed on their port number (1-6).
# we can reference a particular port this way. Here it is being configured for the dc_motor:
mh1 = motor_handler._ports[1]
mh1.configure(Motors.RevvyMotor)

# Finally we can instantiate the controller object that actually talks to this motor.
# Not sure why but we have to configure this object as well
mc1 = DcMotorController(mh1, Motors.RevvyMotor['config'])

# Now I can set the speed of the motor. I can also set the power, as well as get these values.
# Check out the code for more details.
mc1.set_speed(10)
```
