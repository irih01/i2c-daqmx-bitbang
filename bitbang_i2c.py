import time
import nidaqmx
from nidaqmx.constants import LineGrouping, TaskMode
from ctypes import c_ubyte

class DigitalPin:
    def __init__(self, channel):
        self.channel = channel
        self.write_task = nidaqmx.Task()
        self.read_task = nidaqmx.Task()
        
       
        self.write_task.do_channels.add_do_chan(self.channel,line_grouping=LineGrouping.CHAN_PER_LINE)
        self.read_task.di_channels.add_di_chan(self.channel,line_grouping=LineGrouping.CHAN_PER_LINE)

    def set_output(self):
        self.write_task.start()

    def set_input(self):
        self.write_task.stop()
        self.read_task.start()
    
    def write(self, value):
        data = (c_ubyte * 1)(value)
        self.write_task.write(1,data=data)

    def read(self):
        data = (c_ubyte * 1)()
        self.read_task.read(data)
        return data[0]
    
    def close(self):
        self.write_task.stop()
        self.write_task.close()
        self.read_task.stop()
        self.read_task.close()


class BitBangI2C:
    def __init__(self, scl_pin, sda_pin, delay=0.001):
        self.scl = DigitalPin(scl_pin)
        self.sda = DigitalPin(sda_pin)
        self.delay = delay

    def sleep(self):
        time.sleep(self.delay)

    def scl_high(self):
        self.scl.set_input()
        self.sleep()

    def scl_low(self):
        self.scl.set_output()
        self.scl.write(0)
        self.sleep()

    def sda_high(self):
        self.sda.set_input()
        self.sleep()

    def sda_low(self):
        self.sda.set_output()
        self.sda.write(0)
        self.sleep()

    def start(self):
        self.sda_high()
        self.scl_high()
        self.sleep()
        self.sda_low()
        self.sleep()
        self.scl_low()
        self.sleep()

    def stop(self):
        self.sda_low()
        self.scl_high()
        self.sleep()
        self.sda_high()
        self.sleep()

    def write_byte(self, byte):
        for i in range(8):
            if (byte & 0x80):
                self.sda_high()
            else:
                self.sda_low()
            byte <<= 1
            self.scl_high()
            self.scl_low()

            #ACK bit
        self.sda_high() #release SDA
        self.scl_high()
        ack = self.sda.read()
        self.scl_low()
        return ack == 0
    
    def read_byte(self, ack=True):
        byte = 0
        self.sda_high()
        for _ in range(8):
            self.scl_high()
            bit = self.sda.read()
            byte = (byte << 1) | bit
            self.scl_low()
        # Send ACK/NACK
        if ack:
            self.sda_low()
        else:
            self.sda_high()
        self.scl_high()
        self.scl_low()
        self.sda_high()
        return byte
    
    def close(self):
        self.scl.close()
        self.sda.close()
        
        