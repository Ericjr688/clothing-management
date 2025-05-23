# Generated by Django 5.1.6 on 2025-04-11 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothing', '0025_rename_favorites_clothingitem_likes'),
        ('users', '0004_librarianupgraderequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clothingitem',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='favorites', to='users.userprofile'),
        ),
    ]
