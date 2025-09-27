# sherlock-python/inventory/forms.py

from django import forms
from .models import Section
from .models import Space
from .models import Item
from .models import Student

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
        labels = {
            'space_code': 'Space Code',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_code', 'name', 'description', 'buffer_quantity']
        labels = {
            'item_code': 'Item Code',
            'buffer_quantity': 'Buffer Stock Quantity',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['admission_number', 'name', 'student_class', 'section']
        labels = {
            'admission_number': 'Admission Number',
            'student_class': 'Class',
        }

class StockAdjustmentForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity Change",
        widget=forms.NumberInput(attrs={'autofocus': True})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Please provide a reason for this stock change (e.g., 'New order received', 'Dropped and damaged')."
    )