#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 NXEZ.COM.
# http://www.nxez.com
#
# Licensed under the GNU General Public License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.gnu.org/licenses/gpl-2.0.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# tutorials url: http://shumeipai.nxez.com/2015/09/21/saks-diy-tutorials-cpu-temperature-display-and-alarm.html

__author__ = 'Spoony'
__license__  = 'Copyright (c) 2015 NXEZ.COM'

from sakshat import SAKSHAT
from sakspins import SAKSPins as PINS
import time
import commands
import socket
import RPi.GPIO as GPIO

#Declare the SAKS Board
SAKS = SAKSHAT()
keepBeep=True
tcp_client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)


GPIO.setmode(GPIO.BCM)

DS = 6
SHCP = 19
STCP = 13

def init():
    GPIO.setup(DS, GPIO.OUT)
    GPIO.setup(SHCP, GPIO.OUT)
    GPIO.setup(STCP, GPIO.OUT)

    GPIO.output(DS, GPIO.LOW)
    GPIO.output(SHCP, GPIO.LOW)
    GPIO.output(STCP, GPIO.LOW)

def writeBit(data):
    GPIO.output(DS, data)

    GPIO.output(SHCP, GPIO.LOW)
    GPIO.output(SHCP, GPIO.HIGH)

#写入8位LED的状态
def writeByte(data):
    for i in range (0, 8):
        writeBit((data >> i) & 0x01)
    #状态刷新信号
    GPIO.output(STCP, GPIO.LOW)
    GPIO.output(STCP, GPIO.HIGH)

#在检测到轻触开关触发时自动执行此函数
def tact_event_handler(pin, status):  
    if pin == PINS.TACT_RIGHT and status == True:
        tcp_client.send("OK")
        SAKS.buzzer.off()   
        global keepBeep
        keepBeep=False     
        print "TACT_RIGHT"        

def get_cpu_temp():
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp) / 1000
    # Uncomment the next line if you want the temp in Fahrenheit
    #return float(1.8*cpu_temp)+32

def get_gpu_temp():
    gpu_temp = commands.getoutput( '/opt/vc/bin/vcgencmd measure_temp' ).replace( 'temp=', '' ).replace( '\'C', '' )
    return float(gpu_temp)
    # Uncomment the next line if you want the temp in Fahrenheit
    # return float(1.8* gpu_temp)+32

if __name__ == "__main__":    
    SAKS.tact_event_handler = tact_event_handler
    init()
    while True:
        try:
            tcp_client.connect(("172.16.141.158",60000))
            break
        except Exception, ex:
            SAKS.buzzer.off()   
            keepBeep=False 
            SAKS.digital_display.show("2222")
            time.sleep(2)              
    SAKS.digital_display.show("0000")
    while True:
        try:
            if True:
                SAKS.digital_display.show("0000")
                msg=tcp_client.recv(1024)
                if msg.decode('gbk')=="SOS":
                    keepBeep=True
                    SAKS.digital_display.show("1111")                       
                    print "SOS" 
                    
                    while keepBeep:
                        for i in [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]:
                            writeByte(i)
                            time.sleep(0.1)
                        SAKS.buzzer.beepAction(0.02,0.2,3)   
                        time.sleep(1)
                        if keepBeep==False:
                            SAKS.buzzer.off()
                            break                   
        except Exception, ex:
            SAKS.digital_display.show("2222")
            SAKS.buzzer.off()   
            keepBeep=False 
            while True:
                try:
                    tcp_client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    tcp_client.connect(("172.16.141.158",60000))
                    SAKS.digital_display.show("0000")     
                    break
                except Exception, ex:
                    time.sleep(2) 
        time.sleep(1)

