###########################################
# receiving fixed monitor
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0003 - channel 04
# receiver    - address FFFF - channel 04
###########################################

from machine import Pin, I2C
from loraE32 import ebyteE32
import ssd1306
import utime

M0pin = 25
M1pin = 26
AUXpin = 27
oled_i2c_address = 0x3C # decimaal 60

# i2c, oled en e32 instances
i2c = I2C(scl=Pin(21), sda=Pin(22))
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr = oled_i2c_address)

e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0xFFFF, Channel=0x04, debug=False)

e32.start()

from_address = 0x0001
from_channel = 0x02

while True:
    message = e32.recvMessage(from_address, from_channel, useChecksum=True)
    oled.fill(0)
    oled.text(message.get('msg'), 0, 0)
    oled.show()
    utime.sleep_ms(2000)

e32.stop()
oled.poweroff()