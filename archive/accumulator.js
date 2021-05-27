// Create a client instance
client = new Paho.MQTT.Client('ws://localhost:9001/ws', "clientId" + new Date().getTime());

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect, userName: 'spark', password: 'spark'});

lookup = [3.64, 3.62, 3.60, 3.58, 3.56, 3.54, 3.52, 3.49, 3.47, 3.45, 3.43, 3.41, 3.38, 3.36, 3.34, 3.32, 3.29, 3.27, 3.25, 3.22, 3.20, 3.18, 3.16, 3.13, 3.11, 3.09, 3.06, 3.04, 3.02, 2.99, 2.97, 2.94, 2.92, 2.90, 2.87, 2.85, 2.83, 2.80, 2.78, 2.76, 2.73, 2.71, 2.69, 2.66, 2.64, 2.62, 2.59, 2.57, 2.55, 2.52, 2.50, 2.48, 2.45, 2.43, 2.41, 2.39, 2.36, 2.34, 2.32, 2.29, 2.27, 2.25, 2.23, 2.21, 2.18, 2.16, 2.14, 2.12, 2.10, 2.08, 2.05, 2.03, 2.01, 1.99, 1.97, 1.95, 1.93, 1.91, 1.89, 1.87, 1.85, 1.83, 1.81, 1.79, 1.77, 1.75, 1.73, 1.71, 1.69, 1.67, 1.66, 1.64, 1.62, 1.60, 1.58, 1.56, 1.55, 1.53, 1.51, 1.49, 1.48, 1.46, 1.44, 1.43, 1.41, 1.39, 1.38, 1.36, 1.35, 1.33, 1.32, 1.30, 1.28, 1.27, 1.25, 1.24, 1.22, 1.21, 1.20, 1.18, 1.17, 1.15, 1.14, 1.13, 1.11, 1.10, 1.09, 1.07, 1.06, 1.05, 1.04, 1.02, 1.01, 1.00, 0.99, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.91, 0.89, 0.88, 0.87, 0.86, 0.85, 0.84, 0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.77, 0.76, 0.75, 0.74, 0.74, 0.73, 0.72, 0.71, 0.70, 0.69, 0.68, 0.68, 0.67, 0.66, 0.65, 0.64, 0.64, 0.63, 0.62, 0.61, 0.60, 0.60, 0.59, 0.58, 0.58, 0.57, 0.56, 0.56, 0.55, 0.54, 0.54, 0.53, 0.52, 0.52, 0.51, 0.50, 0.50, 0.49, 0.49, 0.48, 0.47, 0.47, 0.46, 0.46, 0.45, 0.45, 0.44];

// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  client.subscribe("control/#");
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
  }
}

// called when a message arrives
function onMessageArrived(message) {
  path = message.destinationName.split('/')[1];
  x = message.payloadString.split(' ');
  total = 0;

  if (path == 'voltage') {
    for (i = 1; i < 145; i++) {
      var span = document.getElementById('voltage-'+i);
      if (parseFloat(x[i-1]) < 3.5) {
        span.innerHTML = parseFloat(x[i-1]).toFixed(2) + ' V <a class="ui red empty circular label"></a>';
      } else if (parseFloat(x[i-1]) < 3.7) {
        span.innerHTML = parseFloat(x[i-1]).toFixed(2) + ' V <a class="ui yellow empty circular label"></a>';
      } else {
        span.innerHTML = parseFloat(x[i-1]).toFixed(2) + ' V';
      }
      total = total + parseFloat(x[i-1]);
      var span = document.getElementById('voltage-total');
      span.innerHTML = total.toFixed(2) + ' V';
    }
  }

  if (path == 'temperature') {
    for (i = 1; i < 145; i++) {
      var span = document.getElementById('temperature-'+i);
      var temp = parseFloat(x[i-1])/10;

      var j = 0;
      if(temp > 0 && temp < 5) {
        while (temp < lookup[j] && j < 300) { j++; }
      }

      j = (j/2).toFixed(1);

      if (j > 50.0) {
        span.innerHTML = j + ' °C <a class="ui red empty circular label"></a>';
      } else if (j > 40.0) {
        span.innerHTML = j + ' °C <a class="ui yellow empty circular label"></a>';
      } else {
        span.innerHTML = j + ' °C';
      }
    }
  }
}
