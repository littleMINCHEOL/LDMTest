#!/usr/bin/env python
from ina219 import INA219
from ina219 import DeviceRangeError
from time import sleep

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2
ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=0x40)
ina.configure(ina.RANGE_16V)

def read():
 try:
    print("BUS Current: %.3f mA" % ina.current())
    print("BUS Voltage: %.3f V" % ina.voltage())
 except DeviceRangeError as e:
    print(e)

while 1:
    read()
    sleep(15)
