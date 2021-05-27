$(document).ready(function(){
  var track_id = 0;
  var track = Object;

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

    lat = data.gps_lat;
    lon = data.gps_lon;

    // For rendering track when ID sent from backend
    if (track_id === 0 && data.track != 0) {
      track_id = data.track;
      $.ajax({
          dataType: "json",
          url: "/api/track/" + track_id,
          success: function(t) {
              draw_track(t,lon, lat);
              track = t
          }
      });
    }


    if (track_id != 0) {
      draw_track(track, lon, lat);
      $("#track", "table").text(track.name);
    }

    var html = "";

    for (var s in data.laps) {
      html = html + "<tr><td>#"+data.laps[s].id+"</td><td>"+data.laps[s].distance+" km</td><td>"+data.laps[s].total_time+" s</td><td>"+data.laps[s].lap_time+" s</td></tr>";
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
          url: "/api/track/" + track_id,
          success: function(t) {
              draw_track(t,0,0);
              track = t
          }
      });
  });
});
