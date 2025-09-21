# In your Django app's models.py file

from django.db import models
from django.conf import settings # To link to the User model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum

# Python libraries we will need to install:
# pip install python-barcode qrcode

import barcode
from barcode.writer import SVGWriter
import qrcode
import qrcode.image.svg

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True # This makes it a reusable base, not a real table

# ==============================================================================
# 1. SECTION MODEL
# Replicates your Section model for high-level locations (e.g., "Main Lab").
# ==============================================================================
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
    
    # This connects this model to the SearchEntry model
    search_entry = GenericRelation('SearchEntry', object_id_field='object_id', content_type_field='content_type')

    def __str__(self):
        return f"{self.name} (Section: {self.section_code})"
    
    def get_absolute_url(self):
        # This will create URLs like /sections/1001/
        return reverse('inventory:section_detail', kwargs={'section_code': self.section_code})

    def generate_qr_code_svg(self):
        """Generates the QR code SVG content, replicating the Rails logic."""
        # Pad the name and description exactly as in the original code
        padded_name = (self.name + '*' * 50)[:50]
        padded_desc = (self.description + '*' * 100)[:100]
        
        qr_data = (
            f"SHERLOCK;SECTIONCODE:{str(self.section_code).zfill(4)};;"
            f"RESTOREDATA;NAME:{padded_name};DESCRIPTION:{padded_desc};;"
        )
        
        # Generate SVG QR code
        img = qrcode.make(qr_data, image_factory=qrcode.image.svg.SvgPathImage)
        return img.to_string(encoding='unicode')

# ==============================================================================
# 2. SPACE MODEL
# Replicates your Space model for specific locations within a Section (e.g., "Workbench A").
# ==============================================================================
class Space(TimeStampedModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='spaces')
    space_code = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ],
        help_text="A 4-digit code for this space, unique within its section (1-9999)."
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    
    search_entry = GenericRelation('SearchEntry')

    class Meta:
        # Ensures that space_code is unique for a given section
        unique_together = ('section', 'space_code')

    def __str__(self):
        return f"{self.name} (Space: {self.space_code} in {self.section.name})"
        
    def get_absolute_url(self):
        # This will create URLs like /sections/1001/spaces/2001/
        return reverse('inventory:space_detail', kwargs={'section_code': self.section.section_code, 'space_code': self.space_code})

    def generate_qr_code_svg(self):
        """Generates the QR code SVG content, replicating the Rails logic."""
        padded_name = (self.name + '*' * 50)[:50]
        padded_desc = (self.description + '*' * 100)[:100]
        
        qr_data = (
            f"SHERLOCK;SECTIONCODE:{str(self.section.section_code).zfill(4)};"
            f"SPACECODE:{str(self.space_code).zfill(4)};;"
            f"RESTOREDATA;NAME:{padded_name};DESCRIPTION:{padded_desc};;"
        )
        
        img = qrcode.make(qr_data, image_factory=qrcode.image.svg.SvgPathImage)
        return img.to_string(encoding='unicode')

