# -*- coding: utf-8 -*-
"""
Created on Sat Jan 10 20:37:06 2015

@author: ouuuutchi
"""
import spidev
from time import sleep

class SPI():
    #init the chip 
    def __str__(self):
        listMsg = ["1: ChipSelect/ShutDown input (pins 24)","2: Channel 0 Analog input(to the sensor)",
                   "3: Channel 1 Analog unput(to the sensor else ground)","4: VSS (ground 4,6,..)",
                   "5: Din (MOSI, 19)","6: Dout (MISO, 21)","7: CLK (SCLK, 23)","8: VDD (3.3V, 1)"]
        msg = "Heres to connection instructions for a MCP-3002 chip"
        for i in listMsg:
            msg = msg + '\n' + i
        return msg
    def Get_Voltage(self,channel=0):
        raw = self.Read_Analog(channel)
        percent = raw / 1023.0
        #the value return by the MCP3002 is a interger between 0 and 1023
        voltage = percent * 3.3
        return voltage
    def Read_Analog(self,channel):
        assert channel in (1,0)   
        #open the spi
        spi = spidev.SpiDev()
        spi.open(0,0)
        command = [1, (2 + channel) << 6, 0]
        reply = spi.xfer2(command)
        value = reply[1] & 31
        value = value << 6
        value = value + (reply[2] >> 2)
        spi.close()
        return value
    def Read_Potentiometer(self,channel):
        spi = spidev.SpiDev()
        spi.open(0,0)
        command = [1,128,0]
        reply = spi.xfer2(command)
        #Parse reply 10 bits from 24 bits package
        data = reply[1] & 31
        data = data << 6
        data = data +(reply[2] >> 2)
        spi.close()
        return data
