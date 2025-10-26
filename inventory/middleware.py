# sherlock-python/inventory/middleware.py

from django.utils import timezone
from .models import UserProfile

class UpdateLastSeenMiddleware:
    """
    Custom middleware to update the 'last_seen' timestamp for an
    authenticated user with every request they make.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            UserProfile.objects.filter(user=request.user).update(last_seen=timezone.now())
        
        return response