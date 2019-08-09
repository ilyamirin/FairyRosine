from django.shortcuts import render
from .models import Category
from .models import Coin

def index(req):
  categories = Category.objects.all()

  cats = {
    "categories": categories,
  }

  return render(req, 'coinCatalog/index.html', cats)

def category(req, id = -1):
  coins = Coin.objects.get(category = id)

  return render(req, 'coinCatalog/category.html')

def stream(req):
  return render(req, 'coinCatalog/stream.html')