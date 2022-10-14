# coding=utf-8

import board
from loraE32 import ebyteE32


M0pin = board.D2
M1pin = board.D3
AUXpin = board.D4

e32 = ebyteE32(board.D2, board.D3, board.D4, Port='U2', Address=0x0001, Channel=0x04)

e32.start()
# e32.getConfig()
# e32.getVersion()
# e32.reset()
# e32.setConfig('setConfigPwrDwnSave')
# e32.setConfig('setConfigPwrDwnNoSave')

e32.stop()
