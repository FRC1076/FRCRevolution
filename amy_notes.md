# Hacking the Robot
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

I did this using the SD card from the freenova kit and everything worked!

# How the Revvy Framework does hardware control
The Revvy code doesn't talk directly to motors or sensors - it talks to a [hardware controller](https://github.com/RevolutionRobotics/RevvyFramework/tree/master/revvy/mcu). While there are [motor](https://github.com/RevolutionRobotics/RevvyFramework/blob/master/revvy/robot/ports/motors/dc_motor.py) and [sensor](https://github.com/RevolutionRobotics/RevvyFramework/blob/master/revvy/robot/ports/sensors/ev3.py) objects, to instantiate them you must first instantiate an object that represents the hardware controller as well as a 'handler' that talks to the controller.

If you were to clone the RevvyFramework repo and copy it into 
