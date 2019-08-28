let english = window.location.href.indexOf('/en') !== -1;

document.getElementById('footer-text').innerHTML = (english) ? "FEFU DIGITAL SCHOOL, 2019" : "ШКОЛА ЦИФРОВОЙ ЭКОНОМИКИ ДВФУ, 2019";

document.querySelectorAll('#nav-sberta').forEach(v => v.innerHTML = (english) ? "SBERTA" : "СБЕРТА");
document.querySelectorAll('#nav-recognize').forEach(v => v.innerHTML = (english) ? "RECOGNIZE" : "РАСПОЗНАВАНИЕ");
document.querySelectorAll('#nav-catalog').forEach(v => v.innerHTML = (english) ? "CATALOG" : "КАТАЛОГ");

