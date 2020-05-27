from django.test import TestCase

from django.urls import reverse

class HomePageTests(TestCase):
    def test_found(self):
        '''
        Tests that the home page is found
        '''
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)

    def test_navigation_bar(self):
        '''
        Tests that the navigation bar is part of the response
        '''
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, "About")
        self.assertContains(response, "Contact Us")
        self.assertContains(response, "Sign In")
        self.assertContains(response, "Sign Up")

    def test_home_header(self):
        '''
        Tests that the header is included in the response
        '''
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, "Welcome to the Future of Online Learning")

    def test_icons_grid(self):
        ''' 
        Tests that the icon grid is included in the response
        '''
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, "Connect with Others")
        self.assertContains(response, "Personalized Learning")
        self.assertContains(response, "Mobile Ready")

    def test_image_showcase(self):
        '''
        Tests that that image showcase is included in the response
        '''
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, "Active Learning")
        self.assertContains(response, "Intelligent Content Recommendations")
        self.assertContains(response, "Invest in Yourself")

    def test_call_to_action(self):
        '''
        Tests that the call to action is part of the response
        '''
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, "Ready to get started? Sign up now.")

    def test_footer(self):
        '''
        Tests that the footer is part of the response
        '''
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, "&copy; Simon Fraser 2018. All Rights Reserved.")
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Terms of Use")

class AboutPageTests(TestCase):
    def test_found(self):
        '''
        Tests that the about page is found
        '''
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)

    def test_navigation_bar(self):
        '''
        Tests that the navigation bar is part of the response
        '''
        response = self.client.get(reverse('pages:about'))
        self.assertContains(response, "About")
        self.assertContains(response, "Contact Us")
        self.assertContains(response, "Sign In")
        self.assertContains(response, "Sign Up")

    def test_about_header(self):
        '''
        Tests that the header is part of the response
        '''
        response = self.client.get(reverse('pages:about'))
        self.assertContains(response, "About Us")

    def test_sections(self):
        '''
        Tests that each section is part of the response
        '''
        response = self.client.get(reverse('pages:about'))
        self.assertContains(response, "Our Mission")
        self.assertContains(response, "Our Story")

    def test_footer(self):
        '''
        Tests that the footer is part of the response
        '''
        response = self.client.get(reverse('pages:about'))
        self.assertContains(response, "&copy; Simon Fraser 2018. All Rights Reserved.")
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Terms of Use")

class ContactPageTests(TestCase):
    def test_navigation_bar(self):
        '''
        Tests that the navigation bar is part of the response
        '''
        response = self.client.get(reverse('pages:contact'))
        self.assertContains(response, "About")
        self.assertContains(response, "Contact Us")
        self.assertContains(response, "Sign In")
        self.assertContains(response, "Sign Up")

    def test_found(self):
        '''
        Tests that the contact page is found
        '''
        response = self.client.get(reverse('pages:contact'))
        self.assertEqual(response.status_code, 200)

    def test_header(self):
        '''
        Tests that the header is part of the response
        '''
        response = self.client.get(reverse('pages:contact'))
        self.assertContains(response, "Contact Us")
        self.assertContains(response, "Please fill out the form below")

    def test_footer(self):
        '''
        Tests that the footer is part of the response
        '''
        response = self.client.get(reverse('pages:contact'))
        self.assertContains(response, "&copy; Simon Fraser 2018. All Rights Reserved.")
        self.assertContains(response, "Privacy Policy")
        self.assertContains(response, "Terms of Use")

