var x = Object;
var id = 0;

$(document).ready(function() {
    $("#add").on('click', function(e) {
        $("#modal_add").modal("show");
    });

    $("#render", "#modal_add").on('click', function(e) {
        render("#modal_add", 'track_add');
    });

    $("#render", "#modal_edit").on('click', function(e) {
        render("#modal_edit", 'track_edit');
    });

    $("button[type='submit']", "#modal_add").on('click', function(e) {
        e.preventDefault();
        render("#modal_add", 'track_add');

        $("button[type='submit']").attr("disabled", "disabled");

        var formdata = new FormData();
        formdata.append("name", $("[name='name']", "#modal_add").val());
        formdata.append("points", JSON.stringify({'gate': x.gate, 'track':x.track}));

        $.ajax({
            url: '/api/track/add',
            type: 'POST',
            data: formdata,
            contentType: false,
            cache: false,
            processData: false,
            success: function(d) {
                console.log(d);
                if (d == "ok") {
                    $("button[type='submit']").attr("disabled", null);
                    $("#modal_add").modal("hide");
                    location.reload();
                }
            }
        });
    });

    $("button[type='submit']", "#modal_edit").on('click', function(e) {
        e.preventDefault();
        render("#modal_edit", 'track_edit');

        $("button[type='submit']").attr("disabled", "disabled");

        var formdata = new FormData();
        formdata.append("name", $("[name='name']", "#modal_edit").val());
        formdata.append("points", JSON.stringify({'gate': x.gate, 'track':x.track}));

        $.ajax({
            url: '/api/track/edit/'+ id,
            type: 'POST',
            data: formdata,
            contentType: false,
            cache: false,
            processData: false,
            success: function(d) {
                console.log(d);
                if (d == "ok") {
                    $("button[type='submit']").attr("disabled", null);
                    $("#modal_edit").modal("hide");
                    location.reload();
                }
            }
        });
    });

    $(".edit_button").on('click', function() {
	id = $(this).parent().parent().data("id");

        $.ajax({
            dataType: "json",
            url: "/api/settings_track/" + id,
            success: function(track) {
                console.log(track)
                $("[name='name']", "#modal_edit").val(track.name);
                $("[name='gate']", "#modal_edit").val(track.gate[0][0]+","+track.gate[0][1]+"\n"+track.gate[1][0]+","+track.gate[1][1]);

                var coords = [];

                for (var t in track.track) {
                    coords.push(track.track[t].join(","));

                }
                $("[name='track']", "#modal_edit").val(coords.join("\n"));

                $("[name='name']", "#modal_edit").val(track.name);

	        render("#modal_edit", 'track_edit');
	        $("#modal_edit").modal("show");
            }
        });
    });
});

function render(modal, c='track') {
    x.track = [];
    x.gate = []

    track = $("[name='track']", modal).val().split("\n");
    gate = $("[name='gate']", modal).val().split("\n");

    for (var t in track) {
        s = track[t].split(",");
        x.track.push([parseFloat(s[0]), parseFloat(s[1])]);
    }

    for (var g in gate) {
        s = gate[g].split(",");
        x.gate.push([parseFloat(s[0]), parseFloat(s[1])]);
    }

    console.log(x);

    draw_track(x, 0,0,c);
}
