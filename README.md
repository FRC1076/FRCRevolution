# FRCRevolution
Hack revolution robotics platform to run our RobotKitLib

Revolution Robotics kit runs its Revvy framework on PiZero to do its thing.
We'd like to see if we can run our RobotKitLib on it instead.    This would permit
us to unify our codebase, and allow us to usr competition style programming
on the Revolution Robotics projects.

There is the process described here to recreate the SD-card for the RR unit starting
on a raspbian base.   We should be able to look at this code (if code is available)
to maybe figure out which pins on the PiZero are being used to drive motors, etc...

https://revolutionrobotics.org/pages/robot-framework-on-raspbian

RR brain using PiZero W (where W means Wifi, so we are good for Wifi)

Some unanswered questions so far.  (and kind of critical)
  
  I imagine the PiZero has a subset of capabilities of the Pi3B+, but if there is something
  the it is providing that we don't have on the 3B+, we might have troubles.
  
  Is there enough memory on the PiZero to run our the RobotKitLib?
    Someone can investigate this.
  
  What other things should we look at before spending a bunch of time on trying to hack it.
  
  Materials needed for the Hacking Effort
  
    * mini-HDMI cable  to your monitor
    * micro-usb OTG (on the go) dongle (that will let you plug in a keyboard)
    * usb-hub if you want keyboard and mouse (or, I guess a single wireless keyboard mouse
      would work.
      matthew might have one of these in a software tote somewhere if you don’t have one)
    * Raspian image with the RobotKitLib build on it.

The RR folks might be helpful with the hack effort, for example to let you know what PWM chip they might be using
to drive the motors?
But you might find that information in the code, or from their tech folks if they are forthcoming.

   * There may be motor drivers connected directly to Pi GPIO pins, in which case the the Pi
     might be doing PWM (generating the waveform for the drivers(amps)).     There is python library
     to do that.  (although it doesn't have a great reputation)
   * There could be a PWM chip connected to the I2C bus on the Pi, in which case the commands
     would be sent on that bus to drive motors.  (different channels on the chip would drive different
     motors)   See:  https://github.com/FRC1076/RobotKitLib/blob/main/pikitlib/pikitlib/pca_motor.py
     for an example of the interface to a PWM chip.
   * It could be something else.  I have limited knowledge about these things.

Then you can start writing little python snippets to see if you can spin motors.


  
  
  
