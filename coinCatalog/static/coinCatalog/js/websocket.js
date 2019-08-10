const video = document.querySelector('video');

navigator.mediaDevices.getUserMedia({video: {width: 600, height: 600}}).then((stream) => video.srcObject = stream);

const getFrame = () => {
    console.log("send frame");
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    return JSON.stringify({
        img: canvas.toDataURL('image/png'),
        timestamp: + new Date(),
    });

};
const FPS = 5;

let socketUrl = "ws://" + window.location.host + window.location.pathname;
let socket = new WebSocket(socketUrl);

socket.onmessage = function (event) {
    console.log(event);
};

socket.onopen = function (event) {
    console.log('socket opened');
    console.log(event);
    setInterval(() => socket.send(getFrame()), 1000 / FPS);
};

socket.onclose = function (event) {
    console.log('socket closed');
    console.log(event);
};

socket.onerror = function (event) {
    console.log('socket errors');
    console.log(event);
};