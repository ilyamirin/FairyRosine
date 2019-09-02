let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');

let frameLoop = null;
let firstWhite = false;

let canvasData = {
    "face": [],
    "coin": [],
};

function drawRect(rect, text, colorStroke, fillStyle){
    context.beginPath();
    context.rect(rect[1], rect[0], rect[3] - rect[1], rect[2] - rect[0]);
    context.strokeStyle = colorStroke;
    context.lineWidth = "3";
    context.stroke();
    context.closePath();

    context.beginPath();
    context.fillStyle = fillStyle;
    context.fillRect(rect[1] - 2, rect[0] + rect[2] - rect[0], Math.max(rect[3] - rect[1] + 4, text.length * 9 + 4), 20);
    context.closePath();

    context.beginPath();
    context.font = "16px Arial";
    context.fillStyle = 'white';
    context.fillText(text, rect[1] + 2, rect[2] - rect[0] + rect[0] + 15);
    context.closePath();
}

function drawCanvasData() {
    let userColor = 'blue';
    context.clearRect(0, 0, canvas.width, canvas.height);
    canvasData["face"].forEach((rect, i) =>
        drawRect(rect, rect[4],
            (!i && firstWhite) ? userColor: 'green', (!i && firstWhite) ? userColor : 'green'));
    canvasData["coin"].forEach(d => drawRect(d.coords, d.short_name, 'blue', 'blue'));
}

drawInterval = setInterval(() => drawCanvasData(), 1000 / 24);

function resetCanvas() {
    clearInterval(drawInterval);
    context.clearRect(0, 0, canvas.width, canvas.height);
}

function activateCanvas() {
    drawInterval = setInterval(() => drawCanvasData(), 1000 / 24);
}