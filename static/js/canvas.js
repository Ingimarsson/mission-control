function draw_track(track, x, y, c = 'track') {
    var canvas = document.getElementById(c);
    var ctx = canvas.getContext('2d');

    ctx.clearRect(0,0,700,700);

    var xs = [];
    var ys = [];

    for (var s in track.track) {
        xs.push(track.track[s][0]);
        ys.push(track.track[s][1]);
    }

    var Dx = Math.max(...xs) - Math.min(...xs);
    var Dy = Math.max(...ys) - Math.min(...ys);

    if (Dy > Dx) {
        var ytemp = ys;
        ys = xs;
        xs = ys;

        var Dx = Math.max(...xs) - Math.min(...xs);
        var Dy = Math.max(...ys) - Math.min(...ys);
    }

    var x0 = Math.min(...xs);
    var y0 = Math.min(...ys);

    canvas.height = 700*Dy/Dx;

    console.log(Dx)

    ctx.beginPath();
    ctx.moveTo((0.9*((xs[0]-x0)/Dx)+0.05)*700, (0.9*((ys[0]-y0)/Dy)+0.05)*canvas.height);

    for (var s=1; s < xs.length; s++) {
        ctx.lineTo((0.9*((xs[s]-x0)/Dx)+0.05)*700, (0.9*((ys[s]-y0)/Dy)+0.05)*canvas.height);
    }
    ctx.lineTo((0.9*((xs[0]-x0)/Dx)+0.05)*700, (0.9*((ys[0]-y0)/Dy)+0.05)*canvas.height);
    ctx.closePath();
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo((0.9*((track.gate[0][0]-x0)/Dx)+0.05)*700, (0.9*((track.gate[0][1]-y0)/Dy)+0.05)*canvas.height);
    ctx.lineTo((0.9*((track.gate[1][0]-x0)/Dx)+0.05)*700, (0.9*((track.gate[1][1]-y0)/Dy)+0.05)*canvas.height);
    ctx.closePath();
    ctx.strokeStyle = '#00F';
    ctx.stroke();

    ctx.arc((0.9*((x-x0)/Dx)+0.05)*700, (0.9*((y-y0)/Dy)+0.05)*canvas.height, 4, 0, Math.PI*2);
    ctx.fillStyle = '#F00';
    ctx.fill();
}
