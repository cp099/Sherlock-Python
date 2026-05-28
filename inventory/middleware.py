# sherlock-python/inventory/middleware.py

from django.utils import timezone
from datetime import timedelta
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

        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                profile = request.user.profile
                now = timezone.now()
                if not profile.last_seen or now - profile.last_seen > timedelta(minutes=1):
                    UserProfile.objects.filter(user=request.user).update(last_seen=now)
            except UserProfile.DoesNotExist:
                pass
        
        return response