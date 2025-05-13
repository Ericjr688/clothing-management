from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from .models import Collection
from clothing.models import ClothingItem
from .forms import CollectionForm
from django.contrib import messages
from django.db.models import Q

# Create your views here.
@login_required
def create_collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, user=request.user)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user.userprofile
            if request.user.userprofile.role == 'patron':
                collection.visibility = 'public'
            collection.save()
            form.save_m2m()
            return redirect('clothing_collections:collection_detail', collection_id=collection.id)
    else:
        form = CollectionForm(user=request.user)
    return render(request, 'clothing_collections/create_collection.html', {'form': form})

@login_required
def add_item_to_collection(request, collection_id, item_id):
    collection = get_object_or_404(Collection, id=collection_id)
    item = get_object_or_404(ClothingItem, id=item_id)
    if not collection.can_modify_collection(request.user):
        return HttpResponseForbidden("You do not have permission to modify this collection.")
    
    # if item is in a private collection, do not add it to any other collection
    if item.item_collections.filter(visibility='private').exists():
        return HttpResponseForbidden("This item is in a private collection and cannot be added to another collection.")
    
    # if item is in a public collection, only add it to a public collection
    if item.item_collections.filter(visibility='public').exists() and collection.visibility == 'private':
        return HttpResponseForbidden("This item is in a public collection and cannot be added to a private collection.")
    
    collection.items.add(item)
    return redirect('clothing_collections:collection_detail', collection_id=collection.id)

@login_required
def remove_item_from_collection(request, collection_id, item_id):
    collection = get_object_or_404(Collection, id=collection_id)
    item = get_object_or_404(ClothingItem, id=item_id)
    if not collection.can_modify_collection(request.user):
        return HttpResponseForbidden("You do not have permission to modify this collection.")
    
    collection.items.remove(item)
    return redirect('clothing_collections:collection_detail', collection_id=collection.id)

@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if not collection.can_modify_collection(request.user):
        return HttpResponseForbidden("You do not have permission to modify this collection.")
    
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection, user=request.user)
        if form.is_valid():
            # Check if the visibility is being changed to private
            new_visibility = form.cleaned_data.get('visibility')
            if new_visibility == 'private':
                # For each item in the collection, verify it is not in any other collection.
                for item in collection.items.all():
                    if item.item_collections.exclude(id=collection.id).exists():
                        form.add_error('visibility', 
                            f"Cannot change to private: Item '{item.name}' is present in another collection.")
                        return render(request, 'clothing_collections/create_collection.html', {'form': form})
            form.save()
            return redirect('clothing_collections:collection_detail', collection_id=collection.id)
    else:
        # Pass the instance to pre-fill the form with the collection's details
        form = CollectionForm(instance=collection, user=request.user)
    
    return render(request, 'clothing_collections/create_collection.html', {'form': form})

@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if not collection.can_modify_collection(request.user):
        return HttpResponseForbidden("You do not have permission to modify this collection.")
    
    if request.method == 'POST':
        collection.delete()
        messages.success(request, "Collection deleted successfully.")
        return redirect('clothing_collections:collection_list')
    else:
        return HttpResponse("Only POST requests are allowed to delete a collection.", status=405)
    
@login_required
def make_collection_request(request, collection_id):
       
    collection = get_object_or_404(Collection, id=collection_id)
    user_profile = request.user.userprofile

    if user_profile.role != 'patron':
        return HttpResponseForbidden("Only patrons can request access to collections.")
    
    if collection.visibility != 'private':
        return HttpResponseForbidden("Only private collections can have access requests.")
    
    existing_request = collection.access_requests.filter(requester=user_profile, status='pending').first()
    if existing_request:
        return HttpResponseForbidden("You have already requested access to this collection.")
    
    collection.access_requests.create(requester=user_profile)

    # maybe implement method to send a notification to the collection owner

    return redirect('clothing_collections:collection_list')

@login_required
def approve_collection_request(request, collection_id, request_id):
    if request.method != 'POST':
        return HttpResponse("Only POST requests are allowed to approve a collection request.", status=405)
    
    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can approve collection requests.")
    
    collection = get_object_or_404(Collection, id=collection_id)
    collection_request = get_object_or_404(collection.access_requests, id=request_id)
    
    if not collection.can_modify_collection(request.user):
        return HttpResponseForbidden("You do not have permission to modify this collection.")
    
    collection_request.status = 'approved'
    collection_request.save()

    collection.allowed_users.add(collection_request.requester)

    # maybe implement method to send a notification to the requester

    return redirect('clothing_collections:collection_detail', collection_id=collection.id)

@login_required
def deny_collection_request(request, collection_id, request_id):
    if request.method != 'POST':
        return HttpResponse("Only POST requests are allowed to deny a collection request.", status=405)
    
    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can deny collection requests.")
    
    collection = get_object_or_404(Collection, id=collection_id)
    collection_request = get_object_or_404(collection.access_requests, id=request_id)
    
    if not collection.can_modify_collection(request.user):
        return HttpResponseForbidden("You do not have permission to modify this collection.")
    
    collection_request.status = 'denied'
    collection_request.save()
    return redirect('clothing_collections:collection_detail', collection_id=collection.id)

def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if not collection.can_access_directly(request.user):
        return HttpResponseForbidden("You do not have permission to view this collection.", status=403)
    collection.can_modify = collection.can_modify_collection(request.user)

    items = collection.items.all()
    search_query = request.GET.get('q', '').strip()
    if search_query:
        
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__category__icontains=search_query) |
            Q(tags__size__icontains=search_query) |
            Q(tags__color__icontains=search_query)
        )

    access_requests = None
    if request.user.is_authenticated and request.user.userprofile.role == 'librarian':
        access_requests = collection.access_requests.filter(status='pending')
    return render(request, 'clothing_collections/collection_detail.html', {'collection': collection, 'items': items, 'access_requests': access_requests, 'search_query': search_query})

def collection_list(request):
    search_query = request.GET.get('q', '').strip()
    
    if search_query:
        filtered_collections = Collection.objects.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    else:
        filtered_collections = Collection.objects.all()
    
    # Filter to include only collections viewable by the user.
    collections = [
        collection for collection in filtered_collections 
        if collection.is_collection_viewable_by(request.user)
    ]
    
    for collection in collections:
        collection.can_access = collection.can_access_directly(request.user)
        collection.pending_request = collection.has_pending_request(request.user)
    
    context = {
        'collections': collections,
        'search_query': search_query,
    }
    return render(request, 'clothing_collections/collection_list.html', context)

@login_required
def select_items_for_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    if not collection.can_modify_collection(request.user):
        return HttpResponseForbidden("You do not have permission to modify this collection.")
    
    search_query = request.GET.get('q', '').strip()
    if search_query:
        items = ClothingItem.search_combined(search_query)
    else:
        items = ClothingItem.objects.all()
    
    # Filter out items already in the collection and only show items viewable by the user.
    items_to_add = [item for item in items if item.can_be_added_to(request.user, collection)]
    
    if request.method == "POST":
        selected_ids = request.POST.getlist('selected_items')
        for item_id in selected_ids:
            response = add_item_to_collection(request, collection_id, item_id)
            # If the response is not a redirect, it means there was an error adding the item.
            if response.status_code != 302:
                return response
        return redirect('clothing_collections:collection_detail', collection_id=collection.id)

    context = {
        'collection': collection,
        'items': items_to_add,
        'search_query': search_query,
    }
    return render(request, 'clothing_collections/select_items.html', context)
