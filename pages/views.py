from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic.base import TemplateView

from .forms import ContactForm

class HomePageView(TemplateView):

    template_name = "pages/home.html"

class AboutPageView(TemplateView):

    template_name = "pages/about.html"

def ContactPageView(request):
    context = {
        'contactform':ContactForm,
    }
    return render(request, 'pages/contact.html', context)

def SubmitContactForm(request):
    if request.method == "POST":
    
        contact_form = ContactForm(request.POST)
    
        if contact_form.is_valid():
            
            name = contact_form.cleaned_data['name']
            contact_email = contact_form.cleaned_data['contact_email']
            subject = contact_form.cleaned_data['subject']
            message = contact_form.cleaned_data['message']
        
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [settings.DEFAULT_TO_EMAIL]

            template_context = {
                'user':name,
                'email':contact_email,
                'message':message,
            }

            contact_message = get_template('contact_message_template.html').render(template_context)

            send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

            return redirect('pages:contact-success')
        else:
            messages.error(request, 'Something went wrong, please try again')
            return redirect('pages:contact')
    else:
        return redirect('pages:contact')

class ContactSuccessView(TemplateView):

    template_name = "pages/contact-success.html"

class TermsOfUseView(TemplateView):

    template_name = "pages/terms-of-use.html"

class PrivacyPolicyView(TemplateView):

    template_name = "pages/privacy-policy.html"
