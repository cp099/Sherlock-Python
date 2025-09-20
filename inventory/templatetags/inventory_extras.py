# sherlock-python/inventory/templatetags/inventory_extras.py
import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def highlight(text, query):
    if query:
        # Use regex to find all occurrences of the query, case-insensitively
        # and wrap them in a <strong> tag.
        highlighted_text = re.sub(
            f'({re.escape(query)})', 
            r'<strong>\1</strong>', 
            str(text),  # Ensure text is a string
            flags=re.IGNORECASE
        )
        return mark_safe(highlighted_text)
    return text

@register.filter
def model_name(value):
    """Returns the name of the model for an object."""
    return value.__class__.__name__