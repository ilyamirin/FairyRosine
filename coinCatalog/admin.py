from django.contrib import admin

from .models import Category
from .models import Coin
from .models import ImgCoin

admin.site.register(Category)
admin.site.register(Coin)
admin.site.register(ImgCoin)