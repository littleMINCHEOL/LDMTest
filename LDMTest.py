from tkinter import*
import RPi.GPIO as GP
import tkinter.ttk as ttk
import serial
import os
from os import path
import time
from ina219 import INA219
from ina219 import DeviceRangeError
import smbus
from subprocess import check_output
from re import findall
import sys
from tkinter import messagebox
from tkinter import filedialog

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

Relay1 = 5
Relay2 = 6
Relay3 = 13
Relay4 = 19
Relay5 = 26
Relay6 = 16
Relay7 = 20
Relay8 = 21

LED1 = 17
LED2 = 27
LED3 = 22
LED4 = 18
LED5 = 23
LED6 = 24
LED7 = 25
LED8 = 12

ON = 1
OFF = 0

GP.setmode(GP.BCM)
GP.setup(Relay1,GP.OUT)
GP.setup(Relay2,GP.OUT)
GP.setup(Relay3,GP.OUT)
GP.setup(Relay4,GP.OUT)
GP.setup(Relay5,GP.OUT)
GP.setup(Relay6,GP.OUT)
GP.setup(Relay7,GP.OUT)
GP.setup(Relay8,GP.OUT)

GP.setup(LED1,GP.OUT)
GP.setup(LED2,GP.OUT)
GP.setup(LED3,GP.OUT)
GP.setup(LED4,GP.OUT)
GP.setup(LED5,GP.OUT)
GP.setup(LED6,GP.OUT)
GP.setup(LED7,GP.OUT)
GP.setup(LED8,GP.OUT)

window = Tk()
window.title("LDM TEST")
#w=window.winfo_screenwidth()
#h=window.winfo_screenheight()
#window.geometry("%dx%d"%(w, h))
window.geometry("500x500+600+250")

if path.exists("/dev/ttyUSB0") == True:
    ser=serial.Serial("/dev/ttyUSB0")
    print("connection ttyUSB0")
else:
    window.withdraw()    #deiconify() 
    okey = messagebox.showerror("Error MessageBox", "Please check the USB0 connection")
    if okey == "ok":
        sys.exit("error : plese connection USB0")

try:#LCD_Display
    bus.read_byte(39)
    print(hex(39))
    print("connection LCD_Display")
except:
    window.withdraw()    #deiconify() 
    okey = messagebox.showerror("Error MessageBox", "Please check the LCD_Display connection")
    if okey == "ok":
        sys.exit("error : plese connection LCD_Display")
    pass

try:#INA219
    bus.read_byte(64)
    print(hex(64))
    print("connection INA_219")
    ina1 = INA219(shunt_ohms=0.1, max_expected_amps=0.6, address=0x40)
    ina1.configure(bus_adc=ina1.ADC_128SAMP, shunt_adc=ina1.ADC_128SAMP)
except:
    window.withdraw()    #deiconify() 
    okey = messagebox.showerror("Error MessageBox", "Please check the INA219 connection")
    if okey == "ok":
        sys.exit("error : plese connection INA219")
    pass

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
  
def lcd_byte(bits, mode):
  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)
  
def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
    
def Vol():
    CalV = float(input_text.get())+float(DVoltage)
    Volctrl="VOLT"+' '+str(CalV)+"\r\n"
    print(Volctrl)
    ser.write(Volctrl.encode('ascii'))
    txt_out.configure(text=str(CalV))

def DVol():
    global DVoltage
    DVoltage = input_DV.get()
    print(DVoltage)
    txt_Dout.configure(text=input_DV.get())
    
def MeaCur():
    time.sleep(0.2)
    meaV.configure(text="voltage : %.2f [V]"%ina1.voltage())
    meaC.configure(text="Current : %.2f [mA]"%ina1.current())
    meaP.configure(text="Power : %.2f [mW]"%ina1.power())
    meaSV.configure(text="  Shunt voltage : %.2f [mV]"%ina1.shunt_voltage())
    lcd_init()
    STR1="Current:%.2f mA" % ina1.current()
    STR2="Voltage:%.2f V" % ina1.voltage() 
    lcd_string(STR1,LCD_LINE_1)
    lcd_string(STR2,LCD_LINE_2)
    
