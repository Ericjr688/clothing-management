from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.homepage, name='homepage'),
    path('profile/', views.profile, name='profile'),
    path('test-dashboard/', views.test_dashboard, name='test_dashboard'),
    path('upgrade-request/', views.request_librarian_upgrade, name='request_librarian_upgrade'),
    path('upgrade-requests/', views.librarian_upgrade_requests, name='librarian_upgrade_requests'),
    path('upgrade-request/<int:request_id>/approve/', views.approve_librarian_request, name='approve_librarian_request'),
    path('upgrade-request/<int:request_id>/deny/', views.deny_librarian_request, name='deny_librarian_request'),
    path('profile/edit-photo/', views.edit_profile_picture, name='edit_profile_picture'),
]
