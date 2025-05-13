from django.db import models

class ClothingItem(models.Model):
        
    STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('in_repair', 'In Repair')
    ]
        
    title = models.CharField(max_length=100)
    id = models.CharField(max_length=100, unique=True, primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='checked_in')
    location = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    availability_date = models.DateField()
