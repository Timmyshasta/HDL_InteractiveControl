#Headlamp used with angle sensor for interactive adaptive headlights
#EE Systems Team
#Tim Medina#

import can
import can.interfaces
from can.interfaces import Bus
from can import Message
import subprocess
from subprocess import call
import time 
import datetime
import threading
import keyboard
import RPi.GPIO as GPIO

bus = None
hld = None
Led_Blink = False
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class HLD_Control(): # Control class for the headlamps
    def __init__(self):

        self.HLM_COMMAND_ID = 0x400

        #Defined initial state of the signals

        
                 
