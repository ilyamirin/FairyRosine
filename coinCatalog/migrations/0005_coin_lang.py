# Generated by Django 2.2.4 on 2019-08-27 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinCatalog', '0004_dialoguser'),
    ]

    operations = [
        migrations.AddField(
            model_name='coin',
            name='lang',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
