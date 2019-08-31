import os
import django
import json
import html

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vef.settings")
django.setup()

from vef.settings import BASE_DIR
from coinCatalog.models import Coin
from coinCatalog.models import Category
from coinCatalog.models import CoinDescription
from coinCatalog.models import ImgCoin


def import_catalog(catalog):
    for coin in catalog:
        catalog_id = html.unescape(coin["id"])
        name = html.unescape(coin["name"])
        short_name = html.unescape(coin["short_name"])
        description = html.unescape(coin["description"])
        lang = html.unescape(coin["lang"])
        nominal = html.unescape(coin["nominal"])
        quality = html.unescape(coin["quality"])
        probe = html.unescape(coin["probe"])
        original_equipment = html.unescape(coin["original_equipment"])
        manufacturer = html.unescape(coin["manufacturer"])
        mass = html.unescape(coin["mass"])
        pure_metal = html.unescape(coin["pure_metal"])
        diameter = html.unescape(coin["diameter"])
        thickness = html.unescape(coin["thickness"])
        copies = html.unescape(coin["copies"])
        imgs = coin["imgs"]
        try:
            coin_db = Coin.objects.get(
                catalog_id=catalog_id
            )
        except:
            coin_db = Coin(
                catalog_id=catalog_id
            )
            coin_db.save()
        coin_descr = CoinDescription(
            coin_id=coin_db,
            lang=lang,
            name=name,
            short_name=short_name,
            nominal=nominal,
            quality=quality,
            probe=probe,
            original_equipment=original_equipment,
            pure_metal=pure_metal,
            mass=mass,
            diameter=diameter,
            thickness=thickness,
            copies=copies,
            manufacturer=manufacturer,
            description=description,
        )
        coin_descr.save()
        for img in imgs:
            try:
                ImgCoin.objects.get(coin_id=coin_db)
            except:
                img_coin = ImgCoin(
                    coin_id=coin_db,
                    href=html.unescape(img),
                )
                img_coin.save()


for catalog_name in "catalog_eng.json", "catalog_rus.json":
    catalog = json.loads(open(os.path.join(BASE_DIR, catalog_name), "r").read())
    import_catalog(catalog)
