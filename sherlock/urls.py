# sherlock-python/sherlock/urls.py

from django.contrib import admin
from django.urls import path, include
from inventory import views as inventory_views # We still need this for the landing page

urlpatterns = [
    path('admin/', admin.site.urls),

    # The root URL points to our landing page for logged-out users
    path('', inventory_views.landing_page, name='landing_page'),

    # User Authentication (Login, Logout, Signup)
    path('accounts/signup/', inventory_views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    # All other app-specific URLs (including our new /dashboard/)
    # will be handled by the inventory app's urls.py file.
    path('', include('inventory.urls')),
]