def Write_Result():
    now = time.localtime()
    dt="< %04d-%02d-%02d > "%(now.tm_year,now.tm_mon,now.tm_mday)
    tt="< %02d:%02d:%02d > "%(now.tm_hour,now.tm_min,now.tm_sec)
    f = open("/home/pi/currentResult/Result.txt", "a")
    f.write(dt)
    f.write(tt+"\r\n")
    f.write("seting Voltage :"+' '+input_text.get()+" [V]"+"\r\n")
    f.write("Voltage : %.2f [V], " % ina1.voltage())   #전압
    f.write("current : %.2f [mA], " % ina1.current())  #전류
    f.write("power: %.2f [mW], " % ina1.power())   #전력
    f.write("Shunt voltage: %.2f [mV]\r\n\r\n" % ina1.shunt_voltage())
    f.close()
    
def WR_Reset():
    f = open("/home/pi/currentResult/Result.txt", "w")
    f.write("                  <<<<<<<<<<<<<<<< CURRENT RESULT >>>>>>>>>>>>>>>\r\n")
    f.close()
    
def ResultC():
    filename = filedialog.askopenfilename(initialdir='/home/pi/currentResult', title='Result_TXT', filetypes=(('txt file','.txt'),('all file','*.*')))
    #Rfile=Label(window, text=window.filename).grid(row=11, column=2)
    newWindow=Toplevel(window)
    newWindow.title("Current Result")
    newWindow.geometry("700x490+600+250")
    textR = Text(newWindow, height=30, width=90)
    data=open(filename,'rt',encoding="utf-8")
    textR.delete('1.0',END)
    textR.insert(INSERT,data.read())
    textR.grid(row=0, column=0)

def click(event):
    global comboR
    comboR=int(combo.get())
    print(comboR)

values=["1","2","3","4","5","6","7","8"]
combo=ttk.Combobox(window, width=10, height=5, value=values)
combo.grid(row=1, column=0)
combo.set("Relay Select")
combo.bind("<<ComboboxSelected>>",click)

Rel=Label(window, text="Relay Ctrl")
Rel.grid(row=0, column=0)
b1 = Button(window, text="ON", command=lambda: call1(comboR,ON))
b1.grid(row=0, column=1)
b2 = Button(window, text="OFF", command=lambda: call1(comboR,OFF))
b2.grid(row=0, column=2)

POW=Label(window, text="Rpower suplly ON/OFF")
POW.grid(row=2, column=0)
b3 = Button(window, text="ON", command=lambda: PowONOFF(ON))
b3.grid(row=2, column=1)
b4 = Button(window, text="OFF", command=lambda: PowONOFF(OFF))
b4.grid(row=2, column=2)

VOL=Label(window, text="Rpower suplly Voltage")
VOL.grid(row=3, column=0)
input_text=StringVar()
input_text_enter=Entry(window, width=10, textvariable=input_text)
input_text_enter.grid(row=4, column=0)
b5 = Button(window, text="Enter", command=Vol)
b5.grid(row=4, column=1)
Vollimit = Label(window, text="Vol limit(0~20V)")
Vollimit.grid(row=4, column=2)
CurVol = Label(window, text="current voltage : ")
CurVol.grid(row=5, column=0)
txt_out = Label(window, text="")
txt_out.grid(row=5, column=1)
Vt = Label(window, text="[V]")
Vt.grid(row=5, column=2)

mea=Label(window, text="measur current")
mea.grid(row=7, column=0)
b6 = Button(window, text="measur", command=MeaCur)
b6.grid(row=8, column=0)
meaV = Label(window, text="")
meaV.grid(row=8, column=1)
meaC = Label(window, text="")
meaC.grid(row=8, column=2)
meaP = Label(window, text="")
meaP.grid(row=9, column=1)
meaSV = Label(window, text="")
meaSV.grid(row=9, column=2)

b7 = Button(window, text="Write Result", command=Write_Result)
b7.grid(row=10, column=0)

b8 = Button(window, text="Write Result Reset", command=WR_Reset)
b8.grid(row=10, column=1)

b9 = Button(window, text="Result Check", command=ResultC)
b9.grid(row=10, column=2)

