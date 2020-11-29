## Hacking the Robot
The RR robot has a Raspberry Pi under the hood and is running Raspbian. You can take out the SD card, put it on another Pi, and it will boot. However, the default username/password has been changed by Revolution Robotics. Because we'd rather not mess with the SD card that comes with these bots anyway, the ideal thing to do is get another SD card with Raspbian on it, put code on it that can talk to the robot, and put that card into the RR's Pi instead. 

Revolution Robotics [publishes instructions](https://revolutionrobotics.org/pages/robot-framework-on-raspbian) on how to do this with their own software, however it is slightly incorrect. Below are the instructions with the one tweak needed to actually make it work:

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
```

I followed the above steps using the SD card from the freenova kit with rasbian already installed. I then built the basic Revvy robot, installed the SD card into it, and was able to drive the robot with my phone. What's cool about this is that you can see log messages in the console when you interact with the robot - I found them helpful when trying to figure out how the code works. The one catch is if you reboot or turn off the device, you need to connect to the robot and run "python3 launch_revvy.py" manually. I tried adding this command to /etc/rc.local so that it'd run upon boot, but it didn't work properly - I didn't spend a ton of time getting the framework to launch on boot but I'm sure there's a way.

## Leveraging the Revvy Framework for RobotKitLib
The Revvy code doesn't talk directly to motors or sensors - it talks to a [hardware controller](https://github.com/RevolutionRobotics/RevvyFramework/tree/master/revvy/mcu). While there are [motor](https://github.com/RevolutionRobotics/RevvyFramework/blob/master/revvy/robot/ports/motors/dc_motor.py) and [sensor](https://github.com/RevolutionRobotics/RevvyFramework/blob/master/revvy/robot/ports/sensors/ev3.py) objects, to instantiate them you must first instantiate an object that represents the hardware controller as well as a 'handler' that talks to the controller. Only then can you configure the individual motor and sensor ports and communicate with them.

If you were to clone the [RevvyFramework repo](https://github.com/RevolutionRobotics/RevvyFramework) and copy the "revvy" folder from it into the same directory as your robotkitlib code, below is the code you can use to instantiate a DC motor on port "M1" of the device. I encourage you to mess around in a python console before trying to incorporate this into other code.

Note that to use the revvy code you'll still need to follow steps 1-4 in the above "installing the Revvy framework", and you'll also need to do "sudo apt-get install mpg123" if you want to leverage the [sound](https://github.com/RevolutionRobotics/RevvyFramework/blob/6a59a996cb2694385f3ff5e8524bc5f721eeeb48/revvy/hardware_dependent/sound.py#L10) portions of code. 

```
from revvy.mcu.rrrc_control import RevvyControl
from revvy.mcu.rrrc_transport import RevvyTransport
from revvy.robot.ports.motors.dc_motor import DcMotorController
from revvy.hardware_dependent.rrrc_transport_i2c import RevvyTransportI2CDevice
from revvy.robot.ports.motor import create_motor_port_handler
from revvy.robot.configurations import Motors

# You'll need to do a "pip install smbus2" if it's not already installed
from smbus2 import SMBus

# Instantiate controller. 0x2D is defined as constant "ROBOT_I2C_ADDRESS" in the Revvy framework.
hw_controller = RevvyControl(RevvyTransport(RevvyTransportI2CDevice(0x2D,SMBus(1))))

# instantiate motor handler. There is a similar handler for sensors in revvy.robot.ports.sensor
motor_handler = create_motor_port_handler(hw_controller)

# The handler has a _ports attribute that is a dict of ports keyed on their port number (1-6).
# we can reference a particular port this way. A port must be configured for a particular motor
# type for it to work properly.
mh1 = motor_handler._ports[1]
mh1.configure(Motors.RevvyMotor)

# Now we can instantiate the object that actually controls this motor.
mc1 = DcMotorController(mh1, Motors.RevvyMotor['config'])

# Set the speed of the motor to 10. Check out the DCMotorController object's documentation
# for other things you can do (set/get speed, power, etc)
mc1.set_speed(10)
```

Note that if you try to execute code like this while the revvy framework is running (by that I mean you installed the revvy framework and are currently running 'launch_revvy.py'), it will error out. Apparently only one code instance can talk to the hardware controller at a time.
