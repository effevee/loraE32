###########################################################################
# this node sends temperature & pressure of a BMP180 sensor every 5 minutes,
# after transmitting the ESP32 goes to deepsleep to save battery power
###########################################################################
# transmitter - address 0002 - channel 02
# message     - address 0003 - channel 04
# receiver    - address FFFF - channel 04
###########################################################################

from machine import Pin, I2C, deepsleep
from loraE32 import ebyteE32
from bmp180 import BMP180
import utime
import sys

# pins E32
M0pin = 25
M1pin = 26
AUXpin = 27

# instance E32
e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0x0001, Channel=0x02, debug=False)
e32.start()

# instance BPM180
bus =  I2C(scl=Pin(22), sda=Pin(21), freq=100000)
bmp180 = BMP180(bus)
bmp180.oversample_sett = 2
bmp180.baseline = 101325

# temperature & pressure
# average of 5 measurements
temptot = 0
prestot = 0
for i in range(5):
    temptot += bmp180.temperature
    prestot += bmp180.pressure
    utime.sleep(2)
temp = int(round(temptot / 5))
pres = int(round(prestot / 5))

# send sensor data 
to_address = 0x0003
to_channel = 0x04
message = { 'node': '02', 'temp': str(temp), 'pres': str(pres) }
print('Sending fixed monitor : address %s - channel %d - message %s'%(to_address, to_channel, message))
e32.sendMessage(to_address, to_channel, message, useChecksum=True)
utime.sleep(3)
e32.stop()

# deepsleep for 5 min
deepsleep(300000)