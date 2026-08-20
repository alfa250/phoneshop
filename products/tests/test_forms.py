from django.test import TestCase
from products.forms import CheckoutForm, RegisterForm
from django.contrib.auth.models import User

class CheckoutFormTest(TestCase):

    def test_valid_checkout_form(self):
        form = CheckoutForm(data = {
              'full_name':'Aondofa Alfred',
              'phone': '08133606306',
              'address': '123 main street',
              'city': 'Abuja',
              'state': 'FCT'

        })

        self.assertTrue(form.is_valid())

    def test_checkout_form_rejects_missing_required_fields(self):
        form = CheckoutForm(data = {})


        self.assertFalse(form.is_valid())

    def test_checkout_form_reports_required_field_errors(self):
        form = CheckoutForm(data = {})


        self.assertFalse(form.is_valid())


        self.assertIn('full_name', form.errors)
        self.assertIn('phone', form.errors)
        self.assertIn('address', form.errors)
        self.assertIn('city', form.errors)
        self.assertIn('state', form.errors)
        
class RegisterFormTest(TestCase):

    def test_valid_registration_form(self):
        form = RegisterForm(data = {
            'username': 'testuser',
            'email':'test@example.com',
            'password1':'strongpassword123',
            'password2': 'strongpassword123'
        })

        self.assertTrue(form.is_valid())

    def test_registration_rejects_existing_email(self):
        User.objects.create_user(
            username = 'existinguser',
            email = 'test@example.com',
            password = 'strongpassword123'
        )

        form = RegisterForm(data= {
            'username':'newuser',
            'email': 'test@example.com',
            'password1':'strongpassowrd123',
            'passowrd2':'strongpassword123'
        })

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)



    def test_registration_rejects_email_with_different_case(self):
        User.objects.create_user(
            username = 'existinguser',
            email = 'test@example.com',
            password = 'strongpassword123'
        )

        form = RegisterForm(data = {
            'username':'newuser',
            'email':'TEST@EXAMPLE.COM',
            'password1':'strongpassword123',
            'password2':'strongpassword123'
        })

















        