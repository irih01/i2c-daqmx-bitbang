from bitbang_i2c import BitBangI2C
from htu21d import HTU21D
from bmp280 import BM280
import time

SCL_PIN = "Dev1/port0/line0"
SDA_PIN = "Dev1/port0/line1"

i2c = BitBangI2C(SCL_PIN, SDA_PIN, delay=0.001)
htu = HTU21D(i2c)
bmp = BM280(i2c)

try:
    while True:
        temp1 = htu.read_temperature()
        temp2 =  bmp.read_temperature()
        hum = htu.read_humidity()

        print(f"HTU21D Temp: {temp1:.2f} *C, Humidity: {hum:.2f}%")
        print(f"BMP280 Temp: {temp2:.2f} *C")
        print("-" * 30)

        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
finally:
    i2c.close()
