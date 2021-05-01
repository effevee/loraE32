import wifi_data
import network
import utime
from machine import Pin

class Wifi:
    
    def __init__(self):
        """ activation WLAN interface"""
        self.net = None
        self.status = 0
        self.wdata = wifi_data.Data
        try:
            self.net = network.WLAN(network.STA_IF)
            self.net.active(True)
        except Exception as e:
            self.status = -1
            if self.wdata.debug:
                print('Wifi __init__ fout: ', e)
    
    def open(self):
        """connect to SSID from wifi_data"""
        try:
            for x in range(0, len(self.wdata.ssid)):
                if not self.net.isconnected():
                    self.net.connect(self.wdata.ssid[x], self.wdata.pwd[x])
                    tries = 0
                    while not self.net.isconnected() and tries < self.wdata.times_try:
                        utime.sleep_ms(250)
                        tries += 1
                        pass
                if self.net.isconnected():
                    self.status = 1
                    return True
            self.status = -1
            return False
        except Exception as e:
            self.status = -1
            if self.wdata.debug:
                print('Wifi open fout: ', e)
            return False

    def close(self):
        """disconnect"""
        self.net.disconnect()
        self.status = 0
    
    def get_status(self):
        """gives status by blinking LED
        status NOK: 10 short flash
        status OK: Long on - short off - long on"""
        led_board=Pin(2, Pin.OUT)
        if self.status <= 0:
            for t in range(0, 10):
                led_board.value(0)
                utime.sleep(0.2)
                led_board.value(1)
                utime.sleep(0.2)
        else:
            led_board.value(0)
            utime.sleep(1)
            led_board.value(1)
            utime.sleep(0.2)
            led_board.value(0)
            utime.sleep(1)
            led_board.value(1)
        return self.status

    def get_IPdata(self):
        """Get IP data"""
        if self.status > 0:
            return self.net.ifconfig()
        else:
            return ""
        
    def checkWifiConnect(self):
        """Check Wifi connection and restart if needed"""
        if self.get_IPdata() == "" or self.get_IPdata()[0] == "0.0.0.0":
            self.status = 0
            self.open()
            self.get_status()
        return self.status
    