function getCoinFromServer(id) {
    let coinPlace = document.getElementById('modal-coin-body');
    $.ajax({
        type: 'GET',
        url: location.protocol + "//" + location.host + "/getCoin",
        data: 'id=' + id,
        success: function(data){
            let res = JSON.parse(data);
            let coin = res['coin'];
            console.log(coin['name']);
            $("#modal-coin-body-name").html(coin['name']);
            $("#modal-coin-body-manufacturer").html(coin['manufacturer']);
            $("#modal-coin-body-copies").html(coin['copies']);
            $("#modal-coin-body-description").html(coin['description']);
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