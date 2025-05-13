import os

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from users.models import UserProfile
from django.core.files.storage import default_storage

@csrf_exempt
def sign_in(request):
    return render(request, 'sign_in.html', {
        "login_uri": f"{request.scheme}://{request.get_host()}/sim/auth-receiver"
                                            })

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, google_requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)

    # In a real app, I'd also save any new user here to the database.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    
    # Get data about the user from the Google response
    email = user_data.get("email")
    first_name = user_data.get("given_name", "")
    last_name = user_data.get("family_name", "")
    google_id = user_data.get("sub")
    profile_pic = user_data.get("picture")


    # Get or create a Django user
    user, created = User.objects.get_or_create(
        username=email,
        defaults={"first_name": first_name, "last_name": last_name, "email": email}
    )

    # Selected role for new users is always patron.
    selected_role = "patron"
    if created:
        # Create a new UserProfile with the selected role
        profile = UserProfile.objects.create(user=user, role=selected_role, google_id=google_id)
    
        if profile_pic:
            try:
                response = requests.get(profile_pic)
                if response.status_code == 200:
                    img_content = ContentFile(response.content)
                    filename = f"{email}_profile.jpg"
                    profile.profile_picture.save(filename, img_content, save=True)
                    profile.profile_picture.storage = default_storage
                    profile.save()
                    print(profile.profile_picture.url)
                    
            except Exception as e:
                print(f"Error downloading profile picture: {e}")
    
     # Log the user in and then clear the selected role from the session
    login(request, user)

    return redirect('homepage')

def sign_out(request):
    logout(request)
    return redirect("sign_in")

#change role select so you just login as a borrower by default
# change gooogle id to be email.