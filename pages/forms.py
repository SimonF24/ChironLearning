from django import forms
from django.utils.translation import ugettext_lazy as _

class ContactForm(forms.Form):
    name = forms.CharField(
        label = _('Name:'),
        widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Your Name'}),
        max_length = 100
        )
    contact_email = forms.EmailField(
        label = _('Email:'),
        widget = forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email Address'})
        )
    subject = forms.ChoiceField(
        label = _('Subject:'),
        widget = forms.Select(attrs={'class':'form-control'}),
        choices=(('Feedback', 'Feedback'), ('Suggestion', 'Suggestion'),
                 ('Technical Difficulties', 'Technical Difficulties'), ('Other','Other'))
        )
    message = forms.CharField(
        label = _('Message:'),
        widget = forms.Textarea(attrs={'class':'form-control', 'placeholder':'Enter your message here'})
        )