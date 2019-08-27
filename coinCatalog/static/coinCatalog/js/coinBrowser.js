function getCoinFromServer(id) {
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
    document.getElementById('modal-coin-title').innerHTML = this.getAttribute('modal-title');
}

function drawCoins(coins){
    let row = document.getElementById('rec-coins');
    row.innerHTML = "";
    coins.slice(0, 4).forEach(v => {
        let wrapper = document.createElement('div');
        wrapper.classList.add("col-md-3");
        wrapper.setAttribute('style', 'padding: 10px;');
        wrapper.setAttribute('data-toggle', 'modal');
        wrapper.setAttribute('data-target', '#coinModal');
        wrapper.setAttribute('modal-title', v[0]);
        wrapper.addEventListener("click", clickCoin);

        let div = document.createElement('div');
        div.setAttribute('style', 'background-color: white; border-radius: 8px; padding: 6px;');

        let img = document.createElement('div');
        img.setAttribute('style', 'width: 100%; height: 150px; background-color: #ccc; margin-top: 10px;');
        div.appendChild(img);

        let txt = document.createElement('p');
        txt.innerHTML = v[0];
        div.appendChild(txt);

        wrapper.appendChild(div);

        row.appendChild(wrapper);
    });
}