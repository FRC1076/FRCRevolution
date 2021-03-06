# python run.py robot.py

import traceback

#Networking and Logging
import logging
import logging.handlers
import os
import socket
#General Imports
import sys
import threading
import time
import random


from networktables import NetworkTables

import buffer
#Robot
#import robot
import pikitlib


logging.basicConfig(level=logging.ERROR)

MODE_COLORS = {'Teleop':0x6600cc, 'Auton':0x6600cc}
DISABLE_COLOR = 0xff0000
ENABLE_COLOR = 0x00ff00

class main():
    def __init__(self):
        """
        Construct robot disconnect, and powered on
        """
        self.r = None
        self.current_mode = ""
        self.disabled = True
        
        
        self.timer = pikitlib.Timer()
        self.connectedIP = None
        self.isRunning = False

        
    def tryToSetupCode(self):
        try:
            # Allows absolute references to work when they're
            # copied over.
            dir = os.path.dirname(os.path.realpath(__file__))
            sys.path.append(f'{dir}/RobotCode')
            from RobotCode.robot import MyRobot
            self.r = MyRobot()

            return True
        except Exception as e:
            logging.critical("Looks like you dont have any code!")
            logging.critical("Send code with deploy.py")
            logging.critical(f"ERROR: {e}")
            logging.critical(traceback.print_tb(e.__traceback__))
            self.catchErrorAndLog(e, False)
            return False
        
        
    def connect(self):
        """
        Connect to robot NetworkTables server
        """
        NetworkTables.initialize()
        NetworkTables.addConnectionListener(self.connectionListener, immediateNotify=True)


    def connectionListener(self, connected, info):
        """
        Setup the listener to detect any changes to the robotmode table
        """
        self.connectedIP = str(info.remote_ip)
        logging.info("%s; Connected=%s", info, connected)
        sd = NetworkTables.getTable("RobotMode")
        self.status_nt = NetworkTables.getTable("Status")
        sd.addEntryListener(self.valueChanged)
   
    def valueChanged(self, table, key, value, isNew):
        """
        Check for new changes and use them
        """
        #print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))
        if(key == "Mode"):
            self.setupMode(value)
        if(key == "Disabled"):
            self.disabled = value
        if(key == "ESTOP"):
            self.quit()

    def setupLogging(self):
        rootLogger = logging.getLogger('')
        rootLogger.setLevel(logging.DEBUG)
        socketHandler = logging.handlers.SocketHandler(self.connectedIP,logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        
        rootLogger.addHandler(socketHandler)
        
    def start(self):

        
        self.isRunning = True
        self.r.robotInit()
        self.setupBatteryLogger()
        self.status_nt.putBoolean("Code", True)

        self.stop_threads = False
        self.rl = threading.Thread(target = self.robotLoop, args =(lambda : self.stop_threads, ))
        self.rl.start() 
        self.setupLogging()
        logging.debug("Starting")
        if self.rl.is_alive():
            logging.debug("Main thread created")

    
    def broadcastNoCode(self):
        self.status_nt.putBoolean("Code", False)


    def setupMode(self, m):
        """
        Run the init function for the current mode
        """
        
        if m == "Teleop":
            self.r.teleopInit()
            self.r.set_led_color(MODE_COLORS['Teleop'])
        elif m == "Auton":
            self.r.autonomousInit()
            self.r.set_led_color(MODE_COLORS['Auton'])

        self.current_mode = m

    def auton(self):
        self.r.autonomousPeriodic()

    def teleop(self):
        self.r.teleopPeriodic()
        
    def disable(self):
        if not self.r.disabled:
            self.r.disable()
            self.r.set_led_color(DISABLE_COLOR)

    def enable(self):
        if self.r.disabled:
            self.r.enable()
            self.r.set_led_color(MODE_COLORS.get(self.current_mode,ENABLE_COLOR))

    def setupBatteryLogger(self):
        self.battery_nt = NetworkTables.getTable('Battery')

        # Todo: get battery from revlib
        #self.ai = pikitlib.analogInput(2)
       

    def sendBatteryData(self):
        self.r.update_status()
        self.battery_nt.putNumber("Voltage", self.r.battery)

    def quit(self):
        logging.info("Quitting...")
        self.stop_threads = True
        self.rl.join() 
        self.disable()
        sys.exit()

    def catchErrorAndLog(self, err, logErr=True):
        if logErr:
            logging.critical("Competition robot should not quit, but yours did!")
            logging.critical(err)
            logging.critical(traceback.print_tb(err.__traceback__))
                    

        try:
            self.broadcastNoCode()
        except AttributeError:
            #if there is no code, broadcasting wont work
            #TODO: rework how broadcasting works so this isnt required 
            pass
        


        #logging.critical("Resetting ()...")
        sys.exit()
            
    def robotLoop(self, stop):
        bT = pikitlib.Timer() 
        bT.start()
        while not stop():
            
            if bT.get() > 0.2:
                self.sendBatteryData()
                bT.reset()

            if not self.disabled:
               
                # need to physically enable the bot
                # if it was previously disabled
                self.enable()

                self.timer.start()
                try:
                    if self.current_mode == "Auton":
                        self.auton()
                    elif self.current_mode == "Teleop":
                        self.teleop()
                except Exception as e:
                    self.catchErrorAndLog(e)
                    break
                self.timer.stop()
                ts = 0.02 -  self.timer.get()
                
                self.timer.reset()
                if ts < -0.5:
                    logging.critical("Program taking too long!")
                    self.quit()
                elif ts < 0:
                    logging.warning("%s has slipped by %s miliseconds!", self.current_mode, ts * -1000)
                else:        
                    time.sleep(ts)
            else:
                self.disable()

        self.disable()

            

    def debug(self):
        self.disabled = False
        self.start()
        self.setupMode("Teleop")

    
m = main()
m.connect()

if m.tryToSetupCode():
    m.start()
else:
    time.sleep(0.2)
    try:
        m.broadcastNoCode()
    except:
        print("Either no code or error in robot code")
        print("Waiting...")
    sys.exit(1)

