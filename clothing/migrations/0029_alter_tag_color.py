# Generated by Django 5.1.6 on 2025-04-28 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothing', '0028_clothingitemimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(blank=True, choices=[('Red', 'Red'), ('Orange', 'Orange'), ('Yellow', 'Yellow'), ('Green', 'Green'), ('Blue', 'Blue'), ('Purple', 'Purple'), ('Pink', 'Pink'), ('White', 'White'), ('Black', 'Black'), ('Grey', 'Grey')], max_length=50, null=True),
        ),
    ]
