from django.urls import path
from clothing.views import SearchKeywordView, IndexView, LibrarianView, PatronView, ProfileView, ItemUpdateView
from clothing_collections import views

from . import views

app_name = "clothing"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("search/", views.search, name='search'),
    path("librarian/", LibrarianView.as_view(), name="librarian"),
    path("patron/", PatronView.as_view(), name="patron"),
    path("create/", views.clothing_item_create, name="item_create"),
    path("return/", views.return_view, name="return_item"),
    path('return/', views.return_view, name='return'),
    path('item/<int:pk>/', views.clothing_item_detail, name='item_detail'),
    path('item/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='edit_item'),
    path('item/<int:pk>/remove/', views.remove_item, name='remove_item'),
    path('browse/', views.browse_items_collections, name="browse"),
    path('toggle_favorite/<int:item_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorite/', views.favorites_list, name="favorite"),
    path('borrowed/', views.borrowed_list, name="borrowed"),
    path("profile/", ProfileView.as_view(), name='profile'),
    path('collection/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('item/<int:item_id>/images/', views.view_item_images, name='view_images'),
    path('item/<int:item_id>/images/add/', views.add_item_image, name='add_item_image'),
    path('item/<int:item_id>/images/<int:image_id>/delete/', views.delete_item_image, name='delete_item_image'),
]