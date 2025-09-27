# sherlock-python/inventory/admin.py

from django.contrib import admin
from .models import Section, Space, Item, PrintQueue, PrintQueueItem

admin.site.register(Section)
admin.site.register(Space)
admin.site.register(Item)
admin.site.register(PrintQueue)
admin.site.register(PrintQueueItem)