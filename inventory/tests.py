# sherlock-python/inventory/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import Section, Space, Item, Student, CheckoutLog, CheckInLog, ItemLog

class ModelTests(TestCase):
    """
    A suite of tests to verify the custom logic within our models.
    """
    def setUp(self):
        """Set up a common state for all model tests."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.student = Student.objects.create(name='Test Student', admission_number='T001', student_class='X', section='A')
        self.section = Section.objects.create(name='Test Section', section_code=1)
        self.space = Space.objects.create(name='Test Space', section=self.section, space_code=1)
        self.item = Item.objects.create(
            name='Test Item',
            space=self.space,
            item_code=1,
            quantity=20,
            buffer_quantity=5
        )

    def test_item_quantity_properties(self):
        """Test the quantity calculation properties of the Item model."""
        self.assertEqual(self.item.checked_out_quantity, 0)
        self.assertEqual(self.item.available_quantity, 15) 

        log = CheckoutLog.objects.create(item=self.item, student=self.student, quantity=8, due_date=timezone.now())
        self.assertEqual(self.item.checked_out_quantity, 8)
        self.assertEqual(self.item.available_quantity, 7) 

    def test_checkout_log_is_overdue(self):
        """Test the is_overdue property of the CheckoutLog model."""
        future_log = CheckoutLog.objects.create(item=self.item, student=self.student, quantity=1, due_date=timezone.now() + timedelta(days=1))
        self.assertFalse(future_log.is_overdue)

        past_log = CheckoutLog.objects.create(item=self.item, student=self.student, quantity=1, due_date=timezone.now() - timedelta(days=1))
        self.assertTrue(past_log.is_overdue)

        past_log.return_date = timezone.now()
        past_log.save()
        self.assertFalse(past_log.is_overdue)

    def test_checkout_log_partial_returns(self):
        """Test the quantity calculation properties of the CheckoutLog model."""
        log = CheckoutLog.objects.create(item=self.item, student=self.student, quantity=10, due_date=timezone.now())
        
        self.assertEqual(log.quantity_returned_so_far, 0)
        self.assertEqual(log.quantity_still_on_loan, 10)

        CheckInLog.objects.create(checkout_log=log, quantity_returned=4)
        self.assertEqual(log.quantity_returned_so_far, 4)
        self.assertEqual(log.quantity_still_on_loan, 6)

class ViewTests(TestCase):
    """
    A suite of tests to verify that all pages load correctly and are protected.
    """
    def setUp(self):
        """Set up a user and some data for view tests."""
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.section = Section.objects.create(name='Test Section', section_code=1)
        self.space = Space.objects.create(name='Test Space', section=self.section, space_code=1)
        self.item = Item.objects.create(name='Test Item', space=self.space, item_code=1, quantity=10)

    def test_all_pages_load_correctly(self):
        """Test that all main pages return a 200 OK status code for a logged-in user."""
        urls = [
            reverse('inventory:dashboard'),
            reverse('inventory:section_list'),
            reverse('inventory:section_detail', args=[self.section.section_code]),
            reverse('inventory:space_list', args=[self.section.section_code]),
            reverse('inventory:space_detail', args=[self.section.section_code, self.space.space_code]),
            reverse('inventory:item_list', args=[self.section.section_code, self.space.space_code]),
            reverse('inventory:item_detail', args=[self.section.section_code, self.space.space_code, self.item.item_code]),
            reverse('inventory:student_list'),
            reverse('inventory:on_loan_dashboard'),
            reverse('inventory:overdue_report'),
            reverse('inventory:search'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed to load page: {url}")

    def test_pages_redirect_if_not_logged_in(self):
        """Test that protected pages redirect to the login screen for an anonymous user."""
        self.client.logout()
        response = self.client.get(reverse('inventory:dashboard'))
        self.assertEqual(response.status_code, 302) 
        self.assertIn(reverse('login'), response.url)

class StockAdjustmentWorkflowTests(TestCase):
    """
    An end-to-end test for the full stock adjustment workflow.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.section = Section.objects.create(name='Test Section', section_code=1)
        self.space = Space.objects.create(name='Test Space', section=self.section, space_code=1)
        self.item = Item.objects.create(name='Test Item', space=self.space, item_code=1, quantity=10)

    def test_receive_stock_workflow(self):
        """Test the process of receiving new stock for an item."""
        self.assertEqual(Item.objects.get(id=self.item.id).quantity, 10)
        self.assertEqual(ItemLog.objects.count(), 0)

        url = reverse('inventory:adjust_stock', args=[self.section.section_code, self.space.space_code, self.item.item_code, 'RECEIVED'])
        
        response = self.client.post(url, {
            'quantity': '5',
            'notes': 'New shipment arrived'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.item.get_absolute_url())

        self.assertEqual(Item.objects.get(id=self.item.id).quantity, 15)
        self.assertEqual(ItemLog.objects.count(), 1)
        log = ItemLog.objects.first()
        self.assertEqual(log.action, 'RECEIVED')
        self.assertEqual(log.quantity_change, 5)
        self.assertEqual(log.notes, 'New shipment arrived')