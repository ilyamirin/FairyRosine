const video = document.querySelector('video');

navigator.mediaDevices.getUserMedia({video: {width: 640, height: 480}}).then((stream) => video.srcObject = stream);

const getFrame = () => {
    console.log("send frame");
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    canvas.toBlob(function(blob){
        let encoder = new TextEncoder().encode(String(+ new Date()));
        let _blob = new Blob([encoder]);
        let res = new Blob([_blob, blob]);
        socket.send(res);
    }, 'image/jpeg', 0.8);

};
const FPS = 10;

let socketUrl = "ws://" + window.location.host + window.location.pathname;
let socket = new WebSocket(socketUrl);

let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');

socket.onmessage = function (event) {
    context.clearRect(0, 0, canvas.width, canvas.height);
    let rects = JSON.parse(event.data).text;

    rects.forEach(rect => {
        context.beginPath();
        context.rect(rect[1], rect[0], rect[3] - rect[1], rect[2] - rect[0]);
        context.strokeStyle = 'green';
        context.lineWidth = "3";
        context.stroke();
        context.closePath();

        context.beginPath();
        context.fillStyle = 'green';
        context.fillRect(rect[1] - 2, rect[0] + rect[2] - rect[0], Math.max(rect[3] - rect[1] + 4, rect[4].length * 9 + 4), 20);
        context.closePath();

        context.beginPath();
        context.font = "16px Arial";
        context.fillStyle = 'white';
        context.fillText(rect[4], rect[1] + 2, rect[2] - rect[0] + rect[0] + 15);
        context.closePath();
    });
};

socket.onopen = function (event) {
    console.log('socket opened');
    console.log(event);
    setInterval(() => getFrame(), 1000 / FPS);
};

socket.onclose = function (event) {
    console.log('socket closed');
    console.log(event);
};

socket.onerror = function (event) {
    console.log('socket errors');
    console.log(event);
};