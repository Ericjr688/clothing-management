# Generated by Django 5.1.6 on 2025-04-07 21:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothing', '0016_review'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clothingitem',
            name='likes',
        ),
        migrations.AddField(
            model_name='clothingitem',
            name='favorited_by',
            field=models.ManyToManyField(blank=True, related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
    ]
