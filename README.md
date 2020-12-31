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

### What you will need

To run this code on your robot you will need:
* Your robot's brain
* An SD Card with Raspbian on it (prob should pre-build these w/the software on it)
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
6. Log into Raspbian and launch the console. Type in "sudo raspi-config" and configure the following things:
(to be continued)
7. Now that you've configured Raspbian for your wifi, you should have internet access (woot!). Pull the latest version of this repo with the following console command:
(tbd)
8. On your laptop, clone the repo as well and install the requirements.
(tbd)
