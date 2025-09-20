# sherlock-python/inventory/urls.py

from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Search
    path('search/', views.search_index, name='search'),

    # Print Shop & Queue Management
    path('print/', views.print_queue, name='print_queue'), # The main queue page
    path('print/clear/', views.clear_print_queue, name='clear_print_queue'), # To clear the whole queue
    path('print-shop/', views.print_shop_index, name='print_shop_index'), # The instructions page
    path('print-page/', views.print_page, name='print_page'), # The final printable page
    path('print-queue-items/<int:item_id>/change-quantity/', views.change_print_item_quantity, name='print_item_change_quantity'),
    path('print-queue-items/<int:item_id>/delete/', views.delete_print_item, name='print_item_delete'),

    # Sections Routes
    path('sections/', views.section_list, name='section_list'),
    path('sections/new/', views.section_create, name='section_create'),
    path('sections/<int:section_code>/', views.section_detail, name='section_detail'),
    path('sections/<int:section_code>/edit/', views.section_update, name='section_update'),
    path('sections/<int:section_code>/delete/', views.section_delete, name='section_delete'),
    path('sections/<int:section_code>/add-to-queue/', views.section_add_to_queue, name='section_add_to_queue'),

    # Spaces Routes
    path('sections/<int:section_code>/spaces/', views.space_list, name='space_list'),
    path('sections/<int:section_code>/spaces/new/', views.space_create, name='space_create'),
    path('sections/<int:section_code>/spaces/<int:space_code>/', views.space_detail, name='space_detail'),
    path('sections/<int:section_code>/spaces/<int:space_code>/edit/', views.space_update, name='space_update'),
    path('sections/<int:section_code>/spaces/<int:space_code>/delete/', views.space_delete, name='space_delete'),
    path('sections/<int:section_code>/spaces/<int:space_code>/add-to-queue/', views.space_add_to_queue, name='space_add_to_queue'),

    # Items Routes
    path('sections/<int:section_code>/spaces/<int:space_code>/items/', views.item_list, name='item_list'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/new/', views.item_create, name='item_create'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/', views.item_detail, name='item_detail'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/edit/', views.item_update, name='item_update'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/delete/', views.item_delete, name='item_delete'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/add-small-to-queue/', views.item_add_small_to_queue, name='item_add_small_to_queue'),
    path('sections/<int:section_code>/spaces/<int:space_code>/items/<int:item_code>/add-large-to-queue/', views.item_add_large_to_queue, name='item_add_large_to_queue'),

    # Live Student Search (for HTMX)
    path('live-student-search/', views.live_student_search, name='live_student_search'),

    # Live Item Search (for HTMX)
    path('live-item-search/<int:student_id>/', views.live_item_search, name='live_item_search'),

    # Live Unified Search (for HTMX)
    path('live-unified-student-search/', views.live_unified_student_search, name='live_unified_student_search'),
    path('live-unified-item-search/', views.live_unified_item_search, name='live_unified_item_search'),

    # Student Routes
    path('students/', views.student_list, name='student_list'),
    path('students/new/', views.student_create, name='student_create'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.student_update, name='student_update'),
    path('students/<int:student_id>/delete/', views.student_delete, name='student_delete'),

    # Checkout Log Routes
    path('on-loan/', views.on_loan_dashboard, name='on_loan_dashboard'),
    path('overdue-report/', views.overdue_items_report, name='overdue_report'),
    path('low-stock-report/', views.low_stock_report, name='low_stock_report'),
    path('check-in/<int:log_id>/', views.check_in_page, name='check_in_page'),
    path('check-in/<int:log_id>/process/', views.process_check_in, name='process_check_in'),


    # Checkout Routes
    path('checkout/', views.checkout_find_student, name='checkout_find_student'),
    path('checkout/session/<int:student_id>/', views.checkout_session, name='checkout_session'),
    path('checkout/session/<int:student_id>/remove/<int:item_id>/', views.checkout_remove_item, name='checkout_remove_item'),
    path('checkout/session/<int:student_id>/update/<int:item_id>/', views.checkout_update_item_quantity, name='checkout_update_item_quantity'),
]
