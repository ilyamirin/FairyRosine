from django.db import models


class Category(models.Model):
    lang = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=60, null=True)
    href = models.CharField(max_length=255, default='invest_coins.jpg')

    def __str__(self):
        return self.name


class Coin(models.Model):
    catalog_id = models.CharField(max_length=255, null=True, db_index=True)

    def __str__(self):
        return self.catalog_id


class CoinDescription(models.Model):
    coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE)
    lang = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True, default="")
    short_name = models.CharField(max_length=150, null=True)
    nominal = models.CharField(max_length=150, null=True)
    quality = models.CharField(max_length=50, null=True)
    probe = models.CharField(max_length=50, null=True)
    original_equipment = models.CharField(max_length=255, null=True)
    pure_metal = models.CharField(max_length=255, null=True)
    mass = models.CharField(max_length=50, null=True)
    diameter = models.CharField(max_length=50, null=True)
    thickness = models.CharField(max_length=50, null=True)
    copies = models.CharField(max_length=50, null=True)
    manufacturer = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class ImgCoin(models.Model):
    coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE)
    href = models.CharField(max_length=255)


class DialogUser(models.Model):
    uid = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=True)
    time_enrolled = models.DateTimeField(null=True)
    photo = models.BinaryField(null=True)
    vector = models.BinaryField(null=True)
