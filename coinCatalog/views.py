from django.shortcuts import render
from .models import Category
from .models import Coin
from .models import ImgCoin

import json
from django.forms.models import model_to_dict
from django.http import HttpResponse

def index(req):
  categories = Category.objects.all()

  cats = {
    "categories": categories,
  }

  return render(req, 'coinCatalog/index.html', cats)

def category(req, id=-1):
  coins = Coin.objects.filter(category=id)

  res = coins.values()

  for i in res:
    i['img'] = ImgCoin.objects.get(coin=i['id']).href

  coins = {
    "coins": res,
  }

  return render(req, 'coinCatalog/category.html', coins)

def stream(req):
  return render(req, 'coinCatalog/stream.html')

def dialog(req):
  return render(req, 'coinCatalog/dialog.html')

def coin(req, id=-1):
  coin = Coin.objects.get(id=id)
  imgs = ImgCoin.objects.filter(coin=id)

  coin = {
    "coin": coin,
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