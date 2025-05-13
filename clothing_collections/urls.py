from django.urls import path
from . import views

app_name = 'clothing_collections'

urlpatterns = [
    path('create/', views.create_collection, name='create_collection'),
    path('item/<int:collection_id>/<int:item_id>/add/', views.add_item_to_collection, name='add_item_to_collection'),
    path('item/<int:collection_id>/<int:item_id>/remove/', views.remove_item_from_collection, name='remove_item_from_collection'),
    path('<int:collection_id>/edit/', views.edit_collection, name='edit_collection'),
    path('<int:collection_id>/delete/', views.delete_collection, name='delete_collection'),
    path('<int:collection_id>/request/', views.make_collection_request, name='make_collection_request'),
    path('<int:collection_id>/request/<int:request_id>/approve/', views.approve_collection_request, name='approve_collection_request'),
    path('<int:collection_id>/request/<int:request_id>/deny/', views.deny_collection_request, name='deny_collection_request'),
    path('<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('', views.collection_list, name='collection_list'),
    path('select-for-collection/<int:collection_id>/', views.select_items_for_collection, name='select_items_for_collection'),
]
