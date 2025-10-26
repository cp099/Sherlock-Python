# sherlock-python/inventory/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Max, F, Count
from django.db.models.functions import TruncDay
from django.contrib.auth.models import User


from .models import Section, Space, Item, PrintQueue, PrintQueueItem, SearchEntry, Student, CheckoutLog, CheckInLog, ItemLog, UserProfile
from .forms import SectionForm, SpaceForm, ItemForm, StudentForm, StockAdjustmentForm, UserUpdateForm, UserRoleForm
from .decorators import admin_required

import hashlib
import base64
from datetime import timedelta

def homepage(request):
    """
    Acts as a router for the root URL.
    - If the user is logged in, it redirects them to the main dashboard.
    - If the user is not logged in, it shows the public landing page.
    """
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    
    return render(request, 'inventory/landing_page.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inventory:section_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def universal_lookup(request):
    """
    Receives a scanned code and redirects to the appropriate
    Item, Space, or Section detail page.
    """
    code = request.GET.get('code', '').strip()
    
    if not code:
        messages.error(request, "No code was provided to look up.")
        return redirect('homepage')

    try:
        if code.isdigit() and len(code) >= 12:
            item = Item.objects.get(barcode=code[:12])
            messages.success(request, f"Found Item: {item.name}")
            return redirect(item.get_absolute_url())

        if code.startswith('SHERLOCK;'):
            parts = code.split(';')
            section_code_str = next((p.split(':')[1] for p in parts if p.startswith('SECTIONCODE:')), None)
            space_code_str = next((p.split(':')[1] for p in parts if p.startswith('SPACECODE:')), None)

            if section_code_str:
                section_code = int(section_code_str)
                if space_code_str: 
                    space_code = int(space_code_str)
                    space = get_object_or_404(Space, section__section_code=section_code, space_code=space_code)
                    messages.success(request, f"Found Space: {space.name}")
                    return redirect(space.get_absolute_url())
                else: 
                    section = get_object_or_404(Section, section_code=section_code)
                    messages.success(request, f"Found Section: {section.name}")
                    return redirect(section.get_absolute_url())
        
        messages.error(request, f"Could not find any Item, Section, or Space matching the code.")
        return redirect('homepage')

    except (Item.DoesNotExist, Section.DoesNotExist, Space.DoesNotExist):
        messages.error(request, f"Could not find any Item, Section, or Space matching the code.")
        return redirect('homepage')

@login_required
def sitemap(request):
    """
    Renders the sitemap page, which provides a complete overview and
    quick links to all major parts of the application.
    """
    return render(request, 'inventory/sitemap.html')

@login_required
def dashboard(request):
    now = timezone.now()
    today = now.date()
    one_week_ago = today - timedelta(days=6)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    three_days_from_now = now + timedelta(days=3)

    total_items_on_loan = CheckoutLog.objects.filter(return_date__isnull=True).aggregate(total=Sum('quantity'))['total'] or 0
    overdue_items_count = CheckoutLog.objects.filter(return_date__isnull=True, due_date__lt=now).count()
    low_stock_items_count = Item.objects.filter(quantity__lte=5).count()
    new_students_count = Student.objects.filter(created_at__gte=start_of_month).count()

    recently_checked_out = CheckoutLog.objects.filter(checkout_date__gte=now.replace(hour=0, minute=0), return_date__isnull=True).select_related('item', 'student').order_by('-checkout_date')[:5]
    items_due_soon = CheckoutLog.objects.filter(return_date__isnull=True, due_date__gte=now, due_date__lte=three_days_from_now).select_related('item', 'student').order_by('due_date')[:5]

    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    loan_activity_qs = CheckoutLog.objects.filter(checkout_date__date__gte=one_week_ago).annotate(day=TruncDay('checkout_date')).values('day').annotate(count=Count('id')).order_by('day')
    loan_activity_dict = {entry['day'].date(): entry['count'] for entry in loan_activity_qs}
    loan_activity_data = [loan_activity_dict.get(day, 0) for day in days]
    loan_activity_labels = [day.strftime("%a") for day in days] 

    popular_items_qs = CheckoutLog.objects.values('item__name').annotate(count=Count('item')).order_by('-count')[:5]
    popular_items_labels = [item['item__name'] for item in popular_items_qs]
    popular_items_data = [item['count'] for item in popular_items_qs]
    
    context = {
        'total_items_on_loan': total_items_on_loan,
        'overdue_items_count': overdue_items_count,
        'low_stock_items_count': low_stock_items_count,
        'new_students_count': new_students_count,
        'recently_checked_out': recently_checked_out,
        'items_due_soon': items_due_soon,
        'loan_activity_labels': loan_activity_labels,
        'loan_activity_data': loan_activity_data,
        'popular_items_labels': popular_items_labels,
        'popular_items_data': popular_items_data,
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
def inventory_browser(request):
    """
    Displays the main inventory browser page with the initial list of all sections.
    """
    sections = Section.objects.all().order_by('name')
    context = {
        'sections': sections,
    }
    return render(request, 'inventory/inventory_browser.html', context)


@login_required
def section_detail(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    context = {'section': section}
    return render(request, 'inventory/section_detail.html', context)

@login_required
def section_create(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save()
            return redirect('inventory:section_detail', section_code=section.section_code)
    else:
        last_section = Section.objects.all().aggregate(max_code=Max('section_code'))
        next_code = (last_section['max_code'] or 0) + 1
        form = SectionForm(initial={'section_code': next_code})
    
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
@admin_required
def section_delete(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    if request.method == 'POST':
        section.delete()
        return redirect('inventory:inventory_browser')
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

@login_required
def space_detail(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    context = {'section': section, 'space': space}
    return render(request, 'inventory/space_detail.html', context)

@login_required
@login_required
def space_create(request, section_code):
    section = get_object_or_404(Section, section_code=section_code)
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            space = form.save()
            return redirect('inventory:space_detail', section_code=space.section.section_code, space_code=space.space_code)
    else:
        last_space = Space.objects.filter(section=section).aggregate(max_code=Max('space_code'))
        next_code = (last_space['max_code'] or 0) + 1
        form = SpaceForm(initial={'section': section, 'space_code': next_code})
    
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
@admin_required
def space_delete(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    if request.method == 'POST':
        space.delete()
        return redirect('inventory:inventory_browser')
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


@login_required
def item_detail(request, section_code, space_code, item_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    item = get_object_or_404(Item, space=space, item_code=item_code)
    
    item_logs = ItemLog.objects.filter(item=item).order_by('-timestamp')
    
    item_loan_history = CheckoutLog.objects.filter(item=item).select_related('student').order_by('-checkout_date')

    item_logs = ItemLog.objects.filter(item=item).order_by('-timestamp')
    inv_filter_type = request.GET.get('inv_filter', '')
    if inv_filter_type == 'week':
        item_logs = item_logs.filter(timestamp__gte=timezone.now() - timedelta(days=7))
    elif inv_filter_type == 'month':
        item_logs = item_logs.filter(timestamp__gte=timezone.now() - timedelta(days=30))
    elif inv_filter_type == 'year':
        item_logs = item_logs.filter(timestamp__gte=timezone.now() - timedelta(days=365))
    elif inv_filter_type == 'custom':
        start_date = request.GET.get('inv_start_date')
        end_date = request.GET.get('inv_end_date')
        if start_date and end_date:
            item_logs = item_logs.filter(timestamp__range=[start_date, end_date])

    context = {
        'section': section,
        'space': space,
        'item': item,
        'item_logs': item_logs,
        'item_loan_history': item_loan_history,
    }
    return render(request, 'inventory/item_detail.html', context)

@login_required
def item_create(request, section_code, space_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect(item.get_absolute_url())
    else:
        last_item = Item.objects.filter(space=space).aggregate(max_code=Max('item_code'))
        next_code = (last_item['max_code'] or 0) + 1
        
        form = ItemForm(initial={'space': space, 'item_code': next_code})
    
    context = {
        'form': form,
        'section': section,
        'space': space,
    }
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
@admin_required
def item_delete(request, section_code, space_code, item_code):
    section = get_object_or_404(Section, section_code=section_code)
    space = get_object_or_404(Space, section=section, space_code=space_code)
    item = get_object_or_404(Item, space=space, item_code=item_code)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory:inventory_browser')
    return redirect('inventory:item_detail', section_code=section.section_code, space_code=space.space_code, item_code=item.item_code)

@login_required
def adjust_stock(request, section_code, space_code, item_code, action):
    item = get_object_or_404(Item,
        space__section__section_code=section_code,
        space__space_code=space_code,
        item_code=item_code
    )

    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            
            if action in ['RECEIVED', 'CORR_ADD']:
                item.quantity += quantity
                quantity_change = quantity
            elif action in ['DAMAGED', 'LOST', 'CORR_SUB']:
                if quantity > item.quantity:
                    messages.error(request, f"Cannot remove {quantity} units. Only {item.quantity} are in stock.")
                    return redirect(item.get_absolute_url())
                item.quantity -= quantity
                quantity_change = -quantity
            else:
                messages.error(request, "Invalid stock adjustment action.")
                return redirect(item.get_absolute_url())

            item.save()

            # Create the permanent log entry
            ItemLog.objects.create(
                item=item,
                user=request.user,
                action=action,
                quantity_change=quantity_change,
                notes=notes
            )
            
            messages.success(request, "Stock quantity has been updated successfully.")
            return redirect(item.get_absolute_url())
    else:
        form = StockAdjustmentForm()

    action_titles = {
        'RECEIVED': 'Receive New Stock for',
        'DAMAGED': 'Report Damaged Stock for',
        'LOST': 'Report Lost Stock for',
        'CORR_ADD': 'Make a Positive Stock Correction for',
        'CORR_SUB': 'Make a Negative Stock Correction for',
    }
    
    context = {
        'form': form,
        'item': item,
        'page_title': action_titles.get(action, 'Adjust Stock for')
    }
    return render(request, 'inventory/adjust_stock_form.html', context)

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

@login_required
def student_list(request):
    students_query = Student.objects.all().order_by('name')

    distinct_classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')

    selected_class = request.GET.get('class_filter', '')
    if selected_class:
        students_query = students_query.filter(student_class=selected_class)

    context = {
        'students': students_query,
        'distinct_classes': distinct_classes,
        'selected_class': selected_class,
    }
    return render(request, 'inventory/student_list.html', context)

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    items_on_loan = CheckoutLog.objects.filter(
        student=student,
        return_date__isnull=True
    ).select_related('item').order_by('-checkout_date')

    # This is the new query: it fetches individual return logs instead of closed loans.
    return_history = CheckInLog.objects.filter(
        checkout_log__student=student
    ).select_related('checkout_log__item').order_by('-return_date')

    context = {
        'student': student,
        'items_on_loan': items_on_loan,
        'return_history': return_history, # We now pass the new queryset to the template
    }
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
@admin_required
def student_delete(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('inventory:student_list')
    return redirect('inventory:student_detail', student_id=student.id)

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

@login_required
def live_unified_student_search(request):
    """
    Handles HTMX requests for the student search on the unified search page.
    Returns only the table rows with the results.
    """
    student_query = request.GET.get('student_query', '').strip()
    student_results = None
    if len(student_query) >= 1: 
        student_results = Student.objects.filter(
            Q(name__icontains=student_query) | Q(admission_number__icontains=student_query)
        ).order_by('student_class', 'name')

    context = {
        'student_results': student_results,
        'student_query': student_query,
    }
    return render(request, 'inventory/partials/unified_student_search_results.html', context)

@login_required
def live_unified_item_search(request):
    """
    Handles HTMX requests for the item search on the unified search page.
    This is the CORRECTED, working version.
    """
    item_query = request.GET.get('item_query', '').strip()
    item_results = None
    if len(item_query) >= 1:
        search_entries = SearchEntry.objects.filter(
            name__icontains=item_query
        ).select_related('content_type')
        item_results = search_entries
    
    context = {
        'item_results': item_results,
        'item_query': item_query,
    }
    return render(request, 'inventory/partials/unified_item_search_results.html', context)

@login_required
def search_index(request):
    """
    This view now ONLY renders the main search page.
    All the search logic is handled by the live search views.
    """
    context = {
        'item_query': '',
        'student_query': '',
        'item_results': None,
        'student_results': None,
    }
    return render(request, 'inventory/search_index.html', context)

@login_required
def live_student_search(request):
    """
    This view is specifically for HTMX requests. It returns a partial
    HTML snippet of the student search results.
    """
    query = request.GET.get('query', '').strip()
    student_results = None
    if len(query) >= 2: 
        student_results = Student.objects.filter(
            Q(name__icontains=query) | Q(admission_number__icontains=query)
        ).order_by('name')
    
    context = {'student_results': student_results}
    return render(request, 'inventory/partials/student_search_results.html', context)

@login_required
def live_item_search(request, student_id):
    query = request.GET.get('query', '').strip()
    item_results = None
    if len(query) >= 1:
        item_results = Item.objects.filter(
            Q(name__icontains=query) | Q(barcode__startswith=query)
        ).annotate(
            on_loan_qty=Sum('checkout_logs__quantity', filter=Q(checkout_logs__return_date__isnull=True))
        ).filter(
            Q(on_loan_qty__isnull=True) | Q(quantity__gt=F('on_loan_qty') + F('buffer_quantity'))
        ).distinct()[:5]

    context = {
        'item_results': item_results,
        'student_id': student_id,
        'query': query
    }
    return render(request, 'inventory/partials/item_search_results.html', context)

@login_required
def checkout_find_student(request):
    query = request.POST.get('query', '').strip()
    student_results = None

    if request.method == 'POST' and query:
        student_results = Student.objects.filter(
            Q(name__icontains=query) | Q(admission_number__icontains=query)
        ).order_by('name')

        if student_results.count() == 1:
            student = student_results.first()
            if 'checkout_items' in request.session:
                del request.session['checkout_items']
            return redirect('inventory:checkout_session', student_id=student.id)
        
        elif student_results.count() == 0:
            messages.error(request, f"No student found matching '{query}'.")

    context = {
        'student_results': student_results,
    }
    return render(request, 'inventory/checkout_find_student.html', context)

@login_required
def checkout_session(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    checkout_items = request.session.get('checkout_items', {})

    items_in_session_details = []
    total_units_in_session = 0
    if checkout_items:
        item_ids = checkout_items.keys()
        items = Item.objects.filter(id__in=item_ids)
        for item in items:
            quantity = checkout_items.get(str(item.id))
            total_units_in_session += quantity
            items_in_session_details.append({'item': item, 'quantity': quantity})

    if request.method == 'POST':
        item_to_add = None
        quantity_to_add = 1
        query = ''

        if 'add_item_from_scan' in request.POST:
            query = request.POST.get('barcode', '').strip()
        elif 'add_item' in request.POST:
            query = request.POST.get('query', '').strip()

        if query:
            if query.isdigit() and len(query) >= 12:
                try:
                    section_code = int(query[0:4])
                    space_code = int(query[4:8])
                    item_code = int(query[8:12])
                    item_to_add = Item.objects.get(space__section__section_code=section_code, space__space_code=space_code, item_code=item_code)
                except (Item.DoesNotExist, ValueError):
                    pass
            
            if not item_to_add:
                results = Item.objects.filter(name__icontains=query)
                if results.count() == 1:
                    item_to_add = results.first()
                elif results.count() > 1:
                    messages.error(request, f"Multiple items found for '{query}'. Please be more specific or use the barcode.")
            
            if item_to_add:
                current_in_session = checkout_items.get(str(item_to_add.id), 0)
                requested_total = current_in_session + quantity_to_add
                if requested_total > item_to_add.available_quantity:
                    messages.error(request, f"Not enough stock for '{item_to_add.name}'. Available to lend: {item_to_add.available_quantity}")
                else:
                    checkout_items[str(item_to_add.id)] = requested_total
                    request.session['checkout_items'] = checkout_items
                    messages.success(request, f"Added 1 x '{item_to_add.name}' to the list.")
            else:
                messages.error(request, f"ERROR: No item found matching '{query}'.")

        elif 'complete_checkout' in request.POST:
            if not checkout_items:
                messages.error(request, "Cannot complete checkout with no items.")
            else:
                notes = request.POST.get('notes', '')
                due_date_option = request.POST.get('due_date_option')
                final_due_date = None

                if due_date_option == 'days':
                    try:
                        days = int(request.POST.get('days_to_return', 0))
                        if days > 0:
                            future_date = timezone.now().date() + timedelta(days=days)
                            final_due_date = timezone.make_aware(datetime.combine(future_date, datetime.min.time())).replace(hour=14)
                    except (ValueError, TypeError):
                         messages.error(request, "Invalid number of days.")
                
                elif due_date_option == 'date':
                    try:
                        due_date_str = request.POST.get('return_date')
                        if due_date_str:
                            final_due_date = timezone.make_aware(datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M'))
                    except (ValueError, TypeError):
                        messages.error(request, "Invalid date/time format.")
                
                if final_due_date and final_due_date < timezone.now():
                    messages.error(request, "The return date and time cannot be in the past.")
                    final_due_date = None 
                
                if final_due_date:
                    for item_id, quantity in checkout_items.items():
                        item = Item.objects.get(id=item_id)
                        CheckoutLog.objects.create(
                            item=item, 
                            student=student, 
                            due_date=final_due_date, 
                            quantity=quantity,
                            notes=notes 
                        )
                    del request.session['checkout_items']
                    messages.success(request, f"Checkout complete! {total_units_in_session} items have been loaned to {student.name}.")
                    return redirect('inventory:student_detail', student_id=student.id)
                elif not messages.get_messages(request):
                    messages.error(request, "Please specify a valid return date or number of days.")

        return redirect('inventory:checkout_session', student_id=student.id)

    context = {
        'student': student,
        'items_in_session': items_in_session_details,
        'total_units_in_session': total_units_in_session,
    }
    return render(request, 'inventory/checkout_session.html', context)

@login_required
def checkout_remove_item(request, student_id, item_id):
    if request.method == 'POST':
        checkout_items = request.session.get('checkout_items', {})
        if str(item_id) in checkout_items:
            del checkout_items[str(item_id)]
            request.session['checkout_items'] = checkout_items
            messages.info(request, "Item removed from the list.")
    return redirect('inventory:checkout_session', student_id=student_id)

@login_required
def checkout_update_item_quantity(request, student_id, item_id):
    if request.method == 'POST':
        checkout_items = request.session.get('checkout_items', {})
        item_id_str = str(item_id)
        
        try:
            new_quantity = int(request.POST.get('quantity', 0))
            if new_quantity <= 0:
                if item_id_str in checkout_items:
                    del checkout_items[item_id_str]
                    messages.info(request, "Item removed from the list.")
            else:
                item = Item.objects.get(id=item_id)
                current_in_session = checkout_items.get(item_id_str, 0)
                max_allowable = item.available_quantity + current_in_session
                
                if new_quantity > max_allowable:
                    messages.error(request, f"Not enough stock for '{item.name}'. Max available to lend: {max_allowable}")
                else:
                    checkout_items[item_id_str] = new_quantity
                    messages.success(request, f"Updated quantity for '{item.name}'.")

            request.session['checkout_items'] = checkout_items

        except (ValueError, Item.DoesNotExist):
            messages.error(request, "Invalid item or quantity.")

    return redirect('inventory:checkout_session', student_id=student_id)

@login_required
def on_loan_dashboard(request):
    """
    Displays a list of all items currently checked out.
    This is the main hub for managing loaned items.
    """
    on_loan_logs = CheckoutLog.objects.filter(
        return_date__isnull=True
    ).select_related('item', 'student').order_by('due_date')

    context = {
        'on_loan_logs': on_loan_logs,
    }
    return render(request, 'inventory/on_loan_dashboard.html', context)

@login_required
def overdue_items_report(request):
    """
    Displays a dedicated report of only items that are past their due date.
    """
    overdue_logs = CheckoutLog.objects.filter(
        return_date__isnull=True,
        due_date__lt=timezone.now() 
    ).select_related('item', 'student').order_by('due_date')

    context = {
        'overdue_logs': overdue_logs,
    }
    return render(request, 'inventory/overdue_report.html', context)

@login_required
def low_stock_report(request):
    """
    Displays a report of all items with a quantity of 5 or less,
    ordered by their section and space for easy location.
    """
    low_stock_items = Item.objects.filter(
        quantity__lte=5
    ).select_related('space__section').order_by('space__section__name', 'space__name', 'name')

    context = {
        'low_stock_items': low_stock_items,
    }
    return render(request, 'inventory/low_stock_report.html', context)

@login_required
def check_in_page(request, log_id):
    """
    Displays the details of a loan and the form for returning a quantity.
    """
    log_entry = get_object_or_404(CheckoutLog, id=log_id, return_date__isnull=True)
    quantity_still_on_loan = log_entry.quantity - log_entry.quantity_returned_so_far
    
    context = {
        'log_entry': log_entry,
        'quantity_still_on_loan': quantity_still_on_loan,
    }
    return render(request, 'inventory/check_in_page.html', context)

@login_required
def process_check_in(request, log_id):
    """
    Handles the logic of a partial or full return, including item condition.
    If an item is returned as 'Damaged', its total quantity in the main
    inventory is permanently reduced.
    """
    if request.method == 'POST':
        log_entry = get_object_or_404(CheckoutLog, id=log_id, return_date__isnull=True)
        
        try:
            quantity_to_return = int(request.POST.get('quantity_returned', 0))
            return_condition = request.POST.get('condition', CheckInLog.Condition.OK)
            quantity_still_on_loan = log_entry.quantity_still_on_loan

            if return_condition not in CheckInLog.Condition.values:
                messages.error(request, "Invalid return condition specified.")
            elif quantity_to_return <= 0:
                messages.error(request, "Quantity to return must be a positive number.")
            elif quantity_to_return > quantity_still_on_loan:
                messages.error(request, f"Cannot return {quantity_to_return}. Only {quantity_still_on_loan} units are on loan.")
            else:
                CheckInLog.objects.create(
                    checkout_log=log_entry,
                    quantity_returned=quantity_to_return,
                    condition=return_condition
                )
                
                if return_condition == CheckInLog.Condition.DAMAGED:
                    item = log_entry.item
                    item.quantity -= quantity_to_return
                    item.save()
                    
                    ItemLog.objects.create(
                        item=item,
                        user=request.user,
                        action=ItemLog.Action.DAMAGED,
                        quantity_change=-quantity_to_return,
                        notes=f"Reported damaged during return by student {log_entry.student.name}."
                    )
                    messages.warning(request, f"{quantity_to_return} x '{item.name}' were marked as damaged and removed from total stock.")
                
                log_entry.refresh_from_db()

                messages.success(request, f"Successfully processed return of {quantity_to_return} x '{log_entry.item.name}'.")

                if log_entry.quantity_still_on_loan == 0:
                    log_entry.return_date = timezone.now()
                    log_entry.save()
                    messages.info(request, "This loan is now fully returned and closed.")
                    return redirect('inventory:on_loan_dashboard')
                
                return redirect('inventory:check_in_page', log_id=log_id)

        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity entered.")
            
    return redirect('inventory:check_in_page', log_id=log_id)

@login_required
def get_spaces_for_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    spaces = Space.objects.filter(section=section).order_by('name')
    context = {'spaces': spaces}
    return render(request, 'inventory/partials/_browser_spaces_column.html', context)

@login_required
def get_items_for_space(request, space_id):
    space = get_object_or_404(Space, id=space_id)
    items = Item.objects.filter(space=space).order_by('name')
    context = {'items': items}
    return render(request, 'inventory/partials/_browser_items_column.html', context)

@login_required
def get_preview(request, model_name, object_id):
    if model_name == 'section':
        instance = get_object_or_404(Section, id=object_id)
    elif model_name == 'space':
        instance = get_object_or_404(Space, id=object_id)
    elif model_name == 'item':
        instance = get_object_or_404(Item, id=object_id)
    else:
        return HttpResponse("Invalid model type.", status=400)
        
    context = {
        'instance': instance,
        'model_name': model_name,
    }
    return render(request, 'inventory/partials/_browser_preview_pane.html', context)

@login_required
def my_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('inventory:my_profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'inventory/my_profile.html', context)


@login_required
@admin_required
def team_management(request):
    if request.user.profile.role != 'ADMIN':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('inventory:dashboard')
    
    users = UserProfile.objects.exclude(user=request.user).order_by('user__username')
    form = UserRoleForm()
    
    context = {'users': users, 'form': form}
    return render(request, 'inventory/team_management.html', context)

@login_required
@admin_required
def update_user_role(request, user_id):
    """Handles the form submission for changing a user's role."""
    if request.user.profile.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('inventory:team_management')

    if request.method == 'POST':
        user_to_update = get_object_or_404(UserProfile, id=user_id)
        new_role = request.POST.get('role')
        if new_role in UserProfile.Role.values:
            user_to_update.role = new_role
            user_to_update.save()
            messages.success(request, f"Successfully updated role for {user_to_update.user.username}.")
        else:
            messages.error(request, "Invalid role selected.")
            
    return redirect('inventory:team_management')

@login_required
@admin_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Successfully created user '{user.username}'. You can now assign them a role.")
            return redirect('inventory:team_management')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'inventory/create_user.html', context)

def custom_page_not_found_view(request, exception):
    """
    Custom view to render the 404.html template.
    """
    return render(request, "404.html", status=404)