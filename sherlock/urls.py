# sherlock-python/sherlock/urls.py
"""
Main URL Configuration for the Sherlock project.
...
"""
from django.contrib import admin
from django.urls import path, include
from inventory import views as inventory_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', inventory_views.homepage, name='homepage'),

    path('accounts/signup/', inventory_views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', include('inventory.urls')),
]

handler404 = 'inventory.views.custom_page_not_found_view'