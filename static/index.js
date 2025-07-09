var temperatureHistoryDiv = document.getElementById("temperature-history");
var humidityHistoryDiv = document.getElementById("humidity-history");
var outdoorHistoryDiv = document.getElementById("outdoor-history"); // ✅

var temperatureGaugeDiv = document.getElementById("temperature-gauge");
var humidityGaugeDiv = document.getElementById("humidity-gauge");
var outdoorGaugeDiv = document.getElementById("outdoor-gauge"); // ✅

var graphConfig = {
  displayModeBar: false,
  responsive: true,
};

// History Data
var temperatureTrace = {
  x: [],
  y: [],
  name: "Indoor Temp",
  mode: "lines+markers",
  type: "line",
};
var humidityTrace = {
  x: [],
  y: [],
  name: "Humidity",
  mode: "lines+markers",
  type: "line",
};
var outdoorTrace = {
  x: [],
  y: [],
  name: "Outdoor Temp",
  mode: "lines+markers",
  type: "line",
};

var temperatureLayout = {
  autosize: true,
  title: { text: "Indoor Temperature" },
  font: { size: 14, color: "#000" },
  colorway: ["#B22222"],
  margin: { t: 30, b: 30, l: 50, r: 20, pad: 0 },
};
var humidityLayout = {
  autosize: true,
  title: { text: "Humidity" },
  font: { size: 14, color: "#7f7f7f" },
  colorway: ["#00008B"],
  margin: { t: 30, b: 30, l: 50, r: 20, pad: 0 },
};
var outdoorLayout = {
  autosize: true,
  title: { text: "Outdoor Temperature" },
  font: { size: 14, color: "#2f4f4f" },
  colorway: ["#228B22"],
  margin: { t: 30, b: 30, l: 50, r: 20, pad: 0 },
};

Plotly.newPlot(temperatureHistoryDiv, [temperatureTrace], temperatureLayout, graphConfig);
Plotly.newPlot(humidityHistoryDiv, [humidityTrace], humidityLayout, graphConfig);
Plotly.newPlot(outdoorHistoryDiv, [outdoorTrace], outdoorLayout, graphConfig); // ✅

// Gauge Data
var layout = {
  width: 350,
  height: 250,
  paper_bgcolor: "#a5d8d3",
  plot_bgcolor: "#a5d8d3",
  margin: { t: 0, b: 0, l: 0, r: 0 },
};

var temperatureData = [{
  domain: { x: [0, 1], y: [0, 1] },
  value: 0,
  title: { text: "Indoor Temp" },
  type: "indicator",
  mode: "gauge+number+delta",
  delta: { reference: 25 },
  gauge: {
    axis: { range: [null, 50] },
    steps: [
      { range: [0, 20], color: "lightgray" },
      { range: [20, 30], color: "gray" },
      { range: [30, 40], color: "orange" },
      { range: [40, 50], color: "red" },
    ],
    threshold: {
      line: { color: "red", width: 4 },
      thickness: 0.75,
      value: 25,
    },
  },
}];

var humidityData = [{
  domain: { x: [0, 1], y: [0, 1] },
  value: 0,
  title: { text: "Humidity" },
  type: "indicator",
  mode: "gauge+number+delta",
  delta: { reference: 45 },
  gauge: {
    axis: { range: [null, 100] },
    steps: [
      { range: [0, 20], color: "white" },
      { range: [20, 35], color: "lightgray" },
      { range: [35, 50], color: "gray" },
      { range: [50, 60], color: "yellow" },
      { range: [60, 80], color: "orange" },
      { range: [80, 100], color: "red" },
    ],
    threshold: {
      line: { color: "red", width: 4 },
      thickness: 0.75,
      value: 45,
    },
  },
}];

var outdoorData = [{ // ✅
  domain: { x: [0, 1], y: [0, 1] },
  value: 0,
  title: { text: "Outdoor Temp" },
  type: "indicator",
  mode: "gauge+number+delta",
  delta: { reference: 10 },
  gauge: {
    axis: { range: [null, 50] },
    steps: [
      { range: [0, 10], color: "#d0f0c0" },
      { range: [10, 20], color: "#a2d5ab" },
      { range: [20, 30], color: "#7dc77d" },
      { range: [30, 50], color: "#ffcc99" },
    ],
    threshold: {
      line: { color: "green", width: 4 },
      thickness: 0.75,
      value: 15,
    },
  },
}];

Plotly.newPlot(temperatureGaugeDiv, temperatureData, layout, graphConfig);
Plotly.newPlot(humidityGaugeDiv, humidityData, layout, graphConfig);
Plotly.newPlot(outdoorGaugeDiv, outdoorData, layout, graphConfig); // ✅

let newTempXArray = [], newTempYArray = [];
let newHumidityXArray = [], newHumidityYArray = [];
let newOutdoorXArray = [], newOutdoorYArray = []; // ✅

let MAX_GRAPH_POINTS = 12;
let ctr = 0;

function updateBoxes(temperature, humidity, outTemp) {
  document.getElementById("temperature").innerHTML = temperature + " C";
  document.getElementById("humidity").innerHTML = humidity + " %";
  document.getElementById("out_temp").innerHTML = outTemp + " C"; // ✅
}

function updateGauge(temperature, humidity, outTemp) {
  Plotly.update(temperatureGaugeDiv, { value: [temperature] });
  Plotly.update(humidityGaugeDiv, { value: [humidity] });
  Plotly.update(outdoorGaugeDiv, { value: [outTemp] }); // ✅
}

function updateCharts(lineChartDiv, xArray, yArray, sensorRead) {
  if (xArray.length >= MAX_GRAPH_POINTS) xArray.shift();
  if (yArray.length >= MAX_GRAPH_POINTS) yArray.shift();
  xArray.push(ctr++);
  yArray.push(sensorRead);
  Plotly.update(lineChartDiv, { x: [xArray], y: [yArray] });
}

function updateSensorReadings(jsonResponse) {
  let temperature = parseFloat(jsonResponse.temperature || -1);
  let humidity = parseFloat(jsonResponse.humidity || -1);
  let outTemp = parseFloat(jsonResponse.out_temp || -1);

  updateBoxes(
    temperature >= 0 ? temperature.toFixed(2) : "-",
    humidity >= 0 ? humidity.toFixed(2) : "-",
    outTemp >= 0 ? outTemp.toFixed(2) : "-"
  );

  updateGauge(
    temperature >= 0 ? temperature : 0,
    humidity >= 0 ? humidity : 0,
    outTemp >= 0 ? outTemp : 0
  );

  if (temperature >= 0)
    updateCharts(temperatureHistoryDiv, newTempXArray, newTempYArray, temperature);
  if (humidity >= 0)
    updateCharts(humidityHistoryDiv, newHumidityXArray, newHumidityYArray, humidity);
  if (outTemp >= 0)
    updateCharts(outdoorHistoryDiv, newOutdoorXArray, newOutdoorYArray, outTemp);


  updateCharts(temperatureHistoryDiv, newTempXArray, newTempYArray, temperature);
  updateCharts(humidityHistoryDiv, newHumidityXArray, newHumidityYArray, humidity);
  updateCharts(outdoorHistoryDiv, newOutdoorXArray, newOutdoorYArray, outTemp);
}

// SocketIO
var socket = io.connect();
socket.on("updateSensorData", function (msg) {
  var sensorReadings = JSON.parse(msg);
  updateSensorReadings(sensorReadings);
});