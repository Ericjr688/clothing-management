from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from django.urls import reverse
from django.views import View
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse 
from django.db.models import Q, Avg
from .models import ClothingItem, ClothingItemImage, Tag
from .forms import ClothingItemImageForm, SearchForm, ReviewForm, ClothingItemForm 
from django.contrib.auth.decorators import login_required
from .forms import ClothingItemForm, ReviewForm
from django.http import HttpResponse
from clothing_collections.models import Collection
from borrowing.models import BorrowRequest
from users.models import UserProfile
from django.contrib import messages

class IndexView(View):
    def get(self, request):
        return render(request, 'clothing/index.html') 
    
def search(request):
    query = request.GET.get('q') or request.GET.get('keyword', '')
    matches = ClothingItem.search_combined(query)
    filtered_matches = [item for item in matches if item.is_viewable_by(request.user)]
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        results = []
        for item in filtered_matches:
            code = item.availability
            label = item.get_availability_display()
            results.append({
                'id': item.id,
                'name': item.name,
                'image_url': item.image.url if item.image else '',
                'availability': label,
                'availability_code': code,
            })
        return JsonResponse({'results': results})

    return render(request, 'clothing/search_results.html', {
        'items': filtered_matches,
        'search_query': query,
    })

@login_required
def return_view(request):
    checked_out_items = ClothingItem.objects.filter(
        checked_out_by=request.user,
        availability='checked_out'
    )

    if request.method == 'POST':
        items_to_return = request.POST.getlist('items_to_return')
        for item_id in items_to_return:
            try:
                item = checked_out_items.get(pk=item_id)
            except ClothingItem.DoesNotExist:
                continue

            item.checked_out_by = None
            item.availability = 'checked_in'
            item.save()

        messages.success(request, "Selected item(s) have been returned.")
        return redirect('clothing:return')

    return render(request, "clothing/return.html", {
        "checked_out_items": checked_out_items
    })

class SearchKeywordView(View):    
    template_name = "clothing/search.html"

    def get(self, request):
        keyword = request.GET.get('keyword', '')
        form = SearchForm(initial={'keyword':keyword})
        results = []

        if keyword:
            all_results = ClothingItem.search_combined(keyword)
            results = [item for item in all_results if item.is_viewable_by(request.user)]
        else:
            results=[]
        context = {
            'form': form,
            'keyword': keyword,
            'results': results,
        }
        return render(request, self.template_name, context)

    
    def post(self, request):
        """Handle search form submission."""
        form = SearchForm(request.POST)
        results = []
        keyword = ''

        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            # Perform search using your model
            matching_tags = Tag.objects.filter(
                Q(category__icontains=keyword) |
                Q(size__icontains=keyword) |
                Q(color__icontains=keyword)
            )

            # Use the matching tags to filter ClothingItems
            #results = ClothingItem.search_by_keyword(keyword)
            #results = ClothingItem.objects.filter(tags__in=matching_tags).distinct()
            results = ClothingItem.search_by_title(keyword)
        context = {
            'form': form,
            'keyword': keyword,
            'results': results
        }
        
        return render(request, self.template_name, context)

class LibrarianView(View):
    def get(self, request):
        return render(request, 'clothing/librarian.html')

class PatronView(View):
    def get(self, request):
        return render(request, 'clothing/patron.html')

class ProfileView(View):
    def get(self, request):
        return render(request, 'users/profile.html')

class FavoritesView(View):
    def get(self, request):
        return render(request, 'clothing/favorite.html')
    
# def clothing_item_detail(request, pk):
#     item = get_object_or_404(ClothingItem, pk=pk)
#     collections = item.collections.all()
#     print("Collections: ", collections)
#     return render(request, 'clothing/item_detail.html',  {
#         'item': item,
#         'collections': collections
#     })
    
def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    return render(request, 'clothing/collection_detail.html', {'collection': collection})

@login_required
def clothing_item_create(request):
    # only librarians can create new clothing items
    if request.user.userprofile.role != 'librarian':
        return HttpResponse("You do not have permission to create items.", status=403)
    if request.method == "POST":
        form = ClothingItemForm(request.POST, request.FILES)
        if form.is_valid():
            clothing_item = form.save(commit=False)
            clothing_item.owner = request.user.userprofile
            clothing_item.save()
            form.save_m2m()

            if clothing_item.image:
                ClothingItemImage.objects.create(
                    item=clothing_item,
                    image=clothing_item.image
                )
            return redirect('clothing:item_detail', pk=clothing_item.pk)
    else:
        form = ClothingItemForm()
    
    return render(request, 'clothing/item_form.html', {'form': form})

