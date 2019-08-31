from django.shortcuts import render
from .models import Category
from .models import Coin
from .models import ImgCoin
from .models import CoinDescription

import json
from django.forms.models import model_to_dict
from django.http import HttpResponse

def get_lang(req):
  lang = 'ru'
  if req.session.get('lang') is None:
    req.session['lang'] = lang
  else:
    lang = req.session.get('lang')

  print('____________________' + lang)
  return lang

def index(req):
  # categories = Category.objects.filter(lang=lang)
  #
  # cats = {
  #   "categories": categories,
  # }

  return render(req, 'coinCatalog/index.html', {})

def category(req, id=-1):
  coins = Coin.objects.all()

  res = coins.values()

  for i in res:
    imgs = ImgCoin.objects.filter(coin_id=i['id']).values()[0]
    print(i['id'])
    print(get_lang(req))
    desc = CoinDescription.objects.get(coin_id=i['id'], lang=get_lang(req))
    i['img'] = imgs['href']
    i['desc'] = desc

  coins = {
    "coins": res,
  }

  return render(req, 'coinCatalog/category.html', coins)

def stream(req):
  lang = get_lang(req)
  res = render(req, 'coinCatalog/stream.html', {
    "lang": lang,
  })
  res['Feature-Policy'] = "fullscreen *"
  return res

def dialog(req):
  return render(req, 'coinCatalog/dialog.html')

def coin(req, id=-1):
  # coin = Coin.objects.get(id=id)
  desc = CoinDescription.objects.get(coin_id=id, lang=get_lang(req))
  imgs = ImgCoin.objects.filter(coin_id=id)

  coin = {
    "coin": desc,
    "imgs": imgs
  }

  return render(req, 'coinCatalog/coin.html', coin)

def production(req):
  return render(req, 'coinCatalog/production.html')

def get_coin(req, id=1):
  coin = model_to_dict(Coin.objects.get(id=id))

  imgs = ImgCoin.objects.filter(coin=id).values()
  imgs = [img for img in imgs]

  res = {
    "coin": coin,
    "imgs": imgs,
  }

  return HttpResponse(json.dumps(res))

def change_lang(req, lang):
  req.session['lang'] = lang
  print("ses")
  print(get_lang(req))
  print("ses")
  return HttpResponse(json.dumps({'lang': get_lang(req)}))