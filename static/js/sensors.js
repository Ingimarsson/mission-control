// Create a client instance
client = new Paho.MQTT.Client('ws://localhost:9001/ws', "clientId" + new Date().getTime());

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect, userName: 'spark', password: 'spark'});

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
  msg = message.payloadString;

  if (path == 'latest') {
    data = JSON.parse(msg);

    for (var k in data) {
        $("tr[data-path='"+k+"'] > .value").html(data[k]);
    }
  }

  if (path == 'count') {
    data = JSON.parse(msg);

    for (var k in data) {
        $("tr[data-path='"+k+"'] > .frequency").html(data[k] + " val/s");
    }
  }

}

$(document).ready(function() {
    $("#upload").on('click', function(e) {
        $("#modal_upload").modal("show");
    });

    $("input:text").click(function() {
        $(this).parent().find("input:file").click();
    });

    $('input:file', '.ui.left.action.input').on('change', function(e) {
        var name = e.target.files[0].name;
        $('input:text', $(e.target).parent()).val(name);
    });

    $("button[type='submit']").on('click', function(e) {
        e.preventDefault();

        $("button[type='submit']").attr("disabled", "disabled");

        var formdata = new FormData();
        formdata.append("file", $("input[type='file']")[0].files[0]);

        $.ajax({
            url: '/api/sensors/upload',
            type: 'POST',
            data: formdata,
            contentType: false,
            cache: false,
            processData: false,
            success: function(d) {
                if (d == "ok") {
                    location.reload();
                } else {
                    alert("Unexpected error occurred. Contact system administrator.");
                }
            }
        });
    });
});
