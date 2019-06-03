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


class HLD_Control(): # Control Class for the headlamps
    def __init__(self):

        self.HLM_COMMAND_ID = 0x400

        #### Defined initial state of the signals ####

        #Signals in Byte 1
        self.HLML_LAMPCMD_PARK = 0
        self.HLMR_LAMPCMD_PARK = 0
        self.HLM_LAMPCMD_DRL = 0
        self.HLML_LAMPCMD_SUPPRESS_PARK = 0
        self.HLMR_LAMPCMD_SUPPRESS_PARK = 0
        self.HLM_LAMPCMD_BEAMS = 0
        self.HLM_LAMPSET_SWIVEL_ENABLE = 1

        #Signals in Byte 2
        self.HLM_VehicleSpeed_Validity = 1

        #Signals Byte 2 -> 3
        self.HLM_VehicleSpeed = 15 # Keep at 15mph
        self.HLM_VehicleSpeed = int(((self.HLM_VehicleSpeed + 125)/ 0.125)) #Offset & Factor for vehicle speed

        #Signals Byte 4 & 5
        self.HLM_SteeringWheelAngle = 0

        #Signals Byte 6
        self.HLM_SteeringWheelAngleRate = 800
        self.HLM_SteeringWheelAngleRate = int((self.HLM_SteeringWheelAngleRate/4)) #Offset & Factor for angle rate

        #Signals Byte 7
        self.HLM_ActuatedGear = 3 #Vehicle in "D"
        self.HLM_NM = 1
        self.HLM_COMMAND_ALIVE_COUNT = 0
        

    def build_msg(self):
        self.mask1 = 0x7F00
        self.mask2 = 0xFF
        self.mask3 = 0xFF00

        #Build message for Byte 0
        self.byte0 = self.HLML_LAMPCMD_PARK | (self.HLMR_LAMPCMD_PARK <<1)

        #Build message for Byte 1 no message in byte 1. Define as 0
        self.byte1 = 0
        #print(byte1)

        
        #Build message for Byte 2 
        self.data1_HLMVehicleSpeed = self.HLM_VehicleSpeed
        self.data1_HLMVehicleSpeed = self.data1_HLMVehicleSpeed & self.mask1
        self.byte2 = self.data1_HLMVehicleSpeed >> 8
        self.byte2 = self.byte2 | (self.HLM_VehicleSpeed_Validty  <<7)
        #print(byte2)
        
        #Build message for Byte 3 
        self.data2_HLMVehicleSpeed = self.HLM_VehicleSpeed
        self.data2_HLMVehicleSpeed = self.HLM_VehicleSpeed & self.mask2
        self.byte3 = self.data2_HLMVehicleSpeed
        #print(hex(byte3))

        #Build message for Byte 4 & 5 
        self.data1_HLM_SteeringWheelAngle = self.HLM_SteeringWheelAngle
        self.data1_HLM_SteeringWheelAngle = self.HLM_SteeringWheelAngle & self.mask3
        self.byte4 = self.data1_HLM_SteeringWheelAngle >> 8
        #print(byte4)
        
        self.data2_HLM_SteeringWheelAngle = self.HLM_SteeringWheelAngle
        self.data2_HLM_SteeringWheelAngle = self.HLM_SteeringWheelAngle & self.mask2
        self.byte5 = self.data2_HLM_SteeringWheelAngle
        #print(byte5)
        
        ####Byte 6 
        self.byte6 = self.HLM_SteeringWheelAngleRate

        ####Byte 7 
        self.HLM_COMMAND_ALIVE_COUNT
        #print(HLM_COMMAND_ALIVE_COUNT)
        self.HLM_COMMAND_ALIVE_COUNT = self.HLM_COMMAND_ALIVE_COUNT + 1
        self.HLM_COMMAND_ALIVE_COUNT = self.HLM_COMMAND_ALIVE_COUNT % 4
        
        self.byte7 = self.HLM_ActuatedGear | (self.HLM_NM <<4)
        self.byte7 = self.byte7 | (self.HLM_COMMAND_ALIVE_COUNT<<6)
        #print(byte7)

        self.big_byte = [self.byte0,self.byte1,self.byte2,self.byte3,self.byte4,self.byte5,self.byte6,self.byte7]
        self.msg = can.Message(arbitration_id=self.HLM_COMMAND_ID, extended_id = False, data=self.big_byte)
        #print(msg)
        return self.msg

    def turn_signal_on(self):
        GPIO.output(10,True)
        
    def turn_signal_off(self):
        GPIO.output(10,False)
        
    def turn_signal(self):
        global Led_Blink
        while True:
            self.turn_signal_off()
            while Led_Blink == True:
                self.turn_signal_on()
                time.sleep(.5)
                self.turn_signal_off()
                time.sleep(.5)
                
    def turn_off_beam(self):
        self.HLM_LAMPCMD_BEAMS = 0
        
    def turn_on_beam(self):
        self.HLM_LAMPCMD_BEAMS = 1
    
    def turn_on_DRL(self):
        self.HLM_LAMPCMD_DRL = 1
    
    def turn_off_DRL(self):
        self.HLM_LAMPCMD_DRL = 0
    
    def high_beam(self):
        self.HLM_LAMPCMD_BEAMS= 2
    
    def flash_to_pass(self):
        self.HLM_LAMPCMD_BEAMS = 3
    
    def actuated_gear_park(self):
        self.HLM_ActuatedGear = 0
        
    def actuated_gear_reverse(self):
        self.HLM_ActuatedGear = 1
        
    def actuated_gear_neutral(self):
        self.HLM_ActuatedGear = 2
        
    def steering_wheel_angle(self,x):
        self.HLM_SteeringWheelAngle = x
    
    def vehicle_speed(self):
        self.HLM_VehicleSpeed()

def transmit_thread():
    #print('Start transmit')
    while True:
        try:
            msg = hld.build_msg()    
            bus.send(msg)
            time.sleep(.001)
        except:
            pass        
        
