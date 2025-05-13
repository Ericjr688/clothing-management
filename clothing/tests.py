from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from clothing.models import ClothingItem, Tag
from users.models import UserProfile

class SearchKeywordViewTest(TestCase):
    def setUp(self):
        """Setup test data for search functionality"""
        self.client = Client()
        # Create a test user
        self.user = get_user_model().objects.create_user(username="testuser", password="password123")
        self.profile = UserProfile.objects.create(
            user=self.user, 
            role="patron", 
            google_id=111, 
            profile_picture="http://example.com/profile.jpg"
        )
        tag = Tag.objects.create(category="outerwear", size="med", color="Red")
        print(tag, type(tag))

        # Create ClothingItem instances using the owner field
        self.item1 = ClothingItem.objects.create(
            name="Red Hoodie",
            owner=self.profile,
            description="A comfortable red hoodie for winter",
            availability_date="2025-01-01"
        )
        self.item1.save()
        self.item1.tags.add(tag)

        tag = Tag.objects.create(category="Bottoms", size="med", color="Blue")
        self.item2 = ClothingItem.objects.create(
            name="Blue Jeans",
            owner=self.profile,
            description="Classic blue jeans for everyday wear",
            availability_date="2025-01-01"
        )
        self.item2.save()
        self.item2.tags.add(tag)

class ClothingItemLikesTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user1 = User.objects.create_user(username="user1", password="testpass", email="user1@example.com")
        self.user2 = User.objects.create_user(username="user2", password="testpass", email="user2@example.com")
        
        self.profile1 = UserProfile.objects.create(
            user=self.user1, role="patron", google_id="google_id_1", profile_picture="http://example.com/pic1.jpg"
        )
        self.profile2 = UserProfile.objects.create(
            user=self.user2, role="patron", google_id="google_id_2", profile_picture="http://example.com/pic2.jpg"
        )
        
        tag = Tag.objects.create(category="tops", size="s", color="Red")
        self.clothing = ClothingItem.objects.create(
            name="Test Shirt",
            description="A test shirt",
            availability_date="2025-01-01",
            owner=self.profile1,
        )
        self.clothing.tags.add(tag)

    def test_initial_likes_count(self):
        """Ensure that a new ClothingItem starts with zero likes."""
        self.assertEqual(self.clothing.total_likes(), 0)

    def test_add_like(self):
        """Adding a like should increase the count and include the profile in the likes."""
        self.clothing.likes.add(self.profile1)
        self.assertEqual(self.clothing.total_likes(), 1)
        self.assertIn(self.profile1, self.clothing.likes.all())

    def test_add_multiple_likes(self):
        """Test that multiple likes are counted properly."""
        self.clothing.likes.add(self.profile1)
        self.clothing.likes.add(self.profile2)
        self.assertEqual(self.clothing.total_likes(), 2)
        self.assertIn(self.profile1, self.clothing.likes.all())
        self.assertIn(self.profile2, self.clothing.likes.all())

    def test_remove_like(self):
        """Removing a like should decrease the count."""
        self.clothing.likes.add(self.profile1)
        self.clothing.likes.remove(self.profile1)
        self.assertEqual(self.clothing.total_likes(), 0)