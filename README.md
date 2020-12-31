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


## Installation
Here is how to install this code on your Revolution Robotics kit.

### What you will need
For initial installation:
* Your robot's brain, connected and powered up
* USB keyboard
* HDMI-capable monitor/display
* Mini-USB to USB-A adapter
* Mini (or whatever) HDMI to normal HDMI adapter
* HDMI cable
* Administrative access to your home router (not strictly necesary, but highly encouraged)

For programming and driving the robot:
* A USB xbox controller
* A laptop with the following capabilities:
  * Can run python (basically this means a Windows, Mac, or Linux machine, no Chromebooks)
  * Has a USB port you can plug the xbox controller into

