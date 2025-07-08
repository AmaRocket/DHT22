import os
import glob
import time
import sys

base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')

if not device_folders:
    print("❌ No DS18B20 sensor detected! Check wiring and reboot.")
    sys.exit(1)

device_file = device_folders[0] + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

while True:
    print(f"Temperature: {read_temp():.2f}°C")
    time.sleep(2)