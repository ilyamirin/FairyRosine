from django.contrib import admin

from .models import Category
from .models import Coin
from .models import ImgCoin
from .models import DialogUser
from .models import CoinDescription

admin.site.register(Category)
admin.site.register(Coin)
admin.site.register(ImgCoin)
admin.site.register(DialogUser)
admin.site.register(CoinDescription)