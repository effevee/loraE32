###########################################################################
# this node sends temperature & humidity of a DHT11 sensor every 5 minutes,
# after transmitting the ESP32 goes to deepsleep to save battery power
###########################################################################
# transmitter - address 0001 - channel 02
# message     - address 0003 - channel 04
# receiver    - address FFFF - channel 04
###########################################################################

from machine import Pin, deepsleep
from loraE32 import ebyteE32
import dht
import utime
import sys

# pins E32
M0pin = 25
M1pin = 26
AUXpin = 27

# pin DHT11
DHTpin = 14

# instance E32
e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0x0001, Channel=0x02, debug=False)
e32.start()

# instance DHT11
dht11 = dht.DHT11(Pin(DHTpin))

# temperature & humidity
# average of 5 measurements
temptot = 0
humtot = 0
for i in range(5):
    dht11.measure()
    temptot += dht11.temperature()
    humtot += dht11.humidity()
    utime.sleep(2)
temp = int(round(temptot / 5))
hum = int(round(humtot / 5))

# send sensor data 
to_address = 0x0003
to_channel = 0x04
message = { 'node': '01', 'temp': str(temp), 'hum': str(hum) }
print('Sending fixed monitor : address %s - channel %d - message %s'%(to_address, to_channel, message))
e32.sendMessage(to_address, to_channel, message, useChecksum=True)
utime.sleep(3)
e32.stop()

# deepsleep for 5 min
deepsleep(300000)