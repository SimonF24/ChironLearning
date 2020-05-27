from django.urls import path

from . import views

app_name = 'pages'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('about', views.AboutPageView.as_view(), name='about'),
    path('contact', views.ContactPageView, name='contact'),
    path('contact/submit', views.SubmitContactForm, name="contact-submit"),
    path('contact/success', views.ContactSuccessView.as_view(), name="contact-success"),
    path('terms-of-use', views.TermsOfUseView.as_view(), name="terms-of-use"),
    path('privacy-policy', views.PrivacyPolicyView.as_view(), name="privacy-policy"),
]