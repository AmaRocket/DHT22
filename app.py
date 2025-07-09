import json
import platform
from datetime import datetime
from threading import Lock
from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest


from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.live import Live


import board
from dht22_module import DHT22Module
from ds18b20_module import DS18B20Module

# Init sensors
if platform.system() == "Linux":
    from dht22_module import DHT22Module
    dht22 = DHT22Module()
else:
    class MockDHT22Module:
        def get_sensor_readings(self):
            return 66.5, 66.5
    dht22 = MockDHT22Module()

ds18b20 = DS18B20Module()

# Flask & metrics
console = Console()
thread = None
thread_lock = Lock()
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

inside_temperature = Gauge("inside_temperature_celsius", "Indoor temperature from DHT22")
inside_humidity = Gauge("inside_humidity_percent", "Indoor humidity from DHT22")
outside_temperature = Gauge("outside_temperature_celsius", "Outdoor temperature from DS18B20")



def background_thread():
    while True:
        # Sensor readings
        in_temp, in_humidity = dht22.get_sensor_readings()
        out_temp, _ = ds18b20.get_sensor_readings()

        # Prometheus
        if in_temp is not None:
            inside_temperature.set(in_temp)
        if in_humidity is not None:
            inside_humidity.set(in_humidity)
        if out_temp is not None:
            outside_temperature.set(out_temp)

        # JSON for frontend
        sensor_data = {
            "inside": {
                "temperature": in_temp if in_temp is not None else -1,
                "humidity": in_humidity if in_humidity is not None else -1,
            },
            "outside": {
                "temperature": out_temp if out_temp is not None else -1,
            },
            "timestamp": datetime.now().isoformat()
        }

        socketio.emit("updateSensorData", json.dumps(sensor_data))

        # CLI live update
        console.clear()
        table = Table(title="Sensor Readings")

        table.add_column("Sensor", style="cyan", no_wrap=True)
        table.add_column("Value", style="bold")

        table.add_row("Indoor Temp", f"{in_temp:.1f}   C" if in_temp else "-")
        table.add_row("Humidity", f"{in_humidity:.1f} %" if in_humidity else "-")
        table.add_row("Outdoor Temp", f"{out_temp:.1f}   C" if out_temp else "-")

        console.print(table)

        socketio.sleep(3)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@socketio.on("connect")
def connect():
    global thread
    print(f"Client connected: {request.sid}")
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.on("disconnect")
def disconnect():
    print(f"Client disconnected: {request.sid}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
