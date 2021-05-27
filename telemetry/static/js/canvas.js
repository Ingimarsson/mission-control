function draw_track(track, x, y, c = 'track_map') {
    var canvas = document.getElementById(c);
    var ctx = canvas.getContext('2d');

    ctx.clearRect(0,0,700,700);

    var xs = [];
    var ys = [];
    var xg = [];
    var yg = [];
    x = Math.abs(x);
    y = Math.abs(y);

    for (var s in track.track) {
        xs.push(Math.abs(track.track[s][0]));
        ys.push(Math.abs(track.track[s][1]));
    }

    for (var s in track.gate) {
        xg.push(Math.abs(track.gate[s][0]));
        yg.push(Math.abs(track.gate[s][1]));
    }

    var Dx = Math.max(...xs) - Math.min(...xs);
    var Dy = Math.max(...ys) - Math.min(...ys);

    if (Dy > Dx) {
        var ytemp = ys;
        ys = xs;
        xs = ytemp;
        ytemp = yg;
        yg = xg;
        xg = ytemp;

        var Dx = Math.max(...xs) - Math.min(...xs);
        var Dy = Math.max(...ys) - Math.min(...ys);
    }

    var x0 = Math.min(...xs);
    var y0 = Math.min(...ys);

    canvas.height = 700*Dy/Dx;

    //console.log(Dx)

    ctx.beginPath();
    ctx.moveTo((0.9*((xs[0]-x0)/Dx)+0.05)*700, (0.9*((ys[0]-y0)/Dy)+0.05)*canvas.height);
    // Drow the track
    for (var s=1; s < xs.length; s++) {
        ctx.lineTo((0.9*((xs[s]-x0)/Dx)+0.05)*700, (0.9*((ys[s]-y0)/Dy)+0.05)*canvas.height);
    }
    //Close the loop
    ctx.lineTo((0.9*((xs[0]-x0)/Dx)+0.05)*700, (0.9*((ys[0]-y0)/Dy)+0.05)*canvas.height);
    ctx.closePath();
    ctx.stroke();

    // Draw gate
    ctx.beginPath();
    ctx.moveTo((0.9*((xg[0]-x0)/Dx)+0.05)*700, (0.9*((yg[0]-y0)/Dy)+0.05)*canvas.height);
    ctx.lineTo((0.9*((xg[1]-x0)/Dx)+0.05)*700, (0.9*((yg[1]-y0)/Dy)+0.05)*canvas.height);
    ctx.closePath();
    ctx.strokeStyle = '#00F';
    ctx.stroke();

    // Dtaw location dot
    ctx.arc((0.9*((x-x0)/Dx)+0.05)*700, (0.9*((y-y0)/Dy)+0.05)*canvas.height, 4, 0, Math.PI*2);
    ctx.fillStyle = '#F00';
    ctx.fill();
}
