$(document).ready(function() {
  google.charts.load('current', {'packages':['line']});
  google.charts.setOnLoadCallback(load_sensors);
});

var days_back = 3;

function do_stuff(days) {
  days_back = days;
  load_sensors();
}


function load_sensors() {
  get_sensors().then(function(sensors) {
    assign_colors_to_sensors(sensors);
    drawLastReadings(sensors);
    drawFirmwareVersion(sensors);
    drawWarnings(sensors);
    load_temp_readings(sensors.filter(s => s.sensor_type === 'temperature'));
    load_humidity_readings(sensors.filter(s => s.sensor_type === 'humidity'));
    load_logs(sensors);
  });
}

function get_sensors() {
  return $.getJSON('/api/sensors', function(sensors) {
    return sensors;
  });
}

function get_last_sensor_value(sensor_id) {
  return $.getJSON('/api/sensors/' + sensor_id + '/readings/last', function(reading) {
    return reading;
  });
}

function get_readings(sensor) {
  return $.getJSON('/api/sensors/' + sensor.id + '/readings?days_back=' + days_back, function(readings) {
    return readings;
  });
}

function get_logs_for_sensor(sensor) {
  return $.getJSON('/api/sensors/' + sensor.id + '/logs', function(logs) {
    return logs;
  });
}

function assign_colors_to_sensors(sensors) {
  var colors = ['#4e73df', '#1cc88a', '#fB8c00', '#e53935', '#8e24aa'];
  for (var i = 0; i < sensors.length; i++) {
    if (i < colors.length) {
      sensors[i].color = colors[i];
    } else {
      sensors[i].color = '#000000';
    }
  }
}

function drawWarnings(sensors) {
  sensors.forEach(sensor => {
    if (sensor.is_active == true) {
      $('#sensor-' + sensor.id + '-warning').hide();
    }
  });
}

function drawLastReadings(sensors) {
  sensors.forEach(sensor => {
    get_last_sensor_value(sensor.id).then(function(reading) {
      var utcDate = new Date(reading.timestamp + "Z");
      $('#sensor-' + sensor.id + '-ts').text(formatUTCDate(utcDate));
      if (sensor.sensor_type == 'temperature') {
        $('#sensor-' + sensor.id + '-value').text(reading.value + "℃");
      } else if (sensor.sensor_type == 'humidity') {
        $('#sensor-' + sensor.id + '-value').text(reading.value + "%");
      } else {
        $('#sensor-' + sensor.id + '-value').text(reading.value + "???");
      }
      
      $('#sensor-' + sensor.id + '-color').css('border-left', '.25rem solid ' + sensor.color, 'important');
    });
  });
}

function drawFirmwareVersion(sensors) {
  sensors.forEach(sensor => {
    if (sensor.firmware_version != null) {
      $('#sensor-' + sensor.id + '-firmware').text("Firmware version: " +sensor.firmware_version);
    }
  });
}

async function load_temp_readings(sensors) {
  var readings = await Promise.all(sensors.map(get_readings));
  drawTemperatureChart(sensors, readings);
}

function drawTemperatureChart(sensors, readings) {
  var data = new google.visualization.DataTable();
  data.addColumn('date', 'Timestamps');
  sensors.forEach(sensor => {
    data.addColumn('number', sensor.name);
  });

  var keys = {}
  /* Collect all the keys first. */
  readings.forEach(sensorReading => {
    Object.keys(sensorReading).forEach(key => {
      keys[key] = [];
    });
  });
  for (key in keys) {
    for (var i = 0; i < readings.length; i++) {
      if (key in readings[i]) {
        keys[key].push(readings[i][key]);
      } else {
        keys[key].push(NaN);
      }
    }
  }
  var rows = [];
  for (key in keys) {
    rows.push([new Date(key + "Z")].concat(keys[key]));
  }
  data.addRows(rows);
  var options = {
    chart: {
      title: 'Temperature',
    },
    series: {},
    hAxis: {
      format: 'dd/MM HH:mm:ss',
    },
    vAxis: {
      textPosition: 'none',
    },
    legend: { position: 'none' }, /* Currently not supported to set bottom? */
  };

  for (var i = 0; i < sensors.length; i++) {
    options.series[i] = { color: sensors[i].color }
  }

  var chart = new google.charts.Line(document.getElementById('temperatureChart'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}

async function load_humidity_readings(sensors) {
  var readings = await Promise.all(sensors.map(get_readings));
  drawHumidityChart(sensors, readings);
}

function drawHumidityChart(sensors, readings) {
  var data = new google.visualization.DataTable();
  data.addColumn('date', 'Timestamps');
  sensors.forEach(sensor => {
    data.addColumn('number', sensor.name);
  });

  var keys = {}
  /* Collect all the keys first. */
  readings.forEach(sensorReading => {
    Object.keys(sensorReading).forEach(key => {
      keys[key] = [];
    });
  });
  for (key in keys) {
    for (var i = 0; i < readings.length; i++) {
      if (key in readings[i]) {
        keys[key].push(readings[i][key]);
      } else {
        keys[key].push(NaN);
      }
    }
  }
  var rows = [];
  for (key in keys) {
    rows.push([new Date(key + "Z")].concat(keys[key]));
  }
  data.addRows(rows);
  var options = {
    chart: {
      title: 'Humidity',
    },
    series: {},
    hAxis: {
      format: 'dd/MM HH:mm:ss',
    },
    vAxis: {
      textPosition: 'none',
    },
    legend: { position: 'none' }, /* Currently not supported to set bottom? */
  };

  for (var i = 0; i < sensors.length; i++) {
    options.series[i] = { color: sensors[i].color }
  }

  var chart = new google.charts.Line(document.getElementById('humidityChart'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}


async function load_logs(sensors) {
  var logs = await Promise.all(sensors.map(get_logs_for_sensor));
  var logBody = '';
  for (var i=0; i < sensors.length; i++) {
    if (logs[i].length == 0) {
      continue;
    }
    logBody += '<div id="#logsForSensor' +i +'" class="text-xs font-weight-bold text-uppercase mb-1">' +sensors[i].name +'</div>';
    logs[i].reverse();
    logs[i].forEach(logrow => {
      logBody += '<div class="text-xs mb-1">' +formatUTCDate(new Date(logrow.timestamp + "Z")) +': ' +logrow.message +'</div>';
    });
  }
  $('#logsBody').append(logBody);
}


/* There must be a better way to do this? */
function formatUTCDate(utcDate) {
  return utcDate.getFullYear() + "-"
         + zeroPadding(utcDate.getMonth()+1) + "-"
         + zeroPadding(utcDate.getDate()) + " "
         + zeroPadding(utcDate.getHours()) + ":"
         + zeroPadding(utcDate.getMinutes()) + ":"
         + zeroPadding(utcDate.getSeconds());
}

function zeroPadding(number) {
  return ("0" + number).slice(-2);
}