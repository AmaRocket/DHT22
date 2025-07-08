# mock_Adafruit_DHT.py
DHT22 = 22


def read_retry(sensor, pin):
    # Fake temperature and humidity
    return (55.5, 22.2)
