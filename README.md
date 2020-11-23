# FRCRevolution
Hack revolution robotics platform to run our RobotKitLib

Revolution Robotics kit is uses raspbian on PiZero to do its thing.
We'd like to see if we can run our RobotKitLib on it instead.    This would permit
us to unify our codebase, and allow us to usr competition style programming
on the Revolution Robotics projects.

There is the process described here to recreate the SD-card for the RR unit starting
on a raspbian base.   We should be able to look at this code (if code is available)
to maybe figure out which pins on the PiZero are being used to drive motors, etc...

https://revolutionrobotics.org/pages/robot-framework-on-raspbian

Some unanswered questions so far.
  Does the RR bot have Wifi connection, or could we tap into the USB port to add such
  connectivity.    Wireless is pretty essential for what we are trying to do.    If
  there is only bluetooth, we have the option to run some form of the driverstation
  *on* the RR bot, and connect to it with a bluetooth controller.
  
