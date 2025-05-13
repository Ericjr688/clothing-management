from django.core.mail import send_mail
from django.conf import settings

def send_email_notification(subject, message, recipient_email):
    """ Sends an email notification to a user. """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )