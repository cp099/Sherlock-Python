# sherlock-python/inventory/forms.py

from django import forms
from .models import Section
from .models import Space
from .models import Item

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['section_code', 'name', 'description']
        labels = {
            'section_code': 'Section Code',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = ['space_code', 'name', 'description']
        # The 'section' field is excluded because it will be set automatically
        # from the URL, not from user input.
        labels = {
            'space_code': 'Space Code',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_code', 'name', 'description', 'quantity']
        # The 'space' field is excluded as it's set from the URL.
        labels = {
            'item_code': 'Item Code',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }