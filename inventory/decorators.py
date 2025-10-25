# In inventory/decorators.py

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
            messages.error(request, "You do not have permission to access this page.")
            return redirect('inventory:dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view