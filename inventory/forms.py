# sherlock-python/inventory/forms.py

from django import forms
from .models import Section
from .models import Space
from .models import Item
from .models import Student
from .models import UserProfile
from django.contrib.auth.models import User

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
        fields = ['section', 'space_code', 'name', 'description']
        labels = {
            'space_code': 'Space Code',
            'section': 'Parent Section'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['space_code'].disabled = True

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['space', 'item_code', 'name', 'description', 'quantity', 'buffer_quantity']
        labels = {
            'item_code': 'Item Code',
            'space': 'Parent Space',
            'buffer_quantity': 'Buffer Stock Quantity',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['item_code'].disabled = True

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

class UserUpdateForm(forms.ModelForm):
    """Form for users to update their own basic information."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserRoleForm(forms.ModelForm):
    """Form for Admins to update a user's role."""
    class Meta:
        model = UserProfile
        fields = ['role']