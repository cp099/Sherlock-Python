# sherlock-python/inventory/urls.py

from django.urls import path
from . import views

# This is a common practice to namespace URLs, making them easier to reference from templates.
app_name = 'inventory'

urlpatterns = [
    # Search
    # GET /search -> search#index
    path('search/', views.search_index, name='search'),

    # Print Shop & Queue Management
    # GET /print_shop -> print_shop#index
    path('print-shop/', views.print_shop_index, name='print_shop_index'),
    # GET /print_page -> print_shop#show
    path('print-page/', views.print_page, name='print_page'),

    # POST /print_queue_items/:id/change_quantity
    path('print-queue-items/<int:item_id>/change-quantity/', views.change_print_item_quantity, name='print_item_change_quantity'),
    # DELETE /print_queue_items/:id/delete_item
    path('print-queue-items/<int:item_id>/delete/', views.delete_print_item, name='print_item_delete'),

    # Sections Routes (resources :sections)
    path('sections/', views.section_list, name='section_list'),
    path('sections/new/', views.section_create, name='section_create'),
    path('sections/<int:section_code>/', views.section_detail, name='section_detail'),
    path('sections/<int:section_code>/edit/', views.section_update, name='section_update'),
    path('sections/<int:section_code>/delete/', views.section_delete, name='section_delete'),
    # POST /sections/:sectioncode/add_to_queue
    path('sections/<int:section_code>/add-to-queue/', views.section_add_to_queue, name='section_add_to_queue'),

    # Spaces Routes (resources :spaces, nested under sections)
    path('sections/<int:section_code>/spaces/new/', views.space_create, name='space_create'),
    path('sections/<int:section_code>/spaces/<int:space_code>/', views.space_detail, name='space_detail'),
    path('sections/<int:section_code>/spaces/<int:space_code>/edit/', views.space_update, name='space_update'),
    path('sections/<int:section_code>/spaces/<int:space_code>/delete/', views.space_delete, name='space_delete'),
    # POST /sections/:sectioncode/spaces/:spacecode/add_to_queue
    path('sections/<int:section_code>/spaces/<int:space_code>/add-to-queue/', views.space_add_to_queue, name='space_add_to_queue'),

    # Items Routes (resources :items, nested under spaces)
    path('sections/<int:section_code>/spaces/<int:space_code>/items/new/', views.item_create, name='item_create'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/', views.item_detail, name='item_detail'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/edit/', views.item_update, name='item_update'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/delete/', views.item_delete, name='item_delete'),
    # POST /.../add_small_to_queue
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/add-small-to-queue/', views.item_add_small_to_queue, name='item_add_small_to_queue'),
    # POST /.../add_large_to_queue
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/add-large-to-queue/', views.item_add_large_to_queue, name='item_add_large_to_queue'),
]