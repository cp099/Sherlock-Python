# sherlock-python/sherlock/urls.py

"""
Main URL Configuration for the Sherlock project.

This file routes URLs at the project level. It handles:
- The admin site.
- The public-facing landing page (homepage).
- The user authentication URLs (login, logout, signup).
- Delegates all other application-specific URLs to the `inventory` app's urls.py.
"""

from django.contrib import admin
from django.urls import path, include
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', inventory_views.landing_page, name='homepage'),

    path('accounts/signup/', inventory_views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', include('inventory.urls')),
]