def combos(event):
    global combosl
    combosl=int(comboS.get())
    print(combosl)

valueS=["1","2","3","4","5","6","7","8"]
comboS=ttk.Combobox(window, width=10, height=5, value=valueS)
comboS.grid(row=12, column=0)
comboS.set("Relay Select")
comboS.bind("<<ComboboxSelected>>",combos)

Rel=Label(window, text="LED Relay Ctrl")
Rel.grid(row=11, column=0)
b10 = Button(window, text="ON", command=lambda: LEDRelay(combosl,ON))
b10.grid(row=12, column=1)
b11 = Button(window, text="OFF", command=lambda: LEDRelay(combosl,OFF))
b11.grid(row=12, column=2)

DrobV=Label(window, text="Rpower suplly Drob Voltage")
DrobV.grid(row=13, column=0)
input_DV=StringVar()
input_DV.set("0.0")
input_DV_enter=Entry(window, width=10, textvariable=input_DV)
input_DV_enter.grid(row=14, column=0)
b12 = Button(window, text="Enter", command=DVol)
b12.grid(row=14, column=1)
CurDVol = Label(window, text="Drob voltage : ")
CurDVol.grid(row=15, column=0)
txt_Dout = Label(window, text="")
txt_Dout.grid(row=15, column=1)
DVt = Label(window, text="[V]")
DVt.grid(row=15, column=2)
DVol()

def PowONOFF(P):
    if P == ON:
        ser.write("OUTPUT ON\r\n".encode('ascii'))
    else:
        ser.write("OUTPUT OFF\r\n".encode('ascii'))

def LEDRelay(R, N):
    if R == 1 and N == ON:
        GP.output(LED1, True)
    elif R == 1 and N == OFF:
        GP.output(LED1, False)
    elif R == 2 and N == ON:
        GP.output(LED2, True)
    elif R == 2 and N == OFF:
        GP.output(LED2, False)
    elif R == 3 and N == ON:
        GP.output(LED3, True)
    elif R == 3 and N == OFF:
        GP.output(LED3, False)
    elif R == 4 and N == ON:
        GP.output(LED4, True)
    elif R == 4 and N == OFF:
        GP.output(LED4, False)
    elif R == 5 and N == ON:
        GP.output(LED5, True)
    elif R == 5 and N == OFF:
        GP.output(LED5, False)
    elif R == 6 and N == ON:
        GP.output(LED6, True)
    elif R == 6 and N == OFF:
        GP.output(LED6, False)
    elif R == 7 and N == ON:
        GP.output(LED7, True)
    elif R == 7 and N == OFF:
        GP.output(LED7, False)
    elif R == 8 and N == ON:
        GP.output(LED8, True)
    elif R == 8 and N == OFF:
        GP.output(LED8, False)
    else:
        print("FALSE COMMAND")

def call1(RL, NF):
    if RL == 1 and NF == ON:
        GP.output(Relay1, True)
    elif RL == 1 and NF == OFF:
        GP.output(Relay1, False)
    elif RL == 2 and NF == ON:
        GP.output(Relay2, True)
    elif RL == 2 and NF == OFF:
        GP.output(Relay2, False)
    elif RL == 3 and NF == ON:
        GP.output(Relay3, True)
    elif RL == 3 and NF == OFF:
        GP.output(Relay3, False)
    elif RL == 4 and NF == ON:
        GP.output(Relay4, True)
    elif RL == 4 and NF == OFF:
        GP.output(Relay4, False)
    elif RL == 5 and NF == ON:
        GP.output(Relay5, True)
    elif RL == 5 and NF == OFF:
        GP.output(Relay5, False)
    elif RL == 6 and NF == ON:
        GP.output(Relay6, True)
    elif RL == 6 and NF == OFF:
        GP.output(Relay6, False)
    elif RL == 7 and NF == ON:
        GP.output(Relay7, True)
    elif RL == 7 and NF == OFF:
        GP.output(Relay7, False)
    elif RL == 8 and NF == ON:
        GP.output(Relay8, True)
    elif RL == 8 and NF == OFF:
        GP.output(Relay8, False)
    else:
        print("FALSE COMMAND")

window.mainloop()
