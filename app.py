import json
import platform
from datetime import datetime
from random import random
from threading import Lock

# import flask_socketio as flask_socketio
from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.live import Live

if platform.system() == "Linux":
    import board

    from dht22_module import DHT22Module
    dht22_module = DHT22Module(board.D18)
else:
    # Mock for local dev on Mac
    class MockDHT22Module:
        def get_sensor_readings(self):
            # Return some fake readings for dev/test
            return 66.5, 66.5

    dht22_module = MockDHT22Module()


thread = None
thread_lock = Lock()
console = Console()

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")


# Prometheus metrics
temperature_gauge = Gauge(
    "tunnel_temperature_celsius",
    "Temperature in Celsius in the tunnel"
)
humidity_gauge = Gauge(
    "tunnel_humidity_percent", "Humidity percentage in the tunnel"
)


"""
Background Thread
"""


def background_thread():
    while True:
        temperature, humidity = dht22_module.get_sensor_readings()

        # Prometheus metrics
        if temperature is not None:
            temperature_gauge.set(temperature)
        if humidity is not None:
            humidity_gauge.set(humidity)

        sensor_readings = {
            "temperature": temperature if temperature is not None else -1,
            "humidity": humidity if humidity is not None else -1,
        }
        sensor_json = json.dumps(sensor_readings)
        socketio.emit("updateSensorData", sensor_json)

        # CLI live update
        console.clear()
        table = Table(title="Sensor Readings")

        table.add_column("Sensor", style="cyan", no_wrap=True)
        table.add_column("Value", style="bold")

        table.add_row("Temp", f"{temperature:.1f} °C" if temperature else "-")
        table.add_row("Humidity", f"{humidity:.1f} %" if humidity else "-")


        console.print(table)

        socketio.sleep(3)


"""
Serve root index file
"""


@app.route("/")
def index():
    return render_template("index.html")


"""
Prometheus metrics endpoint
"""


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


"""
Decorator for connect
"""


@socketio.on("connect")
def connect():
    global thread
    print("Client connected")

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


"""
Decorator for disconnect
"""


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
