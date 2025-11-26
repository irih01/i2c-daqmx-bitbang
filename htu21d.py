import time
from bitbang_i2c import BitBangI2C

class HTU21D:
    ADDRESS = 0x40
    CMD_TEMP_HOLD = 0xE3
    CMD_HUMID_HOLD = 0xE5

    def __init__(self, i2c: BitBangI2C):
        self.i2c = i2c

    def read_temperature(self):
        self.i2c.start()
        self.i2c.write_byte((self.ADDRESS<<1)|0)
        self.i2c.write_byte(self.CMD_TEMP_HOLD)
        self.i2c.stop()

        time.sleep(0.05)

        self.i2c.start()
        self.i2c.write_byte((self.ADDRESS << 1) | 1)
        msb = self.i2c.read_byte()
        lsb = self.i2c.read_byte()
        crc = self.i2c.read_byte(ack=False)
        self.i2c.stop()

        raw_temp = ((msb << 8) | lsb) & 0xFFC

        temp_c = -46.85 + 175.72 * raw_temp / 65536.0

        if not self._check_crc(msb,lsb,crc):
            raise ValueError("CRC mismatch in temp reading")
        
        return temp_c
    
    def read_humidity(self):
        self.i2c.start()
        self.i2c.write_byte((self.ADDRESS<<1)|0)
        self.i2c.write_byte(self.CMD_HUMID_HOLD)
        self.i2c.stop()

        time.sleep(0.05)

        self.i2c.start()
        self.i2c.write_byte((self.ADDRESS << 1) | 1)
        msb = self.i2c.read_byte()
        lsb = self.i2c.read_byte()
        crc = self.i2c.read_byte(ack=False)
        self.i2c.stop()

        raw_rh = ((msb << 8) | lsb) & 0xFFC

        rh = -6.0 + 125.0 * raw_rh / 65536.0

        if not self._check_crc(msb,lsb,crc):
            raise ValueError("CRC mismatch in humidity reading")
        
        return rh
    
    def _check_crc(self, msb, lsb, crc):
        data = [msb,lsb]
        calculated_crc = self._calculate_crc(data)
        return calculated_crc == crc
    
    def _calculate_crc(self,data):
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x131
                else:
                    crc <<=1
        return crc & 0xFF
