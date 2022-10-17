###########################################
# receiving fixed point to point
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0003 - channel 04
# receiver    - address 0003 - channel 04
###########################################

import board
from loraE32cp import ebyteE32
import time

M0pin = board.D2
M1pin = board.D3
AUXpin = board.D4

e32 = ebyteE32(board.D2, board.D3, board.D4, Port='U2', Address=0x0003, Channel=0x04, debug=False)

e32.start()

from_address = 0x0001
from_channel = 0x02

while True:
    print('Receiving fixed P2P: address %d - channel %d'%(from_address, from_channel), end='')
    message = e32.recvMessage(from_address, from_channel, useChecksum=True)
    print(' - message %s'%(message))
    time.sleep(2)

e32.stop()