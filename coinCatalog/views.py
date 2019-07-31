from django.shortcuts import render
from .models import Category

def index(req):

  categories = Category.objects.all()

  cats = {
    "categories": categories,
  }

  return render(req, 'coinCatalog/index.html', cats)