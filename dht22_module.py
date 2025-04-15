# import Adafruit_DHT
try:
    import Adafruit_DHT
except ImportError:
    import mock_Adafruit_DHT as Adafruit_DHT

import time


class DHT22Module:
    def __init__(self, pin=4):
        self.dht_device = Adafruit_DHT.DHT22

    def get_sensor_readings(self):
        while True:
            try:
                sensor = Adafruit_DHT.DHT22
                pin = 4
                humidity, temperature_c = Adafruit_DHT.read_retry(sensor, pin)
                print(f"Temp: {temperature_c} C    Humidity: {humidity}% ")
                return temperature_c, humidity

            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                print(error.args[0])
                time.sleep(2.0)
                continue
            except Exception as error:
                print(error)
                raise error
