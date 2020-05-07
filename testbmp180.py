from bmp180 import BMP180
from machine import I2C, Pin

bus =  I2C(scl=Pin(22), sda=Pin(21), freq=100000)   # esp32
bmp180 = BMP180(bus)
bmp180.oversample_sett = 2
bmp180.baseline = 101325
 
temp = bmp180.temperature
p = bmp180.pressure
altitude = bmp180.altitude
print("Temperature: ",temp)
print("Pressure: ",p)
print("Altitude: ",altitude)