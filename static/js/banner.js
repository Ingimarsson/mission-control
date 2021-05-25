// Create a client instance
banner_client = new Paho.MQTT.Client('ws://localhost:9001/ws', "clientId" + new Date().getTime());

// set callback handlers
banner_client.onConnectionLost = onConnectionLost;
banner_client.onMessageArrived = onMessageArrived;

// connect the client
banner_client.connect({onSuccess:onConnect});

// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("Banner onConnect");
  banner_client.subscribe("control/status");
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
  }
}

// called when a message arrives
function onMessageArrived(message) {


  var data = JSON.parse(message.payloadString);
  
  if(data.connected===true){
    document.getElementById("status_connected").style.display = "inline";
    document.getElementById("status_disconnected").style.display = "none";
  }else{
    document.getElementById("status_disconnected").style.display = "inline";
    document.getElementById("status_connected").style.display = "none";
  }

}
