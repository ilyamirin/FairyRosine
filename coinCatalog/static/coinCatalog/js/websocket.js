const video = document.querySelector('video');

navigator.mediaDevices.getUserMedia({video: {width: 640, height: 480}})
    .then(stream => {
        video.srcObject = stream;
        startWebSocketInteraction();
    })
    .catch(e => {
        alert("Не удалось получить доступ к видео. Подключите камеру и обновите страницу");
        console.log(e);
    });

function startWebSocketInteraction(){
    let timeShift = 0;

    const getFrame = () => {
        console.log("send frame");
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);

        canvas.toBlob(function(blob){
            let encoder = new TextEncoder().encode(String(+ new Date() - timeShift));
            let _blob = new Blob([encoder]);
            let res = new Blob([_blob, blob]);
            socket.send(res);
        }, 'image/jpeg', 0.8);

    };
    const FPS = 3;

    let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    let socketUrl = ws_scheme + "://" + window.location.host + window.location.pathname.slice(0, -1) + "1/";
    let socket = new WebSocket(socketUrl);

    socket.onmessage = function (event) {
        let data = JSON.parse(event.data);
        if (data.type === 'sync_clock') {
            let serverNow = Math.round(data.timestamp * 1000);
            timeShift = + new Date() - serverNow;
            console.log('sync clock, shift = ' + timeShift/1000 + ' seconds');
            return;
        }
        if (data.type == 'recognized_coins'){
            drawCoins(data.text);
        }
        canvasData[data.type] = data.text;
    };

    socket.onopen = function (event) {
        console.log('socket opened');
        frameLoop = setInterval(() => getFrame(), 1000 / FPS);
    };

    socket.onclose = function (event) {
        console.log('socket closed');
        if (frameLoop)
            clearInterval(frameLoop);
        alert("Соединение было разорвано!");
    };

    socket.onerror = function (event) {
        console.log('socket errors');
        if (frameLoop)
            clearInterval(frameLoop);
        alert("Сокет вернул ошибку!");
    };
}