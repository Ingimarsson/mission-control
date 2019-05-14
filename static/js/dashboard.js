var track_id = 0;
var track = Object;

$(document).ready(function() {
    $('#drivers').dropdown({allowAdditions: true, fullTextSearch: 'exact'});
    $('#tracks').dropdown({allowAdditions: true, fullTextSearch: 'exact'});

    $("#start").on('click', function(e) {
        $("#modal_start").modal("show");
    });

    $("#stop").on('click', function(e) {
        $("#modal_stop").modal("show");
    });

    $("#stop_recording").on('click', function(e) {
        $.get( "/api/recording/stop", function( data ) {
            if (data == "ok") {
                $("#modal_stop").modal("hide");
            }
        });
    });

    $("button[type='submit']", "#modal_start").on('click', function(e) {
        e.preventDefault();

        $("button[type='submit']").attr("disabled", "disabled");

        var formdata = new FormData();
        formdata.append("driver", $("[name='driver']").val());
        formdata.append("track", $("[name='track']").val());
        formdata.append("comment", $("[name='comment']").val());

        $.ajax({
            url: '/api/recording/start',
            type: 'POST',
            data: formdata,
            contentType: false,
            cache: false,
            processData: false,
            success: function(d) {
                console.log(d);
                if (d == "ok") {
                    $("button[type='submit']").attr("disabled", null);
                    $("#modal_start").modal("hide");
                }
            }
        });
    });

    client = new Paho.MQTT.Client('wss://control.teamspark.is:8083/ws', "clientId" + new Date().getTime());

    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    client.connect({onSuccess:onConnect, userName: 'spark', password: 'spark'});

    function onConnect() {
      console.log("onConnect");
      client.subscribe("control/status");
    }

    function onConnectionLost(responseObject) {
      if (responseObject.errorCode !== 0) {
	console.log("onConnectionLost:"+responseObject.errorMessage);
      }
    }

    function onMessageArrived(message) {
      data = JSON.parse(message.payloadString);
      if (data.recording == false) {
        data.recording = "Not Recording";
        $('#start').css('display', 'block');
        $('#stop').css('display', 'none');
 
      } else {
        data.recording = "Recording";
        $('#start').css('display', 'none');
        $('#stop').css('display', 'block');
      }

      for (var d in data) {
        $("#"+d).text(data[d]);
      }
        
      $("#lat").text(data.x);
      $("#lon").text(data.y);

      if (data.track != track_id) {
        $.ajax({
            dataType: "json",
            url: "/api/track/" + data.track,
            success: function(t) {
                draw_track(t,0,0);
                track = t
                track_id = data.track;
            }
        });
      }

      if (track_id != 0) {
        draw_track(track, data.x, data.y);
        $("#track", "table").text(track.name);
      }
        var html = "";
      for (var s in data.laps) {
        html = html + "<tr><td>#"+data.laps[s].id+"</td><td>"+data.laps[s].time+" s</td><td>"+data.laps[s].dtime+" s</td><td>"+data.laps[s].energy+" Wh</td><td>"+data.laps[s].denergy+" Wh</td></tr>";
;
 ;
      }
      $("#lap_table").html(html);

    }
});

