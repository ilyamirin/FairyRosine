let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
let socketUrl = ws_scheme + "://" + window.location.host + window.location.pathname;
let socket = new WebSocket(socketUrl);
var button = document.getElementById("send");
var history1 = document.getElementById("history");
var micBtn = document.getElementById("mic_btn");
var input = document.getElementById("question");
let body = document.getElementsByTagName("body")[0];
var rec = null;
var isRecording = false;
let micBtnStyle = document.getElementById('mic_btn_style');
let pushVoice = document.getElementById('pushVoice');
let timeShift = 0;
let FPS = 1;
let imgCompressionLvl = 0.8;
const video = document.querySelector('video');

let message_history = [];

navigator.mediaDevices.getUserMedia({
    audio: true
}).then(stream => {
    const aCtx = new AudioContext();
    const streamSource = aCtx.createMediaStreamSource(stream);
    rec = new Recorder(streamSource);
});

navigator.mediaDevices.getUserMedia({video: {width: 640, height: 480}})
.then(stream => {
    video.srcObject = stream;
    frameLoop = setInterval(() => getFrame(), 1000 / FPS);
})
.catch(e => {
    console.log("Не удалось получить доступ к видео. Подключите камеру и обновите страницу");
    console.log(e);
});

let micMouseDown = function() {
    isRecording = true;
    micBtnStyle.classList.remove("attach_btn");
    micBtnStyle.classList.remove("attach_btn2");
    micBtnStyle.classList.add("attach_btn2");
    pushVoice.style.display = 'block';
    rec.clear();
    rec.record();
}

let micMouseUp = function() {
    if (isRecording){
        isRecording = false;
        micBtnStyle.classList.remove("attach_btn");
        micBtnStyle.classList.remove("attach_btn2");
        micBtnStyle.classList.add("attach_btn");
        pushVoice.style.display = 'none';
        rec.stop()
        rec.exportWAV((blob) => {
            socket.send(blob);
        });
    }
}

micBtn.addEventListener("mousedown", micMouseDown);
micBtn.addEventListener("touchstart", micMouseDown);
body.addEventListener("mouseup", micMouseUp);
body.addEventListener("touchend", micMouseUp);

let avatars = [];
let currentAvatar = null;
let currentName = "";

function renderChat(){
    let parent = document.getElementById('parentChat');
    parent.innerHTML = "";

    let rand = Math.floor(Math.random() * (147 - 133 + 1) + 133);
    avatars.push(location.protocol + "//" + location.host + '/static/CoinCatalog/faces/Known ' + rand + '.png');
    message_history.forEach((v, i) => {
        if (v[0] == "user") {
            let part1 = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="' + (v[2] == null ? avatars[i] : ("data:image/png;base64," + v[2])) + '" class="rounded-circle user_img_msg"></div>';
//            let part15 = '<div class="msg_cotainer">';
            let part2 = '<div class="msg_cotainer"><div id="user_name_msg">' + v[3] + '</div>';
            let part3 = '</div></div>';
            parent.innerHTML += part1 + part2 + v[1] + part3;
        }
        else {
            let part1 = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">';
            let part2 = '</div><div class="img_cont_msg"><img src="data:image/png;base64,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"class="rounded-circle user_img_msg">';
            let part3 = '</div></div>';
            parent.innerHTML += part1 + v[1] + part2 + part3;
        }
    });
    parent.scrollTop = parent.scrollHeight;
}

function sendAnswer() {
    let input = document.getElementById("question").value;
    document.getElementById("question").value = "";
    if (!input.length)
        return;

    renderChat(message_history.push(["user", input, currentAvatar, currentName]));
    socket.send(input);
}

var previousRect = null;

function highLight(topic) {
    if (previousRect != null) {
        previousRect.setAttribute("fill", "none");
    }

    //get current topic's rectangle, color it
    let currentRect = document.getElementById(topic).getElementsByTagName("polygon")[0];
    currentRect.setAttribute("fill", "#00AC00");
    previousRect = currentRect;

    //get position, scroll iframe to current topic's rectangle
    let textObj = document.getElementById(topic).getElementsByTagName("text")[0]
    let x = textObj.getAttribute("x");
    let y = textObj.getAttribute("y");
    let xOffset = document.getElementById("graph_frame").clientWidth / 2
    let yOffset = document.getElementById("graph_frame").clientHeight / 2
    console.log(x, y);
    document.getElementById("graph_frame").scrollTo({
        left: 1 * x + 4 - xOffset,
        top: 1 * y + 423 - yOffset,
        behavior: "smooth"
    });
    console.log(1 * x + 4, 1 * y + 423)
}

button.addEventListener("click", sendAnswer);

input.onkeypress = function (event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendAnswer();
    }
};

socket.onmessage = function (event) {
    let data = JSON.parse(event.data);
    console.log(data);
    if (data.type == 'dialog_answer_ready') {
        try {
            highLight(data.topic);
        }
        catch {

        }
    }
    if (data.type === 'recognized_speech_ready') {
        renderChat(message_history.push(["user", data.text, currentAvatar, currentName]));
        return;
    }
    if (data.type === 'sync_clock') {
        let serverNow = Math.round(data.timestamp * 1000);
        timeShift = + new Date() - serverNow;
        console.log('sync clock, shift = ' + timeShift/1000 + ' seconds');
        return;
    }
    if (data.type === 'faces_ready') {
        currentAvatar = data.dialog_photo;
        currentName = data.display_name;
        console.log('avatar updated');
        document.getElementById('user_name').innerHTML = currentName;
        return;
    }
    setTimeout(() => renderChat(message_history.push(["bot", data.text])), 500);
};

socket.onopen = function (event) {
    console.log('socket opened');
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

function getFrame() {
    console.log("send frame");
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    canvas.toBlob(function(blob){
        let encoder = new TextEncoder().encode(String(+ new Date() - timeShift));
        let _blob = new Blob([encoder]);
        let res = new Blob([_blob, blob]);
        try {
            socket.send(res);
        }
        catch {
            console.log("error sending frame");
        }
    }, 'image/jpeg', imgCompressionLvl);
};
