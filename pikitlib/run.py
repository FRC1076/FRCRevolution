# python run.py robot.py

import random

#General Imports
import sys
import time
import threading

#Robot
import revvy_robot
import pikitlib
from networktables import NetworkTables

#Networking and Logging
import logging
import logging.handlers


logging.basicConfig(level=logging.DEBUG)


class main():
    def __init__(self):
        """
        Construct robot disconnect, and powered on
        """
        self.r = revvy_robot.RevvyRobot()
        self.current_mode = ""
        self.disabled = True

        self.timer = pikitlib.Timer()
        
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
        print(info, "; Connected=%s" % connected)
        logging.info("%s; Connected=%s", info, connected)
        sd = NetworkTables.getTable("RobotMode")
        sd.addEntryListener(self.valueChanged)

    def valueChanged(self, table, key, value, isNew):
        """
        Check for new changes and use them
        """
        print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))
        if(key == "Mode"):
            self.setupMode(value)
        if(key == "Disabled"):
            self.disabled = value
        if(key == "ESTOP"):
            self.quit()

    def setupLogging(self):
        rootLogger = logging.getLogger('')
        rootLogger.setLevel(logging.DEBUG)
        socketHandler = logging.handlers.SocketHandler(str(NetworkTables.getRemoteAddress()),
            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        
        rootLogger.addHandler(socketHandler)
        
    def start(self):    
        self.r.robotInit()
        self.setupBatteryLogger()
        self.stop_threads = False
        self.rl = threading.Thread(target = self.robotLoop, args =(lambda : self.stop_threads, )) 
        self.rl.start() 
        if self.rl.is_alive():
            print("Main thread created")
            logging.debug("Main thread created")

    def broadcastNoCode(self):
        self.status_nt.putBoolean("Code", False)


    def setupMode(self, m):
        """
        Run the init function for the current mode
        """
        
        if m == "Teleop":
            self.r.teleopInit()
        elif m == "Auton":
            self.r.autonomousInit()

        self.current_mode = m
       
        self.rl.start()

    def auton(self):
        self.r.autonomousPeriodic()

    def teleop(self):
        self.r.teleopPeriodic()
        
    def disable(self):
        self.r.disable()

    # TODO: Implement battery read class
    def setupBatteryLogger(self):
        self.battery_nt = NetworkTables.getTable('Battery') 

    def sendBatteryData(self):
        self.battery_nt.putNumber("Voltage", random.random())

    def getDriverstationData(self):
        self.battery_nt.getNumber("Driver",-1)

    def quit(self):
        logging.info("Quitting...")
        self.stop_threads = True
        self.rl.join() 
        self.disable()
        sys.exit()
            
    def robotLoop(self, stop):
        bT = pikitlib.Timer() 
        bT.start()
        driver = 0
        while not stop():
            
            if bT.get() > 0.2:
                self.sendBatteryData()
                new_driver = self.getDriverstationData()
                if new_driver != driver:
                    driver = new_driver
                else:
                    logging.critical("Lost connection with driverstation!")
                    m.disable()

                bT.reset()

            if not self.disabled:
                self.timer.start()
                if self.current_mode == "Auton":
                    self.auton()
                elif self.current_mode == "Teleop":
                    self.teleop()
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
        #self.mainLoopThread()

    
            





if __name__ == "__main__":
   
    m = main()
    try:
        m.connect()
        m.start()
    except Exception as e:
        m.disable()
        raise(e)

    
