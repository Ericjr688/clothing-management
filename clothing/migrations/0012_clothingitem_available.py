# Generated by Django 5.1.6 on 2025-03-20 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothing', '0011_alter_clothingitem_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='clothingitem',
            name='available',
            field=models.BooleanField(default=True),
        ),
    ]
