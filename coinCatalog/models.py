from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=60)
    href = models.CharField(max_length=255, default='invest_coins.jpg')

    def __str__(self):
        return self.name

class Coin(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
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
    notes = models.TextField(null=True)
    description = models.TextField(null=True)
    
    def __str__(self):
        return self.name

class ImgCoin(models.Model):
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    href = models.CharField(max_length=255)

    def __str__(self):
        return self.coin.name + " " + self.href