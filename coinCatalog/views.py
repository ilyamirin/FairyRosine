from django.shortcuts import render

def index(req):
  return render(req, 'coinCatalog/index.html')