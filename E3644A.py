#!/usr/bin/env python

import serial
import time
from ina219 import INA219
from ina219 import DeviceRangeError

ser=serial.Serial("/dev/ttyUSB0")
ser.write("OUTPUT ON\r\n")

#time.sleep(3)

ser.write("*IDN?\r\n")
r_msg1=ser.readline()
print(r_msg1)

#ser.write("VOLT 15\r\n")
ser.write("SYSTem:ERRor?\r\n")
r_msg=ser.readline()
print(r_msg)

#time.sleep(10)

#ser.write("OUTPUT OFF\r\n")

ser.close()


def read():
 ina = INA219(shunt_ohms=0.1, max_expected_amps=0.6, address=0x40)
 ina.configure()

 print("Bus VOL : %.3f [V]" % ina.voltage())
 try:
    print("bus current : %.3f [mA]" % ina.current())
    print("power: %.3f [mW]" % ina.power())
    print("Shunt voltage: %.3f [mV]" % ina.shunt_voltage())
 except DeviceRangeError as e:
    print(e)

if __name__=="__main__":
 read()
