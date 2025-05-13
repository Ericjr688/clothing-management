from django.db import models
from django.core.exceptions import ValidationError
from users.models import UserProfile
from clothing.models import ClothingItem


# Create your models here.
VISIBILITY_CHOICES = [
    ('public', 'Public'),
    ('private', 'Private')
]

REQUEST_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('denied', 'Denied')
]

class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='created_collections')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    allowed_users = models.ManyToManyField(UserProfile, related_name='shared_collections', blank=True)
    items = models.ManyToManyField(ClothingItem, related_name='item_collections', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_collection_viewable_by(self, user):
        # anonymous users can only view public collections
        if not user.is_authenticated:
            return self.visibility == 'public'
        # librarians and patrons can view all collections
        return True

    def can_modify_collection(self, user):
        if not user.is_authenticated:
            return False
        role = user.userprofile.role
        # librarians can modify all collections
        if role == 'librarian':
            return True
        # patrons can modify their own collections
        elif role == 'patron':
            return user.userprofile == self.owner and self.visibility == 'public'
        
    def can_access_directly(self, user):
       # public collections can be accessed by anyone
        if self.visibility == 'public':
            return True
        # librarians can access all collections
        if user.is_authenticated and user.userprofile.role == 'librarian':
            return True
        # private collections can only be accessed by the owner and users who have been granted access
        if not user.is_authenticated:
            return False
        profile = user.userprofile
        return profile == self.owner or self.allowed_users.filter(pk=profile.pk).exists()

    def has_pending_request(self, user):
        if not user.is_authenticated:
            return False
        profile = user.userprofile
        return self.access_requests.filter(requester=profile, status='pending').exists()


    def clean(self):
        if self.owner_id and self.owner.role == 'patron' and self.visibility == 'private':
            raise ValidationError("Patrons cannot create private collections.")

        
    def __str__(self):
        return self.title
    
class CollectionAccessRequest(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.user.username} requests access to {self.collection.title} ({self.status})"

# TODO: 
# Modify current search features so collections show up too
# modify form to only show public collections to patrons
# get heroku set up for email notifications

# be able to access clothing detail from borrow request