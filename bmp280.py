import time
from bitbang_i2c import BitBangI2C

class BM280:
    ADDRESS = 0x76
    REG_TEMP_MSB = 0xFA
    REG_TEMP_LSB = 0xFB
    REG_TEMP_XLSB = 0xFC
    REG_CTRL_MEAS = 0xF4
    REG_CONFIG = 0xF5

    def __init__(self, i2c:BitBangI2C):
        self.i2c = i2c
        self.calibration = self._read_calibration()
        self.write_register(self.REG_CTRL_MEAS, 0b00100111)

    def write_register(self, reg, value):
        self.i2c.start()
        self.i2c.write_byte((self.ADDRESS << 1) | 0)
        self.i2c.write_byte(reg)
        self.i2c.write_byte(value)
        self.i2c.stop()

    def read_regsters(self, start_reg, length):
        self.i2c.start()
        self.i2c.write_byte((self.ADDRESS << 1) | 0)
        self.i2c.write_byte(start_reg)
        self.i2c.start()
        self.i2c.write_byte((self.ADDRESS << 1) | 1)
        data = [self.i2c.read_byte(ack=(i < length -1)) for i in range(length)]
        self.i2c.stop()
        return data
    
    def _read_calibration(self):
        data = self.read_regsters(0x88, 6)
        T1 = data[1] << 8 | data[0]
        T2 = self._twos_complement(data[3] << 8 | data[2], 16)
        T3 = self._twos_complement(data[5] << 8 | data[4], 16)
        return {"T1": T1, "T2": T2, "T3": T3}
    
    def _twos_complement(self, val, bits):
        if val & (1 << (bits - 1)):
            return val - (1 << bits)
        return val
    
    def read_temperature(self):
        data = self.read_regsters(self.REG_TEMP_MSB, 3)
        raw_temp=  (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        T1 = self.calibration["T1"]
        T2 = self.calibration["T2"]
        T3 = self.calibration["T3"]

        #Compensation
        var1 = (((raw_temp >> 3) - (T1 << 1)) * T2) >> 11
        var2 = (((((raw_temp >> 4) - T1) * ((raw_temp >> 4) - T1)) >> 12) * T3) >> 14
        t_fine = var1 + var2
        temp_c = (t_fine * 5 + 128) >> 8
        return temp_c / 100.0
        