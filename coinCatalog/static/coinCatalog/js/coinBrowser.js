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
            $("#modal-coin-body-name").html(coin['name']);
            $("#modal-coin-body-manufacturer").html(coin['manufacturer']);
            $("#modal-coin-body-copies").html(coin['copies']);
            $("#modal-coin-body-description").html(coin['description']);

            res['imgs'].forEach(v => {
                let img = document.createElement('img');
                img.src = location.protocol + "//" + location.host + '/static/coinCatalog/coins/' + v['href'];
                img.style.width = "100%";
                let col = document.createElement('div');
                col.classList.add('col-md-3');
                col.appendChild(img);
                modalImgs.appendChild(col);
            });
        }
    });
}

function clickCoin(obj) {
    //getCoinFromServer(1);
     $.ajax({
        type: 'GET',
        url: location.protocol + "//" + location.host + "/coin/" + obj.id,
        success: function(data){
            document.getElementById('coinModal2').innerHTML = data;
        }
    });
    document.getElementById('modal-coin-title').innerHTML = obj.short_name;
}

let coinBlocks = {};
let activeBlocks = [];

function makeCoinBlock(obj) {
    let a = document.createElement("a");
    //a.href = location.protocol + "//" + location.host + "/coin/" + obj['id'];
    a.setAttribute('style', 'color: ' + (obj.featured ? 'black' : 'blue') + '; text-decoration: none;');

    let wrapper = document.createElement('div');
    wrapper.classList.add("col-md-3");
    wrapper.setAttribute('style', 'padding: 10px;');
    wrapper.setAttribute('data-toggle', 'modal');
    wrapper.setAttribute('data-target', '#coinModal1');
    wrapper.setAttribute('modal-title', obj['short_name']);
    wrapper.addEventListener("click", () => clickCoin(obj));

    let div = document.createElement('div');
    div.setAttribute('style', 'background-color: white; border-radius: 8px; padding: 6px; text-align: center;');

    let img = document.createElement('img');
    img.src = location.protocol + "//" + location.host + '/static/coinCatalog/coins/' + obj['href'];
    img.setAttribute('style', 'max-width: 100%; max-height: 100px; background-color: #ccc; margin-top: 10px;');
    div.appendChild(img);

    let txt = document.createElement('p');
    txt.setAttribute('style', 'font-size: 18px;');
    let index = obj['short_name'].indexOf('(');
    txt.innerText = (index + 1) ? obj['short_name'].slice(0, index) : obj['short_name'];
    // txt.innerText = name.replace(/_/g, ' ').replace(/avers/g, ' ').replace(/reverse/g, ' ');
    div.appendChild(txt);

    a.appendChild(div);
    wrapper.appendChild(a);

    return wrapper;
}

function makeEmptyBlock() {
    let wrapper = document.createElement('div');
    wrapper.classList.add("col-md-3");
    return wrapper;
}

let emptyBlock = makeEmptyBlock();
let row = document.getElementById('rec-coins');
row.appendChild(makeEmptyBlock());
row.appendChild(makeEmptyBlock());
row.appendChild(makeEmptyBlock());
row.appendChild(makeEmptyBlock());

function drawCoins(coins){
    let cnt = 4;
    coins = coins.slice(0, cnt);
    //console.log("begin");
    //console.log(row.childNodes.length);
    let remove = activeBlocks.filter(v => coins.map(k => k['short_name']).indexOf(v['short_name']) === -1);
    remove.forEach(v => row.replaceChild(makeEmptyBlock(), coinBlocks[v['short_name']]));
    activeBlocks = activeBlocks.filter(v => coins.map(k => k['short_name']).indexOf(v['short_name']) !== -1);
    //console.log("active after clearing");
    //console.log(activeBlocks);
    let addBlocks = coins.filter(v => activeBlocks.map(k => k['short_name']).indexOf(v['short_name']) === -1);

    //console.log('before add');
    //console.log(addBlocks);

    addBlocks.forEach(v => {
        if (!coinBlocks[v['short_name']]){
            coinBlocks[v['short_name']] = makeCoinBlock(v);
        }
        let flagExists = false;
        let flagEmptyBlock = false;
        for (let i = 0; i < row.childNodes.length; i++) {
            if (row.childNodes[i].innerHTML === coinBlocks[v['short_name']].innerHTML) {
                flagExists = true;
            }
        }
        if (!flagExists) {
            for (let i = 0; i < row.childNodes.length; i++) {
                if (row.childNodes[i].innerHTML === emptyBlock.innerHTML) {
                    flagEmptyBlock = true;
                    row.replaceChild(coinBlocks[v['short_name']], row.childNodes[i]);
                    break;
                }
            }
        }
        if (!flagExists && !flagEmptyBlock) {
            row.appendChild(coinBlocks[v['short_name']]);
        }
    });

    //console.log(row.childNodes.length);
    //console.log(row);
    //console.log("end");
    activeBlocks.push(...addBlocks);
}