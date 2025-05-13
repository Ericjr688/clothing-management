from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowing.models import BorrowRequest
from clothing.utils import send_email_notification

@receiver(post_save, sender=BorrowRequest)
def send_approval_email(sender, instance, created, **kwargs):
    # We only care about updates (not on creation) where status is 'approved'
    if created:
        return
    
    if instance.status == 'approved' and not instance.email_sent:
        # Retrieve the borrower's email and first name from the UserProfile (assuming they are set)
        borrower_email = instance.borrower.user.email
        borrower_first = instance.borrower.user.first_name
        
        # Format the due date nicely. If due_date is not set, use "N/A".
        due_date_str = instance.due_date.strftime("%B %d, %Y") if instance.due_date else "N/A"
        
        subject = f"Your Borrow Request for {instance.clothing_item.name} Has Been Approved"
        message = (
            f"Dear {borrower_first},\n\n"
            f"Your request to borrow '{instance.clothing_item.name}' has been approved.\n\n"
            f"Please note that the due date for this item is: {due_date_str}.\n\n"
            f"Pick up your item at: {instance.clothing_item.location}.\n\n"
            f"Thank you for using the B29 Clothing Lending App!\n\n"
            f"Best regards,\n"
            f"The B29 Clothes Library Team"
        )
        
        # Send the email using your email utility function.
        send_email_notification(subject, message, borrower_email)
        
        # Mark the request as having sent the email
        instance.email_sent = True
        instance.save(update_fields=['email_sent'])
