# sherlock-python/sherlock/urls.py

from django.contrib import admin
from django.urls import path, include
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # This is our new landing page for the root URL
    path('', inventory_views.landing_page, name='landing_page'),

    # User Authentication (Login, Logout, etc.)
    path('accounts/signup/', inventory_views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    # All other app-specific URLs
    path('', include('inventory.urls')),
]