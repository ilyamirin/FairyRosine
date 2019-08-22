let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');

let frameLoop = null;

let canvasData = {
    "face": [],
    "coin": [],
}

function drawRect(rect, colorStroke, fillStyle){
    context.beginPath();
    context.rect(rect[1], rect[0], rect[3] - rect[1], rect[2] - rect[0]);
    context.strokeStyle = colorStroke;
    context.lineWidth = "3";
    context.stroke();
    context.closePath();

    context.beginPath();
    context.fillStyle = fillStyle;
    context.fillRect(rect[1] - 2, rect[0] + rect[2] - rect[0], Math.max(rect[3] - rect[1] + 4, rect[4].length * 9 + 4), 20);
    context.closePath();

    context.beginPath();
    context.font = "16px Arial";
    context.fillStyle = 'white';
    context.fillText(rect[4], rect[1] + 2, rect[2] - rect[0] + rect[0] + 15);
    context.closePath();
}

function drawCanvasData() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    canvasData["face"].forEach(rect => drawRect(rect, 'green', 'green'));
    canvasData["coin"].forEach(rect => drawRect(rect, 'blue', 'blue'));
}

drawInterval = setInterval(() => drawCanvasData(), 1000 / 24);