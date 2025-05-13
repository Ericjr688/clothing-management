from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from users.models import UserProfile
from clothing.models import ClothingItem, Tag 
from .models import Collection, CollectionAccessRequest

User = get_user_model()

class CollectionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.patron_user = User.objects.create_user(username='patron1', password='pass123', email='patron@example.com')
        self.librarian_user = User.objects.create_user(username='lib1', password='pass123', email='lib@example.com')
        
        self.patron_profile = UserProfile.objects.create(
            user=self.patron_user, role='patron', google_id='patron_google', profile_picture=''
        )
        self.librarian_profile = UserProfile.objects.create(
            user=self.librarian_user, role='librarian', google_id='lib_google', profile_picture=''
        )
        
        self.item = ClothingItem.objects.create(
            name='Test Shirt',
            description='A test shirt',
            availability_date=date.today()
        )
        
        # Create a public collection owned by the patron.
        self.public_collection = Collection.objects.create(
            title='Public Collection',
            description='A public collection',
            owner=self.patron_profile,
            visibility='public'
        )
        
        # Create a private collection owned by the librarian.
        self.private_collection = Collection.objects.create(
            title='Private Collection',
            description='A private collection',
            owner=self.librarian_profile,
            visibility='private'
        )

        # allow the patron in the private collection.
        self.private_collection.allowed_users.add(self.patron_profile)
        
    def test_create_collection_librarian(self):
        """
        Test that a librarian can create a private collection.
        """
        self.client.login(username='lib1', password='pass123')
        response = self.client.post(reverse('clothing_collections:create_collection'), {
            'title': 'Librarian Private Collection',
            'description': 'A collection by librarian',
            'visibility': 'private',
        })
        self.assertEqual(response.status_code, 302)
        collection = Collection.objects.get(title='Librarian Private Collection')
        self.assertEqual(collection.visibility, 'private')
        self.assertEqual(collection.owner, self.librarian_profile)
        
    def test_add_item_to_public_collection_by_owner(self):
        """
        Test that the owner (patron) of a public collection can add an item.
        """
        self.client.login(username='patron1', password='pass123')
        response = self.client.post(
            reverse('clothing_collections:add_item_to_collection', kwargs={'collection_id': self.public_collection.id, 'item_id': self.item.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.item, self.public_collection.items.all())
        
    def test_add_item_to_private_collection_by_non_modifier(self):
        """
        Test that a patron (not the owner) cannot add an item to a private collection.
        """
        # patron trying to add an item to a private collection owned by librarian
        self.client.login(username='patron1', password='pass123')
        response = self.client.post(
            reverse('clothing_collections:add_item_to_collection', kwargs={'collection_id': self.private_collection.id, 'item_id': self.item.id})
        )
        self.assertEqual(response.status_code, 403)
        
    def test_edit_collection_permission(self):
        """
        Test that only authorized users can edit a collection.
        Patrons can edit their own public collections; patrons cannot edit others' collections.
        """
        # Patron edits their own public collection
        self.client.login(username='patron1', password='pass123')
        response = self.client.post(
            reverse('clothing_collections:edit_collection', kwargs={'collection_id': self.public_collection.id}),
            {'title': 'Updated Public Collection', 'description': 'Updated description', 'visibility': 'public'}
        )
        self.assertEqual(response.status_code, 302)
        updated = Collection.objects.get(id=self.public_collection.id)
        self.assertEqual(updated.title, 'Updated Public Collection')
        
        # Patron trying to edit a private collection they don't own.
        response = self.client.post(
            reverse('clothing_collections:edit_collection', kwargs={'collection_id': self.private_collection.id}),
            {'title': 'Illegal Edit', 'description': 'Should not work', 'visibility': 'private'}
        )
        self.assertEqual(response.status_code, 403)
        
    def test_delete_collection_permission(self):
        """
        Test that only users with proper permissions can delete a collection.
        """
        # Patron deletes their own public collection.
        self.client.login(username='patron1', password='pass123')
        response = self.client.post(
            reverse('clothing_collections:delete_collection', kwargs={'collection_id': self.public_collection.id})
        )
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Collection.DoesNotExist):
            Collection.objects.get(id=self.public_collection.id)
        
        # Patron tries to delete a collection they do not own.
        self.client.logout()
        self.client.login(username='patron1', password='pass123')
        response = self.client.post(
            reverse('clothing_collections:delete_collection', kwargs={'collection_id': self.private_collection.id})
        )
        self.assertEqual(response.status_code, 403)
        
    def test_make_collection_request(self):
        """
        Test that a patron can make an access request for a private collection they are not allowed to view.
        """
        # Create a new private collection without allowing the patron.
        self.client.login(username='patron1', password='pass123')
        new_private = Collection.objects.create(
            title='New Private Collection',
            description='Test private',
            owner=self.librarian_profile,
            visibility='private'
        )
        # Patron is not in allowed_users yet, so they can request access.
        response = self.client.post(
            reverse('clothing_collections:make_collection_request', kwargs={'collection_id': new_private.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(new_private.access_requests.filter(requester=self.patron_profile, status='pending').exists())
        
    def test_approve_collection_request(self):
        """
        Test that only librarians can approve collection access requests.
        """
        # Patron makes a request.
        self.client.login(username='patron1', password='pass123')
        response = self.client.post(
            reverse('clothing_collections:make_collection_request', kwargs={'collection_id': self.private_collection.id})
        )

        self.assertEqual(response.status_code, 302)
        request_obj = self.private_collection.access_requests.get(requester=self.patron_profile)
        
        # Now librarian approves the request.
        self.client.logout()
        self.client.login(username='lib1', password='pass123')
        response = self.client.post(
            reverse('clothing_collections:approve_collection_request', kwargs={'collection_id': self.private_collection.id, 'request_id': request_obj.id})
        )
        self.assertEqual(response.status_code, 302)
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, 'approved')
        self.assertIn(self.patron_profile, self.private_collection.allowed_users.all())
        
    def test_collection_detail_view(self):
        """
        Test that the collection detail view respects permissions.
        """
        # For a logged-in patron, if they are allowed, the detail view should work.
        self.client.login(username='patron1', password='pass123')
        response = self.client.get(
            reverse('clothing_collections:collection_detail', kwargs={'collection_id': self.public_collection.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_collection.title)
        
        # For an anonymous user, only public collections are visible.
        self.client.logout()
        response = self.client.get(
            reverse('clothing_collections:collection_detail', kwargs={'collection_id': self.private_collection.id})
        )
        self.assertEqual(response.status_code, 403)
        
    def test_collection_list_view(self):
        """
        Test that the collection list view returns only collections visible to the user.
        """
        # For a logged-in patron, both public collections and private collections they are allowed to view should appear.
        self.client.login(username='patron1', password='pass123')
        response = self.client.get(reverse('clothing_collections:collection_list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(self.public_collection.title, content)
        self.assertIn(self.private_collection.title, content)
        
        # For an anonymous user, only public collections should appear.
        self.client.logout()
        response = self.client.get(reverse('clothing_collections:collection_list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(self.public_collection.title, content)
        self.assertNotIn(self.private_collection.title, content)


# Test that librarian operate on patron collection, patron operate on only their collection
# Also test that an item can be in more than one public collection at ones, but solely in private collections