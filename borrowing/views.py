from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from borrowing.models import BorrowRequest 
from clothing.models import ClothingItem
from users.models import UserProfile
from datetime import timedelta
from django.utils import timezone

@login_required
def create_borrow_request(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    
    if item.availability != 'checked_in':
        return HttpResponseForbidden("This item is currently not available for borrowing.")
    
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to borrow items.")
    
    if BorrowRequest.objects.filter(borrower=request.user.userprofile, clothing_item=item, status='pending').exists():
        return HttpResponseForbidden("You already have a pending borrow request for this item.")
    
    BorrowRequest.objects.create(
        borrower=request.user.userprofile,
        due_date=timezone.now() + timedelta(days=21),
        clothing_item=item,
        status='pending'
    )

    return redirect('clothing:item_detail', pk=item.id)


@login_required
def borrow_request_list(request):
    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can view borrow requests.")
    
    borrower_id = request.GET.get('borrower')
    item_id = request.GET.get('item')
    
    requests_qs = BorrowRequest.objects.all().order_by('-request_date')
    
    if borrower_id:
        requests_qs = requests_qs.filter(borrower__id=borrower_id)
    if item_id:
        requests_qs = requests_qs.filter(clothing_item__id=item_id)
    
    unique_borrowers = UserProfile.objects.filter(borrow_requests__isnull=False).distinct()
    unique_items = ClothingItem.objects.filter(borrow_requests__isnull=False).distinct()
    
    context = {
        'requests': requests_qs,
        'unique_borrowers': unique_borrowers,
        'unique_items': unique_items,
        'selected_borrower': borrower_id,
        'selected_item': item_id,
    }
    return render(request, 'borrowing/borrow_request_list.html', context)

@login_required
def approve_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can approve borrow requests.")
    
    borrow_request.status = 'approved'
    borrow_request.approver = request.user.userprofile
    borrow_request.save()

    # Deny all other requests for the same item
    BorrowRequest.objects.filter(
        clothing_item=borrow_request.clothing_item,
        status='pending'
    ).exclude(id=borrow_request.id).update(status='denied')

    item = borrow_request.clothing_item
    item.checked_out_by = borrow_request.borrower.user
    item.availability = 'checked_out'
    item.save()
    
    return redirect('borrowing:borrow_request_list')

@login_required
def deny_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)

    if request.user.userprofile.role != 'librarian':
        return HttpResponseForbidden("Only librarians can deny borrow requests.")
    
    borrow_request.status = 'denied'
    borrow_request.approver = request.user.userprofile
    borrow_request.save()

    return redirect('borrowing:borrow_request_list')
