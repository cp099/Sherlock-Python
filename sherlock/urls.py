# sherlock-python/sherlock/urls.py
from django.contrib import admin
from django.urls import path, include
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # The root URL points to our landing page.
    path('', inventory_views.landing_page, name='homepage'),

    path('accounts/signup/', inventory_views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    # All other app-specific URLs
    path('', include('inventory.urls')),
]