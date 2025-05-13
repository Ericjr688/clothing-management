from django.db import models
from django.contrib.auth.models import User, AbstractUser
from clothing.utils import send_email_notification
from django.utils import timezone
from users.models import UserProfile
from django.contrib.auth import get_user_model

class Tag(models.Model):
    ARTICLE_TYPES = [
        ('Tshirt', 'T-Shirt'),
        ('Jeans', 'Jeans'),
        ('Activewear', 'Activewear'),
        ('Jacket', 'Jacket'),
        ('Coat', 'Coat'),
        ('Accessories','Accessories')
    ] 
    SIZES = [
        ('xsmall', 'XS'),
        ('small','S'),
        ('med', 'M'),
        ('large', 'L'),
        ('xlarge', 'XL'),
        ('onesize', 'One Size')
    ]
    COLORS = [
        ('Red', 'Red'),
        ('Orange','Orange'),
        ('Yellow', 'Yellow'),
        ('Green', 'Green'),
        ('Blue', 'Blue'),
        ('Purple', 'Purple'),
        ('Pink', 'Pink'),
        ('White', 'White'),
        ('Black', 'Black'),
        ('Grey', 'Grey')
    ]
    category = models.CharField(max_length=50, blank=True, null=True, choices=ARTICLE_TYPES)
    size = models.CharField(max_length=20, blank=True, null=True, choices = SIZES)
    color = models.CharField(max_length=50, blank=True, null=True, choices = COLORS)
    def __str__(self):
        return f"{self.category} - {self.size} - {self.color}"   

class ClothingItem(models.Model):
    STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('in_repair', 'In Repair')
    ]

    id = models.AutoField(primary_key=True) #explicitly define ID
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    availability = models.CharField(max_length=20, choices=STATUS_CHOICES, default='checked_in')
    availability_date = models.DateField(null=True, blank=True)
    # I think it is easier to make this boolean instead of a string
    available = models.BooleanField(default=True)
    # owner of clothing item - foreign key relationship:
    owner = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, null=True, blank=True)

    #likes = models.ManyToManyField(UserProfile, related_name='liked_items', blank=True)
    likes = models.ManyToManyField(UserProfile, related_name='favorites', blank=True)
    collections = models.ManyToManyField('clothing_collections.Collection', related_name='collection_items', blank=True)
    location = models.CharField(max_length=100, default='UVA')
    checked_out_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='checked_out_items'
    )
    #image
    image = models.ImageField(upload_to='clothing_images/', blank=True, null=True)

    def total_likes(self):
        return self.likes.count()

    def check_if_overdue(self):
        """ Check if the item is overdue and send an email notification. """
        if self.availability == 'checked_out' and self.due_date < timezone.now().date():
            user_email = self.owner.user.email # Get user's email
            subject = "Clothing item overdue"
            message = f"Dear {self.owner.user.username},\n\nYour borrowed item '{self.name}' is overdue. Please return it as soon as possible.\n\nThank you!"
            send_email_notification(subject, message, user_email)

    def __str__(self):
        return f"{self.name} ({self.availability})"    
    @classmethod
    def search_by_title(cls, keyword):
        """Search for ClothingItems by a keyword in name or description"""
        return cls.objects.filter(models.Q(name__icontains=keyword) | models.Q(description__icontains=keyword))
    @classmethod
    def search_by_keyword(cls, keyword):
        """Search for ClothingItems by a keyword in name or description"""
        return cls.objects.filter(models.Q(tags__category__icontains=keyword) | models.Q(tags__size__icontains=keyword) | models.Q(tags__color__icontains=keyword)).distinct()

    @classmethod
    def search_combined(cls, keyword):
        return cls.objects.filter(
            models.Q(name__icontains=keyword) |
            models.Q(description__icontains=keyword) |
            models.Q(tags__category__icontains=keyword) |
            models.Q(tags__size__icontains=keyword) |
            models.Q(tags__color__icontains=keyword)
        ).distinct()

    def is_viewable_by(self, user):
        # If the user is not authenticated, treat them as anonymous.
        if not user.is_authenticated:
            # Anonymous users can only view the item if none of its collections are private.
            for collection in self.item_collections.all():
                if collection.visibility == 'private':
                    return False
            return True

        # If the user is authenticated, try to get their UserProfile.
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            # If the profile does not exist, treat them like an anonymous user.
            for collection in self.item_collections.all():
                if collection.visibility == 'private':
                    return False
            return True

        # For logged-in users with a profile:
        # Librarians can view everything.
        if profile.role == 'librarian':
            return True

        # For patrons, check all collections the item belongs to.
        # If the item is part of a private collection that the patron cannot access, return False.
        for collection in self.item_collections.all():
            if collection.visibility == 'private' and not (
            collection.owner == profile or
            collection.allowed_users.filter(pk=profile.pk).exists()
            ):
                return False
        return True
    
    def can_be_added_to(self, user, target_collection):
        # Check if the item is viewable by the user.
        if not self.is_viewable_by(user):
            return False
        # Check if the item is already in the target collection.
        if self in target_collection.items.all():
            return False
        # If the item is already in a private collection, don't allow it to be added elsewhere.
        if self.item_collections.filter(visibility__iexact='private').exists():
            return False
        # If the item is in a public collection and the target is private, disallow.
        if self.item_collections.filter(visibility__iexact='public').exists() and target_collection.visibility == 'private':
            return False
        return True
    
class Review(models.Model):
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user} on {self.clothing_item.name}'


class ClothingItemImage(models.Model):
    item = models.ForeignKey(
        ClothingItem,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='clothing_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} – image {self.pk}"
