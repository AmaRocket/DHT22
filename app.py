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

import plotext as plt
from datetime import datetime
from rich.console import Console
from rich.table import Table


from rich.layout import Layout
from rich.panel import Panel

from ds18b20_module import DS18B20Module


# Initialize sensors

if platform.system() == "Linux":
    from dht22_module import DHT22Module
    dht22 = DHT22Module()
else:
    # Mock for local dev on Mac
    class MockDHT22Module:
        def get_sensor_readings(self):
            # Return some fake readings for dev/test
            return 66.5, 66.5
    dht22 = MockDHT22Module()


ds18b20 = DS18B20Module()             # Outside temp only
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

MAX_POINTS = 20


def background_thread():
    with Live(console=console, refresh_per_second=1, screen=False) as live:
        while True:
            # Sensor readings
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

            # Prometheus
            if in_temp is not None:
                inside_temperature.set(in_temp)
            if in_humidity is not None:
                inside_humidity.set(in_humidity)
            if out_temp is not None:
                outside_temperature.set(out_temp)

            # Prepare table
            table = Table(title="Sensor Readings", expand=True)
            table.add_column("Sensor", style="cyan")
            table.add_column("Value", style="bold")
            table.add_row("Indoor Temp", f"{in_temp:.1f} °C" if in_temp is not None else "-")
            table.add_row("Indoor Humidity", f"{in_humidity:.1f} %" if in_humidity is not None else "-")
            table.add_row("Outdoor Temp", f"{out_temp:.1f} °C" if out_temp is not None else "-")

            # Prepare plot
            plt.clear_figure()
            plt.canvas_color("black")
            plt.axes_color("black")
            plt.ticks_color("white")
            plt.title("Temperature & Humidity Trends")

            x_vals = list(range(len(temp_series)))  # Use numeric x-axis

            if len(temp_series) >= 3:
                plt.plot(x_vals, temp_series, label="Indoor Temp °C", marker="dot", color="red")
            if len(humidity_series) >= 3:
                plt.plot(x_vals, humidity_series, label="Humidity %", marker="dot", color="cyan")
            if len(outdoor_series) >= 3:
                plt.plot(x_vals, outdoor_series, label="Outdoor Temp °C", marker="dot", color="green")

            # Auto-scale Y with margin
            try:
                all_values = temp_series + humidity_series + outdoor_series
                clean_values = [v for v in all_values if v is not None]
                min_y = min(clean_values)
                max_y = max(clean_values)
                plt.ylim(min_y - 2, max_y + 2)
            except ValueError:
                pass  # In case of all None

            # Capture plot output
            plot_buffer = io.StringIO()
            sys.stdout = plot_buffer
            plt.show()
            sys.stdout = sys.__stdout__
            plot_output = plot_buffer.getvalue()

            layout = Layout()
            layout.split(
                Layout(Panel(table, title="📋 Latest Sensor Data"), name="upper", size=10),
                Layout(Panel(plot_output, title="📊 Sensor Trends"), name="lower")
            )

            live.update(layout)

            # Emit to web frontend
            sensor_data = {
                "inside": {"temperature": in_temp or -1, "humidity": in_humidity or -1},
                "outside": {"temperature": out_temp or -1},
                "timestamp": datetime.now().isoformat(),
            }
            socketio.emit("updateSensorData", json.dumps(sensor_data))

            # console.log(f"[DEBUG] Temp={in_temp}°C Humidity={in_humidity}% Outdoor={out_temp}°C")

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