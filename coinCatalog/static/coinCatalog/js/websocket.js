const video = document.querySelector('video');

navigator.mediaDevices.getUserMedia({video: {width: 640, height: 480}}).then((stream) => video.srcObject = stream);

const getFrame = () => {
    console.log("send frame");
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    let b = + new Date();
    let uint8 = new Uint8Array(8);


    canvas.toBlob(function(blob){
        let encoder = new TextEncoder().encode(String(+ new Date()));
        let _blob = new Blob([encoder]);
        let res = new Blob([_blob, blob]);
        socket.send(res);
    }, 'image/png', 1);

};
const FPS = 4;

let socketUrl = "ws://" + window.location.host + window.location.pathname;
let socket = new WebSocket(socketUrl);

let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');

socket.onmessage = function (event) {
    context.clearRect(0, 0, canvas.width, canvas.height);
    let rects = JSON.parse(JSON.parse(event.data).text);

    rects.forEach(rect => {
        context.beginPath();
        context.rect(rect[1], rect[0], rect[3] - rect[1], rect[2] - rect[0]);
        context.strokeStyle = 'blue';
        context.lineWidth = "3";
        context.stroke();
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