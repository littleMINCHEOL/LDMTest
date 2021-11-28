#!/sur/bin/python

from subprocess import check_output
from  re import findall
import sys
import os

def get_GPU():
	temp = check_output(["vcgencmd","measure_temp"]).decode()
	temp = float(findall('\d+\.\d+', temp)[0])
	return(temp)

def get_CPU():
	stream = os.popen('cat /sys/class/thermal/thermal_zone0/temp')
	OUT = stream.read()
	OUT = float(OUT)/1000
	return(round(OUT, 1))

print("GPU_TEMP : ")
print(get_GPU())
print("CPU_TEMP : ")
print(get_CPU())

try :
	pass
except KeyboardInterrupt:
	pass
finally:
	pass
