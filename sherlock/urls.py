# sherlock-python/sherlock/urls.py

from django.contrib import admin
from django.urls import path, include
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # User Authentication Routes (replaces devise_for :users)
    path('accounts/', include('django.contrib.auth.urls')),

    # All inventory, print, and search URLs will be handled by the 'inventory' app.
    # The empty string '' means it will match paths like /sections/, /search/, etc.
    path('', include('inventory.urls')),

    # Root of the site (Homepage)
    # This MUST come after including the inventory urls if they are at the root.
    # Let's create a dedicated view for the homepage.
    path('', inventory_views.homepage, name='homepage'),
]