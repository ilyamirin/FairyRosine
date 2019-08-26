function getCoinFromServer(id) {
    let coinPlace = document.getElementById('modal-coin-body');
    $.ajax({
        type: 'GET',
        url: location.protocol + "//" + location.host + "/getCoin",
        data: 'id=' + id,
        success: function(data){
            let modalImgs = document.getElementById('modal-imgs');
            modalImgs.innerHTML = "";
            let res = JSON.parse(data);
            let coin = res['coin'];
            console.log(coin['name']);
            $("#modal-coin-body-name").html(coin['name']);
            $("#modal-coin-body-manufacturer").html(coin['manufacturer']);
            $("#modal-coin-body-copies").html(coin['copies']);
            $("#modal-coin-body-description").html(coin['description']);

            res['imgs'].forEach(v => {
                let img = document.createElement('img');
                img.src = location.protocol + "//" + location.host + '/static/coinCatalog/' + v['href'];
                img.style.width = "100%";
                let col = document.createElement('div');
                col.classList.add('col-md-3');
                col.appendChild(img);
                modalImgs.appendChild(col);
            });
        }
    });
}

function clickCoin(event) {
    getCoinFromServer(1);
    let title = event.target.getAttribute('modal-title');
    document.getElementById('modal-coin-title').innerHTML = title;
}

function drawCoins(coins){
    let ul = document.getElementById('rec-coins');
    ul.innerHTML = "";
    coins.forEach(v => {
        let li = document.createElement('li');
        li.classList.add("list-group-item");
        li.classList.add("list-group-item-action");
        li.setAttribute('data-toggle', 'modal');
        li.setAttribute('data-target', '#coinModal');
        li.setAttribute('modal-title', v[0]);
        li.innerHTML = v[0];
        li.onclick = clickCoin;
        ul.appendChild(li);
    });
}