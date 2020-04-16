###########################################################################
# this node receives sensor data from all sensor nodes transmitting on
# channel 4. Valid sensor data is stored in an Influx database table to be
# visualized in a Grafana dashboard
###########################################################################
# receiving fixed monitor
###########################################################################
# transmitter - address 0001 - channel 02
# message     - address 0003 - channel 04
# receiver    - address FFFF - channel 04
###########################################################################

from loraE32 import ebyteE32
from influxdbTools import influxdbPutData
import simpleWifi
import utime

# pins E32
M0pin = 25
M1pin = 26
AUXpin = 27

# instances
e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0xFFFF, Channel=0x04, debug=False)
e32.start()

# influxdb
dbhost = "192.168.1.40"
influx = influxdbPutData(dbhost, 8086, "serre_frank", "node", "field", "value", debug=False)

# connect to WiFi
myWifi = simpleWifi.Wifi()
if myWifi.open():
    print(myWifi.get_IPdata())
else:
    print('No connection to WiFi')
    
# loop to receive sensor data
from_address = 0x0001
from_channel = 0x02
while True:
    # check for sensor data 
    message = e32.recvMessage(from_address, from_channel, useChecksum=True)
    if 'node' in message.keys():
        # display message
        print('.')
        print('Receiving fixed monitor : address %d - channel %d - message %s'%(from_address, from_channel, message))
        # fill datastructure with sensor data
        node = 'node_' + message.get('node')
        field = 'temp'
        value = message.get('temp')
        influx.makeDataStringNodeFieldValue(node, field, value)  # temperature
        field = 'hum'
        value = message.get('hum')
        influx.makeDataStringNodeFieldValue(node, field, value)  # humidity
        # write sensor data to influxdb
        influx.writeToInfluxdb()
    # wait for next check
    print('.', end='')
    utime.sleep_ms(5000)

# stop E32
e32.stop()