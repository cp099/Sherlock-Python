# sherlock-python/inventory/templatetags/inventory_extras.py
from django import template

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
            text, 
            flags=re.IGNORECASE
        )
        return mark_safe(highlighted_text)
    return text