# sherlock-python/inventory/views.py

from django.http import HttpResponse

# This view is for your root path / homepage
def homepage(request):
    return HttpResponse("<h1>Sherlock Homepage</h1><p>Welcome to the new system!</p>")

# ==================================
# Search Views
# ==================================
def search_index(request):
    return HttpResponse("Search Results Page")

# ==================================
# Print Shop Views
# ==================================
def print_shop_index(request):
    return HttpResponse("Print Shop - Your Current Queue")

def print_page(request):
    return HttpResponse("This is the final page formatted for printing.")

def change_print_item_quantity(request, item_id):
    return HttpResponse(f"Changing quantity for print queue item {item_id}")

def delete_print_item(request, item_id):
    return HttpResponse(f"Deleting print queue item {item_id}")

# ==================================
# Section Views (CRUD)
# ==================================
def section_list(request):
    return HttpResponse("List of all Sections")

def section_detail(request, section_code):
    return HttpResponse(f"Detail view for Section {section_code}")

def section_create(request):
    return HttpResponse("Form to create a new Section")

def section_update(request, section_code):
    return HttpResponse(f"Form to update Section {section_code}")

def section_delete(request, section_code):
    return HttpResponse(f"Confirm deletion of Section {section_code}")

def section_add_to_queue(request, section_code):
    return HttpResponse(f"Adding Section {section_code} to print queue")

# ==================================
# Space Views (CRUD)
# ==================================
def space_detail(request, section_code, space_code):
    return HttpResponse(f"Detail view for Space {space_code} in Section {section_code}")

def space_create(request, section_code):
    return HttpResponse(f"Form to create a new Space in Section {section_code}")

def space_update(request, section_code, space_code):
    return HttpResponse(f"Form to update Space {space_code}")

def space_delete(request, section_code, space_code):
    return HttpResponse(f"Confirm deletion of Space {space_code}")

def space_add_to_queue(request, section_code, space_code):
    return HttpResponse(f"Adding Space {space_code} to print queue")

# ==================================
# Item Views (CRUD)
# ==================================
def item_detail(request, section_code, space_code, item_code):
    return HttpResponse(f"Detail view for Item {item_code}")

def item_create(request, section_code, space_code):
    return HttpResponse(f"Form to create a new Item in Space {space_code}")

def item_update(request, section_code, space_code, item_code):
    return HttpResponse(f"Form to update Item {item_code}")

def item_delete(request, section_code, space_code, item_code):
    return HttpResponse(f"Confirm deletion of Item {item_code}")

def item_add_small_to_queue(request, section_code, space_code, item_code):
    return HttpResponse(f"Adding small label for Item {item_code} to queue")

def item_add_large_to_queue(request, section_code, space_code, item_code):
    return HttpResponse(f"Adding large label for Item {item_code} to queue")