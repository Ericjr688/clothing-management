from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('librarian', 'Librarian'),
        ('patron', 'Patron'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    google_id = models.CharField(max_length=50, unique=True)
    profile_picture = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    @property
    def has_pending_upgrade_request(self):
        return self.librarian_upgrade_requests.filter(status="pending").exists()

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    def average_rating(self):
        ratings = self.user.ratings_received.all()
        return round(sum(r.rating for r in ratings) / len(ratings), 2) if ratings else None    
    
class Rating(models.Model):
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings_received")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings_given")
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} rated {self.rated_user.username}: {self.rating}"
    

# Holds data for a promotion request
class LibrarianUpgradeRequest(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied')
    ]
    requester = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='librarian_upgrade_requests'
    )
    status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.user.username} upgrade request ({self.status})"
