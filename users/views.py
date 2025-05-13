from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from users.forms import ProfilePictureForm
from .models import UserProfile, LibrarianUpgradeRequest
from clothing_collections.models import ClothingItem, Collection
from django.db.models import Count
import random

def homepage(request):
    # Get only items with images
    items_with_images = ClothingItem.objects.filter(available=True).exclude(image__isnull=True).exclude(image='')
    items = list(items_with_images)

    # get only viewable items
    items = [item for item in items if item.is_viewable_by(request.user)]
    random.shuffle(items)
    random_items = items # 6 random items

    # Get public collections that are not empty:
    all_collections = Collection.objects.annotate(num_items=Count('items')).filter(num_items__gt=0).distinct()
    # Only keep collections that are viewable by the current user.
    collection_carousels = [col for col in all_collections if col.can_access_directly(request.user)]

    context = {
        'random_items': random_items,
        'collection_carousels': collection_carousels,
    }
    return render(request, 'users/homepage.html', context)

def test_dashboard(request):
    if not request.user.is_authenticated:
        return render(request, "users/test_dashboard.html")
    
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = None

    context = {
        "user": request.user,
        "profile": profile,
    }
    
    if profile and profile.role:
        if profile.role == "librarian":
            return redirect("clothing:librarian")
        elif profile.role == "patron":
            return redirect("clothing:patron")
    
    return render(request, "users/test_dashboard.html", context)

@login_required
def profile(request):
    # grab or 404 if they somehow have no profile
    user_profile = get_object_or_404(UserProfile, user=request.user)

    context = {
        'user': request.user,
        'profile': user_profile,
    }
    return render(request, 'users/profile.html', context)

@login_required
def request_librarian_upgrade(request):
    user_profile = request.user.userprofile
    # Only patrons can request an upgrade.
    if user_profile.role == 'librarian':
        messages.info(request, "You are already a librarian.")
        return redirect('profile') 

    # Check if there's already a pending request.
    if user_profile.librarian_upgrade_requests.filter(status='pending').exists():
        messages.info(request, "Your upgrade request is already pending.")
        return redirect('profile') 

    # Create the upgrade request.
    LibrarianUpgradeRequest.objects.create(requester=user_profile)
    messages.success(request, "Your upgrade request has been submitted and is now pending.")
    return redirect('profile')

# display all pending requests for librarians
@login_required
def librarian_upgrade_requests(request):
    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can access this page.")
    pending_requests = LibrarianUpgradeRequest.objects.filter(status='pending')
    return render(request, 'users/upgrade_requests.html', {'pending_requests': pending_requests})

# approve requests
@login_required
def approve_librarian_request(request, request_id):
    if request.method != 'POST':
        return HttpResponse("Only POST requests allowed.", status=405)
    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can approve upgrade requests.")

    upgrade_request = get_object_or_404(LibrarianUpgradeRequest, id=request_id)
    upgrade_request.status = 'approved'
    upgrade_request.save()
    
    # Upgrade the requester’s role
    user_profile = upgrade_request.requester
    user_profile.role = 'librarian'
    user_profile.save()
    
    messages.success(request, f"{user_profile.user.username} has been upgraded to librarian.")
    return redirect('librarian_upgrade_requests')

#deny requests
@login_required
def deny_librarian_request(request, request_id):
    if request.method != 'POST':
        return HttpResponse("Only POST requests allowed.", status=405)
    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can deny upgrade requests.")
    upgrade_request = get_object_or_404(LibrarianUpgradeRequest, id=request_id)
    upgrade_request.status = 'denied'
    upgrade_request.save()
    messages.info(request, f"Upgrade request for {upgrade_request.requester.user.username} has been denied.")
    return redirect('librarian_upgrade_requests')

@login_required
def edit_profile_picture(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  
            return redirect('clothing:profile') 
    else:
        form = ProfilePictureForm(instance=profile)

    return render(request, 'users/edit_profile_picture.html', {
        'form': form
    })

