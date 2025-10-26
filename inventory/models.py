# sherlock-python/inventory/models.py

from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.db.models.signals import post_save

import barcode
from barcode.writer import SVGWriter
import qrcode
import qrcode.image.svg

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True 

class Section(TimeStampedModel):
    section_code = models.PositiveIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ],
        help_text="A unique 4-digit code for this section (1-9999)."
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    
    search_entry = GenericRelation('SearchEntry', object_id_field='object_id', content_type_field='content_type')

    def __str__(self):
        return f"{self.name} (Section: {self.section_code})"
    
    def get_absolute_url(self):
        return reverse('inventory:section_detail', kwargs={'section_code': self.section_code})

    def generate_qr_code_svg(self):
        """Generates the QR code SVG content, replicating the Rails logic."""
        padded_name = (self.name + '*' * 50)[:50]
        padded_desc = (self.description + '*' * 100)[:100]
        
        qr_data = (
            f"SHERLOCK;SECTIONCODE:{str(self.section_code).zfill(4)};;"
            f"RESTOREDATA;NAME:{padded_name};DESCRIPTION:{padded_desc};;"
        )
        
        img = qrcode.make(qr_data, image_factory=qrcode.image.svg.SvgPathImage)
        return img.to_string(encoding='unicode')

class Space(TimeStampedModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='spaces')
    space_code = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        help_text="A 4-digit code for this space, unique within its section (1-9999)."
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    
    original_section_code = models.PositiveIntegerField(editable=False, null=True)
    
    search_entry = GenericRelation('SearchEntry')

    class Meta:
        unique_together = ('section', 'space_code')

    def __str__(self):
        return f"{self.name} (in {self.section.name})"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.original_section_code = self.section.section_code
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('inventory:space_detail', kwargs={'section_code': self.section.section_code, 'space_code': self.space_code})

    def generate_qr_code_svg(self):
        """Generates the QR code SVG content using the permanent original code."""
        padded_name = (self.name + '*' * 50)[:50]
        padded_desc = (self.description + '*' * 100)[:100]
        

        qr_data = (
            f"SHERLOCK;SECTIONCODE:{str(self.original_section_code).zfill(4)};"
            f"SPACECODE:{str(self.space_code).zfill(4)};;"
            f"RESTOREDATA;NAME:{padded_name};DESCRIPTION:{padded_desc};;"
        )
        
        img = qrcode.make(qr_data, image_factory=qrcode.image.svg.SvgPathImage)
        return img.to_string(encoding='unicode')

class Item(TimeStampedModel):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='items')
    item_code = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        help_text="A 4-digit code for this item, unique within its space (1-9999)."
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Total quantity of this item in inventory."
    )
    buffer_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Minimum quantity to keep in stock. This amount cannot be checked out."
    )
    barcode = models.CharField(max_length=12, blank=True, editable=False)
    original_section_code = models.PositiveIntegerField(editable=False, null=True)
    original_space_code = models.PositiveIntegerField(editable=False, null=True)
    search_entry = GenericRelation('SearchEntry', object_id_field='object_id', content_type_field='content_type')

    class Meta:
        unique_together = ('space', 'item_code')

    def __str__(self):
        return f"{self.name} (Qty: {self.quantity})"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.original_section_code = self.space.section.section_code
            self.original_space_code = self.space.space_code
        
        self.barcode = (
            f"{self.original_section_code:04d}"
            f"{self.original_space_code:04d}"
            f"{self.item_code:04d}"
        )
        super().save(*args, **kwargs)

        search_entry, created = SearchEntry.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        )
        search_entry.name = self.name
        search_entry.url = self.get_absolute_url()
        search_entry.save()
    
    def get_absolute_url(self):
        return reverse('inventory:item_detail', kwargs={
            'section_code': self.space.section.section_code,
            'space_code': self.space.space_code,
            'item_code': self.item_code
        })

    def generate_barcode_svg(self):
        """Generates the EAN-13 barcode SVG content using the permanent barcode field."""
        EAN = barcode.get_barcode_class('ean13')
        ean_barcode = EAN(self.barcode, writer=SVGWriter())
        return ean_barcode.render().decode('utf-8')
    
    @property
    def checked_out_quantity(self):
        """Calculates the total quantity of this item currently on loan."""
        checked_out = self.checkout_logs.filter(return_date__isnull=True).aggregate(total=Sum('quantity'))['total']
        return checked_out or 0
    
    @property
    def available_quantity(self):
        """Calculates the quantity available for checkout (total - checked out - buffer)."""
        return self.quantity - self.checked_out_quantity - self.buffer_quantity
    
class PrintQueue(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Print Queue for {self.user.username}"

class PrintQueueItem(models.Model):
    print_queue = models.ForeignKey(PrintQueue, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    print_content = models.TextField()
    item_hash = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.quantity}x {self.name} in {self.print_queue}"

class SearchEntry(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=500) 

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    searchable_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('content_type', 'object_id')

    def __str__(self):
        return f"Search entry for '{self.name}'"
    
class Student(TimeStampedModel):
    """A record for a student who can borrow items."""
    admission_number = models.CharField(max_length=50, unique=True, help_text="Unique student admission or ID number.")
    name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=50, verbose_name="Class")
    section = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.admission_number})"
    
    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        self.admission_number = self.admission_number.upper()
        self.student_class = self.student_class.upper()
        self.section = self.section.upper()
        
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    """Extends the default Django User model to include a role."""
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MEMBER = 'MEMBER', 'Member'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)

class CheckoutLog(models.Model):
    """A record of an item being checked out by a student."""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="checkout_logs")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="checkout_logs")
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True, help_text="This is set when the item is returned.")
    due_date = models.DateTimeField(help_text="The date and time the item is expected to be returned.")
    notes = models.TextField(blank=True, help_text="Reason or notes for this checkout.")
    
    quantity = models.PositiveIntegerField(default=1, help_text="The number of items checked out in this transaction.")

    def __str__(self):
        status = "Returned" if self.return_date else "On Loan"
        return f"{self.item.name} to {self.student.name} ({status})"
    
    @property
    def quantity_returned_so_far(self):
        """Calculates the total quantity returned for this specific checkout log."""
        returned = self.check_in_logs.aggregate(total=Sum('quantity_returned'))['total']
        return returned or 0
    
    @property
    def quantity_still_on_loan(self):
        """Calculates the quantity still on loan for this checkout."""
        return self.quantity - self.quantity_returned_so_far
    
    @property
    def is_overdue(self):
        """Returns True if the item is not returned and the due date is in the past."""
        return self.return_date is None and self.due_date < timezone.now()
    
class CheckInLog(models.Model):
    """A record of a partial or full return for a specific checkout."""
    class Condition(models.TextChoices):
        OK = 'OK', 'OK'
        DAMAGED = 'DAMAGED', 'Damaged'

    checkout_log = models.ForeignKey(CheckoutLog, on_delete=models.CASCADE, related_name="check_in_logs")
    quantity_returned = models.PositiveIntegerField()
    return_date = models.DateTimeField(auto_now_add=True)
    
    condition = models.CharField(
        max_length=10, 
        choices=Condition.choices, 
        default=Condition.OK,
        help_text="The condition of the item upon return."
    )

    def __str__(self):
        return f"{self.quantity_returned} units of {self.checkout_log.item.name} returned on {self.return_date.strftime('%Y-%m-%d')} (Condition: {self.get_condition_display()})"

class ItemLog(models.Model):
    """A permanent record of a change in an item's stock quantity."""
    class Action(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Received New Stock'
        DAMAGED = 'DAMAGED', 'Reported Damaged'
        LOST = 'LOST', 'Reported Lost'
        CORRECTION_ADD = 'CORR_ADD', 'Manual Correction (Add)'
        CORRECTION_SUB = 'CORR_SUB', 'Manual Correction (Subtract)'

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="item_logs")
    action = models.CharField(max_length=10, choices=Action.choices)
    
    quantity_change = models.IntegerField()
    
    notes = models.TextField(blank=True, help_text="Reason for the stock change.")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = '+' if self.quantity_change > 0 else ''
        return f"{sign}{self.quantity_change} of {self.item.name}: {self.get_action_display()} by {self.user.username if self.user else 'Unknown'}"