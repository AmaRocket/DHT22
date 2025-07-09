import io
import sys
import json
import platform
from datetime import datetime
from threading import Lock
from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

from rich.live import Live
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel

import itrm
from ds18b20_module import DS18B20Module

# Configure itrm for Unicode plotting
itrm.Config.uni = True
itrm.Config.cols = 60
itrm.Config.rows = 15
itrm.Config.bold = True
itrm.Config.cmap = "rainbow"

# Initialize sensors
if platform.system() == "Linux":
    from dht22_module import DHT22Module
    dht22 = DHT22Module()
else:
    class MockDHT22Module:
        def get_sensor_readings(self):
            return 66.5, 66.5
    dht22 = MockDHT22Module()

ds18b20 = DS18B20Module()
console = Console()

# Flask + SocketIO setup
thread = None
thread_lock = Lock()
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# Prometheus metrics
inside_temperature = Gauge("inside_temperature_celsius", "Indoor temperature from DHT22")
inside_humidity = Gauge("inside_humidity_percent", "Indoor humidity from DHT22")
outside_temperature = Gauge("outside_temperature_celsius", "Outdoor temperature from DS18B20")

# Store max 120 points (1 hour with 3s interval)
temp_series = []
humidity_series = []
outdoor_series = []
timestamps = []

MAX_POINTS = 30

def background_thread():
    def sanitize(series):
        return [v if v is not None else 0 for v in series]

    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            in_temp, in_humidity = dht22.get_sensor_readings()
            out_temp, _ = ds18b20.get_sensor_readings()

            now = datetime.now().strftime("%H:%M:%S")
            timestamps.append(now)
            temp_series.append(in_temp)
            humidity_series.append(in_humidity)
            outdoor_series.append(out_temp)

            if len(temp_series) > MAX_POINTS:
                timestamps.pop(0)
                temp_series.pop(0)
                humidity_series.pop(0)
                outdoor_series.pop(0)

            if in_temp is not None:
                inside_temperature.set(in_temp)
            if in_humidity is not None:
                inside_humidity.set(in_humidity)
            if out_temp is not None:
                outside_temperature.set(out_temp)

            table = Table(title="Sensor Readings", expand=True)
            table.add_column("Sensor", style="cyan")
            table.add_column("Value", style="bold")
            table.add_row("Indoor Temp", f"{in_temp:.1f} °C" if in_temp is not None else "-")
            table.add_row("Indoor Humidity", f"{in_humidity:.1f} %" if in_humidity is not None else "-")
            table.add_row("Outdoor Temp", f"{out_temp:.1f} °C" if out_temp is not None else "-")

            if len(temp_series) >= 3:
                plot_output = itrm.iplot(
                    [sanitize(temp_series), sanitize(humidity_series), sanitize(outdoor_series)],
                    label=["Indoor Temp", "Humidity", "Outdoor Temp"],
                    overlay=True
                )
                chart_panel = Panel(plot_output, title="📊 Sensor Trends")
            else:
                chart_panel = Panel("[yellow]Waiting for data...[/]", title="📊 Sensor Trends")

            layout = Layout()
            layout.split(
                Layout(Panel(table, title="📋 Latest Sensor Data"), name="upper", size=10),
                Layout(chart_panel, name="lower")
            )

            live.update(layout)

            sensor_data = {
                "inside": {"temperature": in_temp or -1, "humidity": in_humidity or -1},
                "outside": {"temperature": out_temp or -1},
                "timestamp": datetime.now().isoformat(),
            }
            socketio.emit("updateSensorData", json.dumps(sensor_data))

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
