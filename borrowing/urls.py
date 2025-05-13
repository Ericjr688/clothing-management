from django.urls import path
from . import views

app_name = 'borrowing'

urlpatterns = [
    path('request/<int:item_id>/', views.create_borrow_request, name='create_borrow_request'),
    path('list/', views.borrow_request_list, name='borrow_request_list'),
    path('approve/<int:request_id>/', views.approve_borrow_request, name='approve_borrow_request'),
    path('deny/<int:request_id>/', views.deny_borrow_request, name='deny_borrow_request'),
]