# ==============================================================================
# 3. ITEM MODEL
# Replicates your core Item model for inventory.
# ==============================================================================
class Item(TimeStampedModel):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='items')
    item_code = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ],
        help_text="A 4-digit code for this item, unique within its space (1-9999)."
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        default=1,
        help_text="Total quantity of this item in inventory."
    )
    
    buffer_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Minimum quantity to keep in stock. This amount cannot be checked out."
    )

    search_entry = GenericRelation('SearchEntry')

    class Meta:
        # Ensures that item_code is unique for a given space
        unique_together = ('space', 'item_code')

    def __str__(self):
        return f"{self.name} (Qty: {self.quantity})"
    
    @property
    def checked_out_quantity(self):
        """Calculates the total quantity of this item currently on loan."""
        checked_out = self.checkout_logs.filter(return_date__isnull=True).aggregate(total=Sum('quantity'))['total']
        return checked_out or 0
    
    @property
    def available_quantity(self):
        """Calculates the quantity available for checkout (total - checked out - buffer)."""
        return self.quantity - self.checked_out_quantity - self.buffer_quantity

    def __str__(self):
        return f"{self.name} (Item: {self.item_code} in {self.space.name})"
    
    barcode = models.CharField(max_length=12, blank=True, editable=False)
    
    search_entry = GenericRelation('SearchEntry')

    class Meta:
        unique_together = ('space', 'item_code')

    def __str__(self):
        return f"{self.name} (Qty: {self.quantity})"
    
    def save(self, *args, **kwargs):
        # Auto-generate the 12-digit barcode string
        self.barcode = (
            f"{self.space.section.section_code:04d}"
            f"{self.space.space_code:04d}"
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
        """Generates the EAN-13 barcode SVG content."""
        EAN = barcode.get_barcode_class('ean13')
        
        # Construct the 12-digit code for the EAN-13 barcode
        section_str = str(self.space.section.section_code).zfill(4)
        space_str = str(self.space.space_code).zfill(4)
        item_str = str(self.item_code).zfill(4)
        barcode_value = f"{section_str}{space_str}{item_str}"

        # The python-barcode library automatically calculates the 13th checksum digit
        ean_barcode = EAN(barcode_value, writer=SVGWriter())
        
        # Decode the bytes into a UTF-8 string before returning
        return ean_barcode.render().decode('utf-8')
    
    @property
    def is_on_loan(self):
        """Returns the CheckoutLog if the item is currently on loan, otherwise None."""
        return self.checkout_logs.filter(return_date__isnull=True).first()
    


# ==============================================================================
# 4. PRINT QUEUE MODELS
# Replicates the print queue system.
# ==============================================================================
class PrintQueue(models.Model):
    # A OneToOneField ensures each user gets exactly one print queue
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Print Queue for {self.user.username}"

class PrintQueueItem(models.Model):
    print_queue = models.ForeignKey(PrintQueue, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # TextField is better for storing potentially large SVG/HTML content
    print_content = models.TextField()
    item_hash = models.CharField(max_length=64) # For SHA256 hashes

    def __str__(self):
        return f"{self.quantity}x {self.name} in {self.print_queue}"


# ==============================================================================
# 5. SEARCH ENTRY MODEL (Polymorphic)
# Replicates the polymorphic Searchable relationship using Django's ContentType framework.
# ==============================================================================
class SearchEntry(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=500) # Store the generated URL

    # These three fields create the generic (polymorphic) relationship
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    searchable_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        # Ensures an object (like a specific item) can only have one search entry
        unique_together = ('content_type', 'object_id')

    def __str__(self):
        return f"Search entry for '{self.name}'"
    

# ==============================================================================
# PHASE 2: LENDING SYSTEM MODELS
# ==============================================================================

class Student(TimeStampedModel):
    """A record for a student who can borrow items."""
    admission_number = models.CharField(max_length=50, unique=True, help_text="Unique student admission or ID number.")
    name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=50, verbose_name="Class")
    section = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.admission_number})"
    
    def save(self, *args, **kwargs):
        # Convert fields to uppercase before saving
        self.name = self.name.upper()
        self.admission_number = self.admission_number.upper()
        self.student_class = self.student_class.upper()
        self.section = self.section.upper()
        
        # Call the original save method to save the object to the database
        super().save(*args, **kwargs)

class CheckoutLog(models.Model):
    """A record of an item being checked out by a student."""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="checkout_logs")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="checkout_logs")
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True, help_text="This is set when the item is returned.")
    due_date = models.DateTimeField(help_text="The date and time the item is expected to be returned.")
    
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
        # This will only be True if both conditions are met.
        return self.return_date is None and self.due_date < timezone.now()
    
class CheckInLog(models.Model):
    """A record of a partial or full return for a specific checkout."""
    checkout_log = models.ForeignKey(CheckoutLog, on_delete=models.CASCADE, related_name="check_in_logs")
    quantity_returned = models.PositiveIntegerField()
    return_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity_returned} units of {self.checkout_log.item.name} returned on {self.return_date.strftime('%Y-%m-%d')}"


# ==============================================================================
# NEW INVENTORY AUDIT LOG MODEL
# ==============================================================================

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
    
    # We use a standard IntegerField to allow for negative numbers (e.g., -1 for a damaged item)
    quantity_change = models.IntegerField()
    
    notes = models.TextField(blank=True, help_text="Reason for the stock change.")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Example: "+10 of MQ2 Sensor: Received New Stock by admin"
        sign = '+' if self.quantity_change > 0 else ''
        return f"{sign}{self.quantity_change} of {self.item.name}: {self.get_action_display()} by {self.user.username if self.user else 'Unknown'}"