# Generated by Django 3.2.5 on 2021-08-01 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='imdb',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
