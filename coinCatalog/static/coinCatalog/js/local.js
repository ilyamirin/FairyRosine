// let _video =
// document.getElementById('video').hasAttribute('data-eng') ? null : document.getElementById('languages').setAttribute('style', 'display: none;');
let english = document.getElementsByTagName("body")[0].getAttribute("data-lang") === 'en';

document.getElementById('footer-text').innerHTML = (english) ? "SBERBANK & FEFU Digital School, 2019" : "СБЕРБАНК и Школа Цифровой Экономики ДВФУ, 2019";

document.querySelectorAll('#nav-sberta').forEach(v => v.innerHTML = (english) ? "SBERTA" : "СБЕРТА");
document.querySelectorAll('#nav-recognize').forEach(v => v.innerHTML = (english) ? "RECOGNIZE" : "РАСПОЗНАВАНИЕ");
document.querySelectorAll('#nav-catalog').forEach(v => v.innerHTML = (english) ? "CATALOG" : "КАТАЛОГ");

document.getElementById("langRu").onclick = function() {
    $.ajax({
        type: 'GET',
        url: location.protocol + "//" + location.host + "/changeLang/ru",
        success: function(data){
            data = JSON.parse(data);
            if (data['lang'] === 'ru'){
                document.location.reload(false);
            }
        }
    });
};
document.getElementById("langEn").onclick = function() {
    $.ajax({
        type: 'GET',
        url: location.protocol + "//" + location.host + "/changeLang/en",
        success: function(data){
            data = JSON.parse(data);
            if (data['lang'] === 'en'){
                document.location.reload(false);
            }
        },
        error: function(data){
            console.log(data);
        }
    });

};