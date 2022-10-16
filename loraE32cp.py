# coding=utf-8

import busio
import board
import digitalio
import json
import time


class ebyteE32:
    """
    Class to interface an ESP32 via serial commands to the EBYTE E32 Series LoRa modules

    Attributes:
        PORT (dict): dictionary with UART ports
        PARSTR (dict): dictionary with UART parity strings
        PARINV (dict): dictionary with UART parity inverted
        PARBIT (dict): dictionary with UART parity bits
        BAUDRATE (dict): dictionary with UART baudrates
        BAUDRATEINV (dict): dictionary with UART baudrates inverted
        DATARATE (dict): dictionary with LoRa datarates
        DATARATEINV (dict): dictionary with LoRa datarates inverted
        CMDS (dict): dictionary with commands
        OPERMODE (dict): dictionary with operating modes (set with M0 & M1)
        FREQ (dict): dictionary with model frequencies ranges (MHz)
        FREQV (dict): dictionary with version info frequencies
        MAXPOWER (dict): dictionary with model maximum transmission power (mW)
        TRANSMODE (dict): dictionary with transmission modes
        IOMODE (dict): dictionary with I/O drive mode
        WUTIME (dict): dictionary with wireless wakeup times from sleep mode
        FEC (dict): dictionary with Forward Error Correction (FEC) mode
        TXPOWER (dict): dictionary with transmission power T20/T27/T30 (dBm)
    """

    # UART ports
    PORT = {'U': [board.TX, board.RX], 'U1': [board.TX1, board.RX1], 'U2': [board.TX2, board.RX2],
            'U3': [board.TX3, board.RX3], 'U4': [board.TX4, board.RX4]}
    # UART parity strings
    PARSTR = {'8N1': '00', '8O1': '01', '8E1': '10'}
    PARINV = {v: k for k, v in PARSTR.items()}
    # UART parity bits
    PARBIT = {'N': None, 'E': 0, 'O': 1}
    # UART baudrate
    BAUDRATE = {1200: '000', 2400: '001', 4800: '010', 9600: '011',
                19200: '100', 38400: '101', 57600: '110', 115200: '111'}
    BAUDRINV = {v: k for k, v in BAUDRATE.items()}
    # LoRa datarate
    DATARATE = {'0.3k': '000', '1.2k': '001', '2.4k': '010',
                '4.8k': '011', '9.6k': '100', '19.2k': '101'}
    DATARINV = {v: k for k, v in DATARATE.items()}
    # Commands
    CMDS = {'setConfigPwrDwnSave': 0xC0,
            'getConfig': 0xC1,
            'setConfigPwrDwnNoSave': 0xC2,
            'getVersion': 0xC3,
            'reset': 0xC4}
    # operation modes (set with M0 & M1)
    OPERMODE = {'normal': '00', 'wakeup': '10', 'powersave': '01', 'sleep': '11'}
    # model frequency ranges (MHz)
    FREQ = {170: [160, 170, 173], 400: [410, 470, 525], 433: [410, 433, 441],
            868: [862, 868, 893], 915: [900, 915, 931]}
    # version info frequency
    FREQV = {'0x32': 433, '0x38': 470, '0x45': 868, '0x44': 915, '0x46': 170}
    # model maximum transmission power
    # 20dBm = 100mW - 27dBm = 500 mW - 30dBm = 1000 mW (1 W)
    MAXPOW = {'T20': 0, 'T27': 1, 'T30': 2}
    # transmission mode
    TRANSMODE = {0: 'transparent', 1: 'fixed'}
    # IO drive mode
    IOMODE = {0: 'TXD AUX floating output, RXD floating input',
              1: 'TXD AUX push-pull output, RXD pull-up input'}
    # wireless wakeup times from sleep mode
    WUTIME = {0b000: '250ms', 0b001: '500ms', 0b010: '750ms', 0b011: '1000ms',
              0b100: '1250ms', 0b101: '1500ms', 0b110: '1750ms', 0b111: '2000ms'}
    # Forward Error Correction (FEC) mode
    FEC = {0: 'off', 1: 'on'}
    # transmission power T20/T27/T30 (dBm)
    TXPOWER = {0b00: ['20dBm', '27dBm', '30dBm'],
               0b01: ['17dBm', '24dBm', '27dBm'],
               0b10: ['14dBm', '21dBm', '24dBm'],
               0b11: ['10dBm', '18dBm', '21dBm']}

    def __init__(self, PinM0, PinM1, PinAUX, Model='868T20D', Port='U1', Baudrate=9600, Parity='8N1',
                 AirDataRate='2.4k', Address=0x0000, Channel=0x06, debug=False):
        """
        constructor for ebyte E32 LoRa module

        Examples:
            >>> import board
            >>> import ebyteE32
            >>> M0pin = board.D2
            >>> M1pin = board.D3
            >>> AUXpin = board.D4
            >>> e32 = ebyteE32(board.D2, board.D3, board.D4, Port='U2', Address=0x0001, Channel=0x04)
            >>> e32.start()
            'OK'
            >>> e32.stop()
            'OK'

        Args:
            PinM0 (Pin): pin identifier for M0
            PinM1 (Pin): pin identifier for M1
            PinAUX (Pin): pin identifier for AUX
            Model (str): model of the module (default: '868T20D')
            Port (str): UART port identifier (default: 'U1')
            Baudrate (int): UART baudrate (default: 9600)
            Parity (str): UART parity (default: '8N1')
            AirDataRate (str): LoRa air data rate (default: '2.4k')
            Address (int): LoRa address (default: 0x0000)
            Channel (int): LoRa channel (default: 0x06)
            debug (bool): debug mode (default: False)
        """
        # configuration in dictionary
        self.config = {'model': Model, 'port': Port, 'baudrate': Baudrate, 'parity': Parity, 'datarate': AirDataRate,
                       'address': Address, 'channel': Channel}
        self.calcFrequency()  # calculate frequency (min frequency + channel*1 MHz)
        self.config['transmode'] = 0  # transmission mode (default 0 - tranparent)
        self.config['iomode'] = 1  # IO mode (default 1 = not floating)
        self.config['wutime'] = 0  # wakeup time from sleep mode (default 0 = 250ms)
        self.config['fec'] = 1  # forward error correction (default 1 = on)
        self.config['txpower'] = 0  # transmission power (default 0 = 20dBm/100mW)
        #
        self.PinM0 = PinM0  # M0 pin number
        self.PinM1 = PinM1  # M1 pin number
        self.PinAUX = PinAUX  # AUX pin number
        self.M0 = None  # instance for M0 Pin (set operation mode)
        self.M1 = None  # instance for M1 Pin (set operation mode)
        self.AUX = None  # instance for AUX Pin (device status : 0=busy - 1=idle)
        self.serdev = None  # instance for UART
        self.debug = debug

    def start(self):
        """
        Start the ebyte E32 LoRa module

        Raises:
            E (Error): if error on start UART
        """
        try:
            # check parameters
            if int(self.config['model'].split('T')[0]) not in ebyteE32.FREQ:
                self.config['model'] = '868T20D'
            if self.config['port'] not in ebyteE32.PORT:
                self.config['port'] = 'U1'
            if int(self.config['baudrate']) not in ebyteE32.BAUDRATE:
                self.config['baudrate'] = 9600
            if self.config['parity'] not in ebyteE32.PARSTR:
                self.config['parity'] = '8N1'
            if self.config['datarate'] not in ebyteE32.DATARATE:
                self.config['datarate'] = '2.4k'
            if self.config['channel'] > 31:
                self.config['channel'] = 31
            # make UART instance
            self.serdev = busio.UART(ebyteE32.PORT.get(self.config['port'])[0],
                                     ebyteE32.PORT.get(self.config['port'])[1], timeout=0)
            # init UART
            par = ebyteE32.PARBIT.get(str(self.config['parity'])[1])
            # self.serdev.init(baudrate=self.config['baudrate'], bits=8, parity=par, stop=1)
            if self.debug:
                print(self.serdev)
            # make operation mode & device status instances
            self.M0 = digitalio.DigitalInOut(self.PinM0)
            self.M0.direction = digitalio.Direction.OUTPUT
            self.M1 = digitalio.DigitalInOut(self.PinM1)
            self.M1.direction = digitalio.Direction.OUTPUT
            self.AUX = digitalio.DigitalInOut(self.PinAUX)
            self.AUX.direction = digitalio.Direction.INPUT
            self.AUX.pull = digitalio.Pull.UP
            if self.debug:
                print(self.M0, self.M1, self.AUX)
            # set config to the ebyte E32 LoRa module
            self.setConfig('setConfigPwrDwnSave')
            return "OK"

        except Exception as E:
            if self.debug:
                print("error on start UART", E)
            return "NOK"

    def sendMessage(self, to_address, to_channel, payload, useChecksum=False):
        """
        Send the payload to ebyte E32 LoRa modules in transparent or fixed mode. The payload is a data dictionary to
        accomodate key value pairs commonly used to store sensor data and is converted to a JSON string before sending.
        The payload can be appended with a 2's complement checksum to validate correct transmission.

        - transparent mode : all modules with the same address and channel of the transmitter will receive the payload
        - fixed mode : only the module with this address and channel will receive the payload;
                       if the address is 0xFFFF all modules with the same channel will receive the payload

        Examples:
            >>> sendMessage(0x0000, 0x06, {'temperature': 25.5, 'humidity': 60.0}, True)
            'OK'

        Args:
            to_address (int): target address (0x0000 - 0xFFFF)
            to_channel (int): target channel (0x00 - 0x1F)
            payload (dict): data dictionary to send
            useChecksum (bool): use 2's complement checksum (default: False)

        Returns:
            str: 'OK' if success, 'NOK' if error

        Raises:
            E (Error): if error on sendMessage
        """
        try:
            # type of transmission
            if (to_address == self.config['address']) and (to_channel == self.config['channel']):
                # transparent transmission mode
                # all modules with the same address and channel will receive the payload
                self.setTransmissionMode(0)
            else:
                # fixed transmission mode
                # only the module with the target address and channel will receive the payload
                self.setTransmissionMode(1)
            # put into wakeup mode (includes preamble signals to wake up device in powersave or sleep mode)
            self.setOperationMode('wakeup')
            # check payload
            if type(payload) != dict:
                print('payload is not a dictionary')
                return 'NOK'
            # encode message
            msg = []
            if self.config['transmode'] == 1:  # only for fixed transmission mode
                msg.append(to_address // 256)  # high address byte
                msg.append(to_address % 256)  # low address byte
                msg.append(to_channel)  # channel
            js_payload = json.dumps(payload)  # convert payload to JSON string
            for i in range(len(js_payload)):  # message
                msg.append(ord(js_payload[i]))  # ascii code of character
            if useChecksum:  # attach 2's complement checksum
                msg.append(int(self.calcChecksum(js_payload), 16))
            # debug
            if self.debug:
                print(msg)
            # wait for idle module
            self.waitForDeviceIdle()
            # send the message
            self.serdev.write(bytes(msg))
            return "OK"

        except Exception as E:
            if self.debug:
                print('Error on sendMessage: ', E)
            return "NOK"

    def recvMessage(self, from_address, from_channel, useChecksum=False):
        """
        Receive payload messages from ebyte E32 LoRa modules in transparent or fixed mode. The payload is a JSON string
        of a data dictionary to accomodate key value pairs commonly used to store sensor data. If checksumming is used, the
        checksum of the received payload including the checksum byte should result in 0 for a correct transmission.
        - transparent mode : payload will be received if the module has the same address and channel of the transmitter
        - fixed mode : only payloads from transmitters with this address and channel will be received;
                       if the address is 0xFFFF, payloads from all transmitters with this channel will be received

        Examples:
            >>> recvMessage(0x0000, 0x06, True)
            {'temperature': 25.5, 'humidity': 60.0}

        Args:
            from_address (int): source address (0x0000 - 0xFFFF)
            from_channel (int): source channel (0x00 - 0x1F)
            useChecksum (bool): use 2's complement checksum (default: False)

        Returns:
            dict: data dictionary with payload data if success, None if error

        Raises:
            E (Error): if error on recvMessage
        """
        try:
            # type of transmission
            if (from_address == self.config['address']) and (from_channel == self.config['channel']):
                # transparent transmission mode
                # all modules with the same address and channel will receive the message
                self.setTransmissionMode(0)
            else:
                # fixed transmission mode
                # only the module with the target address and channel will receive the message
                self.setTransmissionMode(1)
            # put into normal mode
            self.setOperationMode('normal')
            # receive message
            js_payload = self.serdev.readline()
            # debug
            if self.debug:
                print(js_payload)
            # did we receive anything ?
            if js_payload == None:
                # nothing
                return {'msg': None}
            else:
                # decode message
                msg = ''
                for i in range(len(js_payload)):
                    msg += chr(js_payload[i])
                # checksum check
                if useChecksum:
                    cs = int(self.calcChecksum(msg), 16)
                    if cs != 0:
                        # corrupt
                        return {'msg': 'corrupt message, checksum ' + str(cs)}
                    else:
                        # message ok, remove checksum
                        msg = msg[:-1]
                # JSON to dictionary
                message = json.loads(msg)
                return message

        except Exception as E:
            if self.debug:
                print('Error on recvMessage: ', E)
            return "NOK"

    def calcChecksum(self, payload):
        """
        Calculates checksum for sending/receiving payloads. Sums the ASCII character values mod256 and returns
        the lower byte of the two's complement of that value in hex notation.

        Examples:
            >>> calcChecksum('{"temperature":25.5,"humidity":60.0}')
            '37'

        Args:
            payload (str): payload to calculate checksum for

        Returns:
            str: checksum in hex notation
        """
        return '%2X' % (-(sum(ord(c) for c in payload) % 256) & 0xFF)

    def reset(self):
        """
        Reset the ebyte E32 Lora module

        Examples:
            >>> reset()
            'OK'

        Returns:
            str: 'OK' if success, 'NOK' if error

        Raises:
            E (Error): if error on reset
        """
        try:
            # send the command
            res = self.sendCommand('reset')
            # discard result
            return "OK"

        except Exception as E:
            if self.debug:
                print("error on reset", E)
            return "NOK"

    def stop(self):
        """
        Stop the ebyte E32 LoRa module

        Examples:
            >>> stop()
            'OK'

        Returns:
            str: 'OK' if success, 'NOK' if error

        Raises:
            E (Error): if error on stop
        """
        try:
            if self.serdev != None:
                self.serdev.deinit()
                del self.serdev
            return "OK"

        except Exception as E:
            if self.debug:
                print("error on stop UART", E)
            return "NOK"

    def sendCommand(self, command):
        """
        Send a command to the ebyte E32 LoRa module.
        The module has to be in sleep mode

        Examples:
            >>> sendCommand('reset')
            'OK'

        Args:
            command (str): command to send

        Returns:
            str: 'OK' if success, 'NOK' if error

        Raises:
            E (Error): if error on sendCommand
        """
        try:
            # put into sleep mode
            self.setOperationMode('sleep')
            # send command
            HexCmd = ebyteE32.CMDS.get(command)
            if HexCmd in [0xC0, 0xC2]:  # set config to device
                header = HexCmd
                HexCmd = self.encodeConfig()
                HexCmd[0] = header
            else:  # get config, get version, reset
                HexCmd = [HexCmd] * 3
            if self.debug:
                print(HexCmd)
            self.serdev.write(bytes(HexCmd))
            # wait for result
            time.sleep(0.05)
            # read result
            if command == 'reset':
                result = ''
            else:
                result = self.serdev.readline()
                # wait for result
                time.sleep(0.05)
                # debug
                if self.debug:
                    print(result)
            return result

        except Exception as E:
            if self.debug:
                print('Error on sendCommand: ', E)
            return "NOK"

    def getVersion(self):
        """
        Get the version info from the ebyte E32 LoRa module

        Examples:
            >>> getVersion()
            ================= E32 MODULE ===================
            model       	433Mhz
            version     	16
            features    	30
            ================================================

        Returns:
            str: version info if success, 'NOK' if error

        Raises:
            E (Error): if error on getVersion
        """
        try:
            # send the command
            result = self.sendCommand('getVersion')
            # check result
            if len(result) != 4:
                return "NOK"
            # decode result
            freq = ebyteE32.FREQV.get(hex(result[1]), 'unknown')
            # show version
            if result[0] == 0xc3:
                print('================= E32 MODULE ===================')
                print('model       \t%dMhz' % (freq))
                print('version     \t%d' % (result[2]))
                print('features    \t%d' % (result[3]))
                print('================================================')
            return "OK"

        except Exception as E:
            if self.debug:
                print('Error on getVersion: ', E)
            return "NOK"

    def getConfig(self):
        """
        Get config parameters from the ebyte E32 LoRa module

        Examples:
            >>> getConfig()
            =================== CONFIG =====================
            model       	E32-868T20D
            frequency   	866Mhz
            address     	0x0001
            channel     	0x04
            datarate    	2.4kbps
            port        	U2
            baudrate    	9600bps
            parity      	8N1
            transmission	transparent
            IO mode     	TXD AUX push-pull output, RXD pull-up input
            wakeup time 	250ms
            FEC         	on
            TX power    	20dBm
            ================================================

        Returns:
            str: config parameters if success, 'NOK' if error

        Raises:
            E (Error): if error on getConfig
        """
        try:
            # send the command
            result = self.sendCommand('getConfig')
            # check result
            if len(result) != 6:
                return "NOK"
            # decode result
            self.decodeConfig(result)
            # show config
            self.showConfig()
            return "OK"

        except Exception as E:
            if self.debug:
                print('Error on getConfig: ', E)
            return "NOK"

    def decodeConfig(self, message):
        """
        decode the config message from the ebyte E32 LoRa module to update the config dictionary

        Examples:
            >>> decodeConfig([0xC0, 0x00, 0x00, 0x00, 0x00, 0x00])

        Args:
            message (list): config message to decode

        Returns:
            None
        """
        # message byte 0 = header
        header = int(message[0])
        # message byte 1 & 2 = address
        self.config['address'] = int(message[1]) * 256 + int(message[2])
        # message byte 3 = speed (parity, baudrate, datarate)
        bits = '{0:08b}'.format(message[3])
        self.config['parity'] = ebyteE32.PARINV.get(bits[0:2])
        self.config['baudrate'] = ebyteE32.BAUDRINV.get(bits[2:5])
        self.config['datarate'] = ebyteE32.DATARINV.get(bits[5:])
        # message byte 4 = channel
        self.config['channel'] = int(message[4])
        # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
        bits = '{0:08b}'.format(message[5])
        self.config['transmode'] = int(bits[0:1])
        self.config['iomode'] = int(bits[1:2])
        self.config['wutime'] = int(bits[2:5])
        self.config['fec'] = int(bits[5:6])
        self.config['txpower'] = int(bits[6:])

    def encodeConfig(self):
        """
        encode the config dictionary to create the config message of the ebyte E32 LoRa module

        Examples:
            >>> encodeConfig()
            [192, 0, 1, 26, 4, 68]

        Returns:
            list: config message if success, 'NOK' if error
        """
        # Initialize config message
        message = []
        # message byte 0 = header
        message.append(0xC0)
        # message byte 1 = high address
        message.append(self.config['address'] // 256)
        # message byte 2 = low address
        message.append(self.config['address'] % 256)
        # message byte 3 = speed (parity, baudrate, datarate)
        bits = '0b'
        bits += ebyteE32.PARSTR.get(self.config['parity'])
        bits += ebyteE32.BAUDRATE.get(self.config['baudrate'])
        bits += ebyteE32.DATARATE.get(self.config['datarate'])
        message.append(int(bits))
        # message byte 4 = channel
        message.append(self.config['channel'])
        # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
        bits = '0b'
        bits += str(self.config['transmode'])
        bits += str(self.config['iomode'])
        bits += '{0:03b}'.format(self.config['wutime'])
        bits += str(self.config['fec'])
        bits += '{0:02b}'.format(self.config['txpower'])
        message.append(int(bits))
        return message

    def showConfig(self):
        """
        Show the config parameters of the ebyte E32 LoRa module on the shell

        Examples:
            >>> showConfig()
            =================== CONFIG =====================
            model       	E32-868T20D
            frequency   	866Mhz
            address     	0x0001
            channel     	0x04
            datarate    	2.4kbps
            port        	U2
            baudrate    	9600bps
            parity      	8N1
            transmission	transparent
            IO mode     	TXD AUX push-pull output, RXD pull-up input
            wakeup time 	250ms
            FEC         	on
            TX power    	20dBm
            ================================================

        Returns:
            str: with the config parameters
        """
        print('=================== CONFIG =====================')
        print('model       \tE32-%s' % (self.config['model']))
        print('frequency   \t%dMhz' % (self.config['frequency']))
        print('address     \t0x%04x' % (self.config['address']))
        print('channel     \t0x%02x' % (self.config['channel']))
        print('datarate    \t%sbps' % (self.config['datarate']))
        print('port        \t%s' % (self.config['port']))
        print('baudrate    \t%dbps' % (self.config['baudrate']))
        print('parity      \t%s' % (self.config['parity']))
        print('transmission\t%s' % (ebyteE32.TRANSMODE.get(self.config['transmode'])))
        print('IO mode     \t%s' % (ebyteE32.IOMODE.get(self.config['iomode'])))
        print('wakeup time \t%s' % (ebyteE32.WUTIME.get(self.config['wutime'])))
        print('FEC         \t%s' % (ebyteE32.FEC.get(self.config['fec'])))
        maxp = ebyteE32.MAXPOW.get(self.config['model'][3:6], 0)
        print('TX power    \t%s' % (ebyteE32.TXPOWER.get(self.config['txpower'])[maxp]))
        print('================================================')

    def waitForDeviceIdle(self):
        """
        Wait for the E32 LoRa module to become idle (AUX pin high)

        Examples:
            >>> waitForDeviceIdle()

        Returns:
            None
        """
        count = 0
        # loop for device busy
        while not self.AUX.value:
            # increment count
            count += 1
            # maximum wait time 100 ms
            if count == 10:
                break
            # sleep for 10 ms
            time.sleep(0.01)

    def saveConfigToJson(self):
        """
        Save config dictionary to JSON file

        Examples:
            >>> saveConfigToJson()

        Returns:
            None
        """
        with open('/E32config.json', 'w') as outfile:
            json.dump(self.config, outfile)

    def loadConfigFromJson(self):
        """
        Load config dictionary from JSON file

        Examples:
            >>> loadConfigFromJson()
            {'parity': '8N1', 'datarate': '2.4k', 'model': '868T20D', 'channel': 4, 'transmode': 0, 'port': 'U2', 'frequency': 866, 'baudrate': 9600, 'txpower': 0, 'iomode': 1, 'wutime': 0, 'address': 1, 'fec': 1}

        Returns:
            dict: config dictionary
        """
        with open('E32config.json', 'r') as infile:
            result = json.load(infile)
        print(self.config)

    def calcFrequency(self):
        """
        Calculate the frequency (= minimum frequency + channel * 1MHz)

        Examples:
            >>> calcFrequency()

        Returns:
            None
        """
        # get minimum and maximum frequency
        freqkey = int(self.config['model'].split('T')[0])
        minfreq = ebyteE32.FREQ.get(freqkey)[0]
        maxfreq = ebyteE32.FREQ.get(freqkey)[2]
        # calculate frequency
        freq = minfreq + self.config['channel']
        if freq > maxfreq:
            self.config['frequency'] = maxfreq
            self.config['channel'] = hex(maxfreq - minfreq)
        else:
            self.config['frequency'] = freq

    def setTransmissionMode(self, transmode):
        """
        Set the transmission mode of the E32 LoRa module

        Examples:
            >>> setTransmissionMode(0)

        Args:
            transmode (int): 0 = transparent, 1 = fixed length

        Returns:
            None
        """
        if transmode != self.config['transmode']:
            self.config['transmode'] = transmode
            self.setConfig('setConfigPwrDwnSave')

    def setConfig(self, save_cmd):
        """
        Set config parameters for the ebyte E32 LoRa module

        Examples:
            >>> setConfig('setConfigPwrDwnSave')
            'OK'

        Args:
            save_cmd (str): 'setConfigPwrDwnSave' or 'setConfig'

        Returns:
            str: 'OK' if success, 'NOK' if error
        """
        try:
            # send the command
            result = self.sendCommand(save_cmd)
            # check result
            if len(result) != 6:
                return "NOK"
            # debug
            if self.debug:
                # decode result
                self.decodeConfig(result)
                # show config
                self.showConfig()
            # save config to json file
            self.saveConfigToJson()
            return "OK"

        except Exception as E:
            if self.debug:
                print('Error on setConfig: ', E)
            return "NOK"

    def setOperationMode(self, mode):
        """
        Set operation mode of the E32 LoRa module

       Examples:
            >>> setOperationMode('normal')

        Args:
            mode (str): 'normal', 'wakeup', 'powerdown', 'sleep'
        """
        # get operation mode settings (default normal)
        bits = ebyteE32.OPERMODE.get(mode, '00')
        # set operation mode
        self.M0.value = bool(int(bits[0]))
        self.M1.value = bool(int(bits[1]))
        # wait a moment
        time.sleep(0.05)
