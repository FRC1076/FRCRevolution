# FRCRevolution
Hack revolution robotics platform to run our RobotKitLib

## Overview
This repo attempts to create an FRC-like development
platform for the Robotics Revolution Challenge Kit.

The repo is basically a kludge of two other repos:
* The [RevvyFramework](https://github.com/RevolutionRobotics/RevvyFramework) repo
is used to interact with the various components of the kit (motors, sensors, etc)
* The [RobotKitLib](https://github.com/FRC1076/RobotKitLib) repo is used for Driverstation,
code pushes to the robot, and xboxcontroller functions.

Files from the above repos have been hand-copied into this one and modified as necessary
to make stuff work. This is not a good strategy for creating sustainable/supportable
code, but our goal was getting basic functionality done quickly. Any improvements are welcome!

## Development
As of January 2021, you can use this code to:
* See/get data from the xboxcontroller (buttons pressed, joystick positions).
* Set motors to various speeds.
* Assign motors to groups and do very simple arcade or tank drives.
* Get data from the distance sensor (in the code it's called "ultra")
* Get a true/false value from the "bumper" button.
* Play sounds.
* Set lights on the LED ring (but only for 5 minutes then this breaks - a known issue :( )
* Get data from the built in accelerometer

As of January 2021, this code does NOT:
* Leverage the Revvy Framework's "drivetrain" code (which appears to be the only thing they currently use the accelerometer for).
* Leverage any bluetooth functionality.
* Leverage any of Revvy Framework's multi-threaded "scripting" functionality (this is how all the coding you do from their phone app works).

### What you will need

To run this code on your robot you will need:
* Your robot's brain
* An SD Card with this software pre-loaded on it
* A USB xbox controller
* A laptop with the following capabilities:
  * Can run python (basically this means a Windows, Mac, or Linux machine, no Chromebooks)
  * Has a USB port you can plug the xbox controller into

To do the initial software installation you will also need:
* USB keyboard
* HDMI-capable monitor/display
* Micro USB to USB-A adapter
* Mini HDMI to normal HDMI adapter
* HDMI cable
* Administrative access to your home router (not strictly necesary, but highly encouraged)

### Installation Steps

1. Get out the Revolution Robotics [brain](https://revolutionrobotics.org/pages/getting-to-know-your-robot-brain).
2. Remove the SD card that came with the kit, and insert your new card.
3. Using a Mini-USB to USB-A adapter, conect a keyboard to the micro USB OTG Data port (NOT the charging port!) on the brain.
4. Using a Mini HDMI to HDMI adapter, connect a monitor to the Mini HDMO port on the brain.
5. Power on the brain.
6. Log into Raspbian and launch the console. Type in "sudo raspi-config" and configure the Pi for your wifi.
7. Now that you've configured Raspbian for your wifi, you should have internet access (woot!). Get the IP address assigned to the robot and save it
```
ip addr
```
(tbd)
Pull the latest code and restart this software:
```
cd ~/FRCRevolution
git pull
sudo systemctl restart robotrunner
```
8. On your laptop, clone the repo as well and install the requirements.
(tbd)
9.
