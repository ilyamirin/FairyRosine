let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');

let frameLoop = null;
let firstWhite = false;

let canvasData = {
    "face": [],
    "coin": [],
};

function drawRect(rect, text, colorStroke, fillStyle){
    if ((rect[3] - rect[1]) * (rect[2] - rect[0]) > 900 * 675 / 3){
    // это на случай криво найденных рамок (горизонтальная полоса на весь экран)
//        return;
    }

    // этот if для того, чтобы на ipad рамки не залезали на карусель монет
//    if (rect[2] > 400) rect[2] = 400;
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
    canvasData["coin"].forEach(d => !d.featured ? drawRect(d.coords, d.short_name, 'blue', 'blue') : null);
}

drawInterval = setInterval(() => drawCanvasData(), 1000 / 24);

function resetCanvas() {
    clearInterval(drawInterval);
    context.clearRect(0, 0, canvas.width, canvas.height);
}

function activateCanvas() {
    drawInterval = setInterval(() => drawCanvasData(), 1000 / 24);
}

let coins = null;

function canvas_updateCoins(coins_){
    coins = coins_;
}

function canvas_registerOnSquareClick(cb) {
    canvas.addEventListener('click', (e) => {
        if (!coins) {
            return;
        }
        const pos = {
            x: e.clientX,
            y: e.clientY
        };
        for (let coin of coins) {
            if (pos.y >= Math.min(coin.coords[0], coin.coords[2]) &&
                pos.y <= Math.max(coin.coords[0], coin.coords[2]) &&
                pos.x >= Math.min(coin.coords[1], coin.coords[3]) &&
                pos.x >= Math.min(coin.coords[1], coin.coords[3])
            ) {
                cb(coin);
                break;
            }
        }
    });
}
