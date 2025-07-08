import os
import glob
import time
import datetime

# these tow lines mount the device:
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


# ds18b20_module.py

import glob
import time
import datetime
import os

# Load required kernel modules
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


class DS18B20Module:
    def __init__(self):
        self.device_folder = self._find_device()

    def _find_device(self):
        devices = glob.glob('/sys/bus/w1/devices/28*')
        return devices[0] if devices else None

    def get_sensor_readings(self):
        if not self.device_folder:
            return None, None

        try:
            with open(f"{self.device_folder}/w1_slave", "r") as f:
                lines = f.readlines()

            if "YES" in lines[0]:
                temp_pos = lines[1].find("t=")
                if temp_pos != -1:
                    temp_string = lines[1][temp_pos + 2:]
                    temp_c = float(temp_string) / 1000.0
                    temp_f = temp_c * 9.0 / 5.0 + 32.0
                    return temp_c, temp_f
        except Exception as e:
            print(f"DS18B20 read error: {e}")

        return None, None


# s = DS18B20Module()
# s.find_sensors()
#
# while True:
#     s.read_temp()
#     s.print_temps()
#     s.clear_log()