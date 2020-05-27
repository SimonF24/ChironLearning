from django.test import TestCase
from django.urls import reverse

class LoginPageTests(TestCase):
    def test_page_found(self):
        '''
        Tests that the page is found
        '''
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)

    def test_navigation_bar(self):
        '''
        Tests that the navigation bar is part of the response
        '''
        response = self.client.get(reverse('main:login'))
        self.assertContains(response, "About")
        self.assertContains(response, "Contact Us")
        self.assertContains(response, "Sign In")
        self.assertContains(response, "Sign Up")

    def test_login_form(self):
        '''
        Tests that the Login Form is part of the response (specifically the headers of the login form)
        '''
        response = self.client.get(reverse('main:login'))
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Email')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Log In')
        self.assertContains(response, 'Forgot Password?')

    def test_register_form(self):
        '''
        Tests that the Registration Form is part of the response
        '''
        response = self.client.get(reverse('main:login'))
        self.assertContains(response, 'Register')
        self.assertContains(response, 'Email')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'This will be publicly visible')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Confirm Password')
        self.assertContains(response, 'Register Now')

    def test_footer(self):
        '''
        Tests that the footer is part of the response
        '''
        response = self.client.get(reverse('main:login'))
        self.assertContains(response, "&copy; Simon Fraser 2018. All Rights Reserved.")
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Terms of Use")

class RegisterPageTests(TestCase):
    def test_page_found(self):
        '''
        Tests that the page redirects as expected
        '''
        response = self.client.get(reverse('main:register'))
        self.assertEqual(response.status_code, 302)
