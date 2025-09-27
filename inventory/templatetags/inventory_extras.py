# sherlock-python/inventory/templatetags/inventory_extras.py
import re
from django import template
from django.utils.safestring import mark_safe
from django.utils import timezone

register = template.Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def highlight(text, query):
    if query:
        highlighted_text = re.sub(
            f'({re.escape(query)})', 
            r'<strong>\1</strong>', 
            str(text),
            flags=re.IGNORECASE
        )
        return mark_safe(highlighted_text)
    return text

@register.filter
def model_name(value):
    """Returns the name of the model for an object."""
    return value.__class__.__name__

@register.filter
def days_until(due_date):
    """Calculates the number of days until a due date."""
    if not due_date:
        return ""
    today = timezone.now().date()
    delta = due_date.date() - today
    days = delta.days
    
    if days < 0:
        return "Overdue"
    elif days == 0:
        return "Due Today"
    elif days == 1:
        return "Due in 1 day"
    else:
        return f"Due in {days} days"
    
@register.filter
def urgency_tag(due_date):
    if not due_date:
        return ""
    days = (due_date.date() - timezone.now().date()).days
    
    if days < 0:
        return mark_safe('<span class="urgency-tag overdue">Overdue</span>')
    elif days == 0:
        return mark_safe('<span class="urgency-tag due-today">Due Today</span>')
    elif days == 1:
        return mark_safe('<span class="urgency-tag due-soon">Due Tomorrow</span>')
    else:
        return f"Due in {days} days"