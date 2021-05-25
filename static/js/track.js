var track_id = 0;
var track = Object;

$(document).ready(function(){

  client = new Paho.MQTT.Client('ws://localhost:9001/ws', "clientId" + new Date().getTime());

  client.onConnectionLost = onConnectionLost;
  client.onMessageArrived = onMessageArrived;

  client.connect({onSuccess:onConnect});

  function onConnect() {
    console.log("onConnect");
    client.subscribe("control/gps");
  }

  function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
       console.log("onConnectionLost:"+responseObject.errorMessage);
    }
  }

  function onMessageArrived(message) {
    data = JSON.parse(message.payloadString);
    console.log(data.laps)
    //console.log(data.gps_lon+"\t"+data.gps_lat);
    // For rendering track when ID sent from backend
    /*
    if (data.track != track_id) {


      $.ajax({
          dataType: "json",
          url: "/api/track/" + track_id,
          success: function(t) {
              draw_track(,x,y);
              track = t
              track_id = data.track;
          }
      });

    }
    */
    if (track_id != 0) {
      draw_track(track, data.gps_lon, data.gps_lat);
      $("#track", "table").text(track.name);
    }

    var html = "";

    for (var s in data.laps) {
      html = html + "<tr><td>#"+data.laps[s].id+"</td><td>"+data.laps[s].time+" s</td><td>"+data.laps[s].dtime+" s</td><td>"+data.laps[s].energy+" Wh</td><td>"+data.laps[s].denergy+" Wh</td></tr>";
    }
    $("#lap_table").html(html);

  }


  $('#track_selection').dropdown({allowAdditions: true, fullTextSearch: 'exact'});

  $('#select_track').on('click', function(e) {
      e.preventDefault();
      console.log("track selected");

      var data = $("[name='track_select_input']").val();
      track_id = data;
      console.log(data);
      $.ajax({
          dataType: "json",
          url: "/api/track/" + data,
          success: function(t) {
              draw_track(t,0,0);
              track = t
          }
      });
      console.log("track set to ")
      console.log(track_id)
  });
});
