# Generated by Django 2.2.3 on 2019-07-31 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinCatalog', '0002_auto_20190731_0732'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='href',
            field=models.CharField(default='invest_coins.jpg', max_length=255),
        ),
    ]
