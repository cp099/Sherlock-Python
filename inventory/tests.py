# sherlock-python/inventory/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import Section, Space, Item, Student, CheckoutLog, CheckInLog, ItemLog

# ==============================================================================
#  MODEL TESTS
# ==============================================================================

class ModelTests(TestCase):
    """Tests for custom logic within the application's models."""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.student = Student.objects.create(name='Test Student', admission_number='T001', student_class='X', section='A')
        cls.section = Section.objects.create(name='Test Section', section_code=1)
        cls.space = Space.objects.create(name='Test Space', section=cls.section, space_code=1, original_section_code=1)
        cls.item = Item.objects.create(
            name='Test Item',
            space=cls.space,
            item_code=1,
            quantity=20,
            buffer_quantity=5
        )

    def test_item_quantity_properties(self):
        """Test the quantity calculation properties of the Item model."""
        self.assertEqual(self.item.checked_out_quantity, 0)
        self.assertEqual(self.item.available_quantity, 15) 

        CheckoutLog.objects.create(item=self.item, student=self.student, quantity=8, due_date=timezone.now())
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
        log.refresh_from_db() 
        self.assertEqual(log.quantity_returned_so_far, 4)
        self.assertEqual(log.quantity_still_on_loan, 6)

# ==============================================================================
#  VIEW & WORKFLOW TESTS
# ==============================================================================

class ViewAndWorkflowTests(TestCase):
    """
    A suite of tests to verify that pages load, are protected, and that
    key user workflows function correctly from end-to-end.
    """
    def setUp(self):
        """Set up a logged-in client and base data for all view tests."""
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        
        self.section = Section.objects.create(name='Test Section', section_code=1)
        self.space = Space.objects.create(name='Test Space', section=self.section, space_code=1, original_section_code=1)
        self.item = Item.objects.create(name='Test Item', space=self.space, item_code=1, quantity=10)
        self.student = Student.objects.create(name='Test Student', admission_number='T001', student_class='X', section='A')

    def test_all_pages_load_correctly(self):
        """Test that all main pages return a 200 OK status code for a logged-in user."""
        urls = [
            reverse('inventory:dashboard'),
            reverse('inventory:inventory_browser'),
            reverse('inventory:section_detail', args=[self.section.section_code]),
            reverse('inventory:space_detail', args=[self.section.section_code, self.space.space_code]),
            reverse('inventory:item_detail', args=[self.section.section_code, self.space.space_code, self.item.item_code]),
            reverse('inventory:student_list'),
            reverse('inventory:student_detail', args=[self.student.id]),
            reverse('inventory:on_loan_dashboard'),
            reverse('inventory:overdue_report'),
            reverse('inventory:low_stock_report'),
            reverse('inventory:search'),
            reverse('inventory:print_queue'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed to load page: {url}")

    def test_pages_redirect_if_not_logged_in(self):
        """Test that a protected page redirects to the login screen for an anonymous user."""
        self.client.logout()
        response = self.client.get(reverse('inventory:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_receive_stock_workflow(self):
        """Test the end-to-end process of receiving new stock for an item."""
        self.assertEqual(Item.objects.get(id=self.item.id).quantity, 10)
        self.assertEqual(ItemLog.objects.count(), 0)

        url = reverse('inventory:adjust_stock', args=[self.section.section_code, self.space.space_code, self.item.item_code, 'RECEIVED'])
        response = self.client.post(url, {'quantity': '5', 'notes': 'New shipment arrived'})
        
        self.assertRedirects(response, self.item.get_absolute_url())
        self.assertEqual(Item.objects.get(id=self.item.id).quantity, 15)
        self.assertEqual(ItemLog.objects.count(), 1)
        log = ItemLog.objects.first()
        self.assertEqual(log.action, 'RECEIVED')
        self.assertEqual(log.quantity_change, 5)

    def test_full_checkout_and_return_workflow(self):
        """Test a complete checkout, check-in, and loan history workflow."""
        # 1. Start a checkout session for the student
        checkout_url = reverse('inventory:checkout_session', args=[self.student.id])
        session = self.client.session
        session['checkout_items'] = {str(self.item.id): 2} 
        session.save()

        # 2. Complete the checkout
        response = self.client.post(checkout_url, {
            'complete_checkout': 'true',
            'due_date_option': 'days',
            'days_to_return': '7',
            'notes': 'Project work',
        })
        self.assertRedirects(response, reverse('inventory:student_detail', args=[self.student.id]))

        # Verify the checkout log was created
        self.assertEqual(CheckoutLog.objects.count(), 1)
        log = CheckoutLog.objects.first()
        self.assertEqual(log.student, self.student)
        self.assertEqual(log.item, self.item)
        self.assertEqual(log.quantity, 2)
        self.assertIsNone(log.return_date)

        # 3. Process a partial return
        check_in_url = reverse('inventory:process_check_in', args=[log.id])
        response = self.client.post(check_in_url, {'quantity_returned': '1'})
        self.assertRedirects(response, reverse('inventory:check_in_page', args=[log.id]))

        # Verify the state after partial return
        log.refresh_from_db()
        self.assertEqual(log.quantity_still_on_loan, 1)
        self.assertIsNone(log.return_date) # Should still be on loan

        # 4. Process the final return
        response = self.client.post(check_in_url, {'quantity_returned': '1'})
        self.assertRedirects(response, reverse('inventory:on_loan_dashboard'))
        
        # Verify the loan is now closed
        log.refresh_from_db()
        self.assertEqual(log.quantity_still_on_loan, 0)
        self.assertIsNotNone(log.return_date)