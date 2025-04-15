# mock_Adafruit_DHT.py
DHT22 = 22


def read_retry(sensor, pin):
    # Fake temperature and humidity
    return (50.0, 22.3)