@login_required
def toggle_favorite(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    user_profile = request.user.userprofile
    if user_profile in item.likes.all():
        item.likes.remove(user_profile)
    else:
        item.likes.add(user_profile)
    return redirect('clothing:item_detail', pk=item.id)

@login_required
def favorites_list(request):
    likes = ClothingItem.objects.filter(likes=request.user.userprofile)
    return render(request, 'clothing/favorite.html', {'favorites': likes})

@login_required
def borrowed_list(request):
    borrowed_items = ClothingItem.objects.filter(checked_out_by=request.user)
    return render(request, 'clothing/borrowed.html', {'borrowed_items': borrowed_items})

def item_list(request):
    items = ClothingItem.objects.all()
    items = [item for item in items if item.is_viewable_by(request.user)]
    return render(request, 'clothing/item_list.html', {'items': items})

def browse_items_collections(request):
    items = ClothingItem.objects.all()   
    items = [item for item in items if item.is_viewable_by(request.user)]
    collections = Collection.objects.all()
    collections = [collection for collection in collections if collection.is_collection_viewable_by(request.user)] 
                     
    return render(request, 'clothing/browse.html', {'items': items, 'collections': collections})
   
def return_item(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    if not item.available:
        item.available = True
    else:
        # throw error? can't return if item is available (not checked out)
        pass
    item.save()
    return redirect('item_list')

def clothing_item_detail(request, pk):
    # 1) load the item
    item = get_object_or_404(ClothingItem, pk=pk)

    # 2) permission check
    if not item.is_viewable_by(request.user):
        return render(request, 'clothing/permission_denied.html', status=403)
    
    # 3) fetch reviews & stats
    reviews = item.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    total_rating_count = reviews.count()
    collections = item.collections.all()

    # 4) pending-borrow / other logic with borrow requests
    borrow_request = None
    pending_borrow = False
    due_date = None
    user_has_borrowed = False

    if request.user.is_authenticated:
        profile = getattr(request.user, 'userprofile', None)

        if profile:
            borrow_request = BorrowRequest.objects.filter(
                borrower=profile,
                clothing_item=item,
            ).order_by('-due_date').first()
            if borrow_request:
                due_date = borrow_request.due_date
                if borrow_request.status == 'pending':
                    pending_borrow = True
                elif borrow_request.status == 'approved':
                    user_has_borrowed = True
    available_from = due_date if not user_has_borrowed else None

    # 5) handle new review POST
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.clothing_item = item
            review.user = request.user
            review.save()
            return redirect('clothing:item_detail', pk=item.pk)
    else:
        form = ReviewForm()

    # 6) render template
    return render(request, 'clothing/item_detail.html', {
        'item': item,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_rating_count': total_rating_count,
        'form': form,
        'pending_borrow': pending_borrow,
        'collections': collections,
        'due_date': due_date,
        'user_has_borrowed': user_has_borrowed,
        'available_from': available_from,
    })

def remove_item(request, pk):
    item = get_object_or_404(ClothingItem, pk=pk)
    item.delete()  # Delete the item
    return redirect('clothing:browse') 

class ItemUpdateView(UpdateView):
    model = ClothingItem
    form_class = ClothingItemForm
    template_name = 'clothing/edit_item.html'
    def get_success_url(self):
        return reverse('clothing:item_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        item = self.get_object()
        if not request.user.is_authenticated or request.user.userprofile.role != 'librarian':
            return redirect('unauthorized')  # or use PermissionDenied
        if item.availability == 'checked_out':
            return redirect('clothing:item_detail', pk=item.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.object
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        item = self.get_object()

        if item.tags.exists():
            tag = item.tags.first()
            initial['category'] = tag.category
            initial['size'] = tag.size
            initial['color'] = tag.color

        return initial
    
def is_librarian(user):
    return user.is_authenticated and user.userprofile.role == 'librarian'

@login_required
@user_passes_test(is_librarian)
def remove_item(request, pk):
    item = get_object_or_404(ClothingItem, pk=pk)
    item.delete()
    return redirect('clothing:browse') 


def view_item_images(request, item_id):
    item = get_object_or_404(ClothingItem, pk=item_id)
    images = item.images.all()
    return render(request, 'clothing/view_images.html', {
        'item': item,
        'images': images
    })

@login_required
@user_passes_test(is_librarian)
def add_item_image(request, item_id):
    item = get_object_or_404(ClothingItem, pk=item_id)
    if request.method == 'POST':
        form = ClothingItemImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.item = item
            img.save()
            return redirect('clothing:view_images', item_id=item.id)
    else:
        form = ClothingItemImageForm()
    return render(request, 'clothing/add_item_image.html', {
        'item': item,
        'form': form
    })

@login_required
@user_passes_test(is_librarian)
def delete_item_image(request, item_id, image_id):
    item = get_object_or_404(ClothingItem, pk=item_id)
    img = get_object_or_404(ClothingItemImage, pk=image_id, item=item)
    if request.method == 'POST':
        img.delete()
        return redirect('clothing:view_images', item_id=item.id)
    return render(request, 'clothing/confirm_delete_image.html', {
        'item': item,
        'image': img
    })