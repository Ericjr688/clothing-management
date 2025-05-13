from django.db import models
from django.utils import timezone
from users.models import UserProfile
from clothing.models import ClothingItem

BORROW_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('denied', 'Denied'),
    ('returned', 'Returned'),
]

class BorrowRequest(models.Model):
    borrower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='borrow_requests')
    approver = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests'
    )
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE, related_name='borrow_requests')
    status = models.CharField(max_length=10, choices=BORROW_STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    return_email_sent = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.borrower.user.username} requests {self.clothing_item.name} ({self.status})"
