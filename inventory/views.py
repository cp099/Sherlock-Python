# sherlock-python/inventory/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Section, Space, Item, PrintQueue, PrintQueueItem, SearchEntry, Student
from .forms import SectionForm, SpaceForm, ItemForm, StudentForm

import hashlib
import base64

def landing_page(request):
    """
    Shows the public landing page to logged-out users.
    Redirects logged-in users directly to the main sections list.
    """
    if request.user.is_authenticated:
        return redirect('inventory:section_list') # Redirect logged-in users
    
    # Show the new landing page to guests
    return render(request, 'inventory/landing_page.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in directly after successful registration
            login(request, user)
            return redirect('inventory:section_list') # Redirect to the main sections page
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# ==================================
# SECTION VIEWS
# ==================================
@login_required
def section_list(request):
    sections = Section.objects.all().order_by('section_code')
    context = {'sections': sections}
    return render(request, 'inventory/section_list.html', context)

@login_required
def section_detail(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    context = {'section': section}
    return render(request, 'inventory/section_detail.html', context)

# ... [All other Section, Space, and Item views remain here, unchanged] ...
# ... I am omitting them for brevity, but they should be in your file ...

@login_required
def section_create(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save()
            return redirect('inventory:section_detail', section_code=section.section_code)
    else:
        form = SectionForm()
    context = {'form': form}
    return render(request, 'inventory/section_form.html', context)

@login_required
def section_update(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            return redirect('inventory:section_detail', section_code=section.section_code)
    else:
        form = SectionForm(instance=section)
    context = {'form': form, 'section': section}
    return render(request, 'inventory/section_form.html', context)

@login_required
def section_delete(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    if request.method == 'POST':
        section.delete()
        return redirect('inventory:section_list')
    return redirect('inventory:section_detail', section_code=section.section_code)

@login_required
def section_add_to_queue(request, section_code):
    if request.method == 'POST':
        section = get_object_or_404(Section, section_code=section_code)
        print_queue, _ = PrintQueue.objects.get_or_create(user=request.user)
        print_name = f"Section Label for {section.name}"
        item_hash = hashlib.sha256(print_name.encode('utf-8')).hexdigest()
        qr_svg = section.generate_qr_code_svg()
        qr_base64 = base64.b64encode(qr_svg.encode('utf-8')).decode('utf-8')
        print_content = render_to_string('inventory/section_label.svg', {'section': section, 'qr_code_base64': qr_base64})
        queue_item, created = PrintQueueItem.objects.get_or_create(
            print_queue=print_queue,
            item_hash=item_hash,
            defaults={'name': print_name, 'quantity': 1, 'print_content': print_content}
        )
        if not created:
            queue_item.quantity += 1
            queue_item.save()
    return redirect('inventory:section_detail', section_code=section.section_code)

# ==================================
# SPACE VIEWS
# ==================================
@login_required
def space_list(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    spaces = Space.objects.filter(section=section).order_by('space_code')
    context = {'section': section, 'spaces': spaces}
    return render(request, 'inventory/space_list.html', context)

@login_required
def space_detail(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    context = {'section': section, 'space': space}
    return render(request, 'inventory/space_detail.html', context)

@login_required
def space_create(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            space = form.save(commit=False)
            space.section = section
            space.save()
            return redirect('inventory:space_detail', section_code=section.section_code, space_code=space.space_code)
    else:
        form = SpaceForm()
    context = {'form': form, 'section': section}
    return render(request, 'inventory/space_form.html', context)

@login_required
def space_update(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    if request.method == 'POST':
        form = SpaceForm(request.POST, instance=space)
        if form.is_valid():
            form.save()
            return redirect('inventory:space_detail', section_code=section.section_code, space_code=space.space_code)
    else:
        form = SpaceForm(instance=space)
    context = {'form': form, 'section': section, 'space': space}
    return render(request, 'inventory/space_form.html', context)

@login_required
def space_delete(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    if request.method == 'POST':
        space.delete()
        return redirect('inventory:space_list', section_code=section.section_code)
    return redirect('inventory:space_detail', section_code=section.section_code, space_code=space.space_code)

@login_required
def space_add_to_queue(request, section_code, space_code):
    if request.method == 'POST':
        section = get_object_or_404(Section, section_code=section_code)
        space = get_object_or_404(Space, section=section, space_code=space_code)
        print_queue, _ = PrintQueue.objects.get_or_create(user=request.user)
        print_name = f"Space Label for {space.name} of section {section.name}"
        item_hash = hashlib.sha256(print_name.encode('utf-8')).hexdigest()
        qr_svg = space.generate_qr_code_svg()
        qr_base64 = base64.b64encode(qr_svg.encode('utf-8')).decode('utf-8')
        print_content = render_to_string('inventory/space_label.svg', {'space': space, 'qr_code_base64': qr_base64})
        queue_item, created = PrintQueueItem.objects.get_or_create(
            print_queue=print_queue,
            item_hash=item_hash,
            defaults={'name': print_name, 'quantity': 1, 'print_content': print_content}
        )
        if not created:
            queue_item.quantity += 1
            queue_item.save()
    return redirect('inventory:space_detail', section_code=section.section_code, space_code=space.space_code)

# ==================================
# ITEM VIEWS
# ==================================
@login_required
def item_list(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    items = Item.objects.filter(space=space).order_by('item_code')
    context = {'section': section, 'space': space, 'items': items}
    return render(request, 'inventory/item_list.html', context)

@login_required
def item_detail(request, section_code, space_code, item_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    item = get_object_or_404(Item, space=space, item_code=item_code)
    context = {'section': section, 'space': space, 'item': item}
    return render(request, 'inventory/item_detail.html', context)

@login_required
def item_create(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.space = space
            item.save()
            return redirect('inventory:item_detail', section_code=section.section_code, space_code=space.space_code, item_code=item.item_code)
    else:
        form = ItemForm()
    context = {'form': form, 'section': section, 'space': space}
    return render(request, 'inventory/item_form.html', context)

@login_required
def item_update(request, section_code, space_code, item_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    item = get_object_or_404(Item, space=space, item_code=item_code)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory:item_detail', section_code=section.section_code, space_code=space.space_code, item_code=item.item_code)
    else:
        form = ItemForm(instance=item)
    context = {'form': form, 'section': section, 'space': space, 'item': item}
    return render(request, 'inventory/item_form.html', context)

@login_required
def item_delete(request, section_code, space_code, item_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    item = get_object_or_404(Item, space=space, item_code=item_code)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory:item_list', section_code=section.section_code, space_code=space.space_code)
    return redirect('inventory:item_detail', section_code=section.section_code, space_code=space.space_code, item_code=item.item_code)

def _add_item_to_queue(request, item, label_type):
    print_queue, _ = PrintQueue.objects.get_or_create(user=request.user)
    print_name = f"{label_type.capitalize()} Item Label for {item.name}"
    item_hash = hashlib.sha256(print_name.encode('utf-8')).hexdigest()
    template_name = f'inventory/item_label_{label_type}.svg'
    barcode_svg = item.generate_barcode_svg()
    barcode_base64 = base64.b64encode(barcode_svg.encode('utf-8')).decode('utf-8')
    print_content = render_to_string(template_name, {'item': item, 'barcode_base64': barcode_base64})
    queue_item, created = PrintQueueItem.objects.get_or_create(
        print_queue=print_queue,
        item_hash=item_hash,
        defaults={'name': print_name, 'quantity': 1, 'print_content': print_content}
    )
    if not created:
        queue_item.quantity += 1
        queue_item.save()

@login_required
def item_add_small_to_queue(request, section_code, space_code, item_code):
    if request.method == 'POST':
        space = get_object_or_404(Space, section__section_code=section_code, space_code=space_code)
        item = get_object_or_404(Item, space=space, item_code=item_code)
        _add_item_to_queue(request, item, 'small')
    return redirect('inventory:item_detail', section_code=section_code, space_code=space_code, item_code=item_code)

@login_required
def item_add_large_to_queue(request, section_code, space_code, item_code):
    if request.method == 'POST':
        space = get_object_or_404(Space, section__section_code=section_code, space_code=space_code)
        item = get_object_or_404(Item, space=space, item_code=item_code)
        _add_item_to_queue(request, item, 'large')
    return redirect('inventory:item_detail', section_code=section_code, space_code=space_code, item_code=item_code)

# ==================================
# NEW STUDENT VIEWS (CRUD)
# ==================================
@login_required
def student_list(request):
    students = Student.objects.all().order_by('name')
    context = {'students': students}
    return render(request, 'inventory/student_list.html', context)

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    # We will enhance this later with loan history
    context = {'student': student}
    return render(request, 'inventory/student_detail.html', context)

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            return redirect('inventory:student_detail', student_id=student.id)
    else:
        form = StudentForm()
    context = {'form': form}
    return render(request, 'inventory/student_form.html', context)

@login_required
def student_update(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('inventory:student_detail', student_id=student.id)
    else:
        form = StudentForm(instance=student)
    context = {'form': form, 'student': student}
    return render(request, 'inventory/student_form.html', context)

@login_required
def student_delete(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('inventory:student_list')
    # If not POST, just redirect back to the detail page.
    return redirect('inventory:student_detail', student_id=student.id)

# ==================================
# Print Shop & Queue Views
# ==================================
@login_required
def print_queue(request):
    queue, _ = PrintQueue.objects.get_or_create(user=request.user)
    context = {'queue': queue}
    return render(request, 'inventory/print_queue.html', context)

@login_required
def clear_print_queue(request):
    if request.method == 'POST':
        queue, _ = PrintQueue.objects.get_or_create(user=request.user)
        queue.delete()
    return redirect('inventory:print_queue')

@login_required
def change_print_item_quantity(request, item_id):
    if request.method == 'POST':
        queue_item = get_object_or_404(PrintQueueItem, id=item_id, print_queue__user=request.user)
        new_quantity = request.POST.get('quantity')
        if new_quantity and int(new_quantity) > 0:
            queue_item.quantity = new_quantity
            queue_item.save()
    return redirect('inventory:print_queue')

@login_required
def delete_print_item(request, item_id):
    if request.method == 'POST':
        queue_item = get_object_or_404(PrintQueueItem, id=item_id, print_queue__user=request.user)
        queue_item.delete()
    return redirect('inventory:print_queue')

@login_required
def print_shop_index(request):
    queue, _ = PrintQueue.objects.get_or_create(user=request.user)
    if not queue.items.exists():
        return redirect('inventory:print_queue')
    return render(request, 'inventory/print_shop_index.html')

@login_required
def print_page(request):
    queue, _ = PrintQueue.objects.get_or_create(user=request.user)
    context = {
        'items': queue.items.all(),
        'generation_time': datetime.now().strftime("on %d/%m/%Y at %H:%M")
    }
    return render(request, 'inventory/print_page.html', context)

# ==================================
# Search View
# ==================================
@login_required
def search_index(request):
    query = request.GET.get('query')
    search_entries = None

    if query:
        search_entries = SearchEntry.objects.filter(
            name__icontains=query
        ).select_related('content_type')

    context = {
        'query': query,
        'search_entries': search_entries,
    }
    return render(request, 'inventory/search_index.html', context)