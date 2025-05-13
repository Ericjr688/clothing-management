from django.conf import settings

def google_oauth(request):
    return {
        'GOOGLE_OAUTH_CLIENT_ID': settings.GOOGLE_OAUTH_CLIENT_ID
    }
