###########################################
# sending fixed broadcast
###########################################
# transmitter - address 0001 - channel 02
# message     - address FFFF - channel 04
# receiver(s) - address 0003 - channel 04
###########################################

import board
from loraE32cp import ebyteE32
import time

M0pin = board.D2
M1pin = board.D3
AUXpin = board.D4

e32 = ebyteE32(board.D2, board.D3, board.D4, Port='U2', Address=0x0001, Channel=0x02, debug=False)

e32.start()

to_address = 0xFFFF
to_channel = 0x04

teller = 0
while True:
    message = { 'msg': 'HELLO WORLD %s'%str(teller) }
    print('Sending fixed broadcast : address %s - channel %d - message %s'%(to_address, to_channel, message))
    e32.sendMessage(to_address, to_channel, message, useChecksum=True)
    teller += 1
    time.sleep(2)

e32.stop()