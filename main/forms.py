from constrainedfilefield.fields import ConstrainedFileField
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import Concept, Resource, Topic

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label = _("Old password"),
        strip = False,
        widget = forms.PasswordInput(attrs={
            'autofocus': True, 
            'class':'form-control', 
            'placeholder':'Enter your old password'})
        )

    new_password1 = forms.CharField(
        label = _("New password"),
        widget = forms.PasswordInput(attrs={
            'class':'form-control', 
            'placeholder':'Enter your new password'}),
        strip = False,
        help_text = password_validation.password_validators_help_text_html(),
        )

    new_password2 = forms.CharField(
        label = _("Confirm New Password"),
        strip = False,
        widget = forms.PasswordInput(attrs={
            'class':'form-control', 
            'placeholder':'Enter your new password again'})
        )

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label = _("Email"),
        widget = forms.EmailInput(attrs={
            'class':'form-control', 
            'placeholder':'Enter the email address associated with your account'}),
        max_length = 254
        )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label = _("New password"),
        widget = forms.PasswordInput(attrs={
            'class':'form-control', 
            'placeholder':'Enter your new password'}),
        strip = False,
        help_text = password_validation.password_validators_help_text_html(),
        )
    new_password2 = forms.CharField(
        label = _("Confirm New password"),
        strip = False,
        widget = forms.PasswordInput(attrs={
            'class':'form-control', 
            'placeholder':'Enter your new password again'}),
        )

class LoginForm(forms.Form):
    email = forms.EmailField(
        label = _('Email'),
        widget = forms.EmailInput(attrs={
            'class':'form-control', 
            'placeholder':'Email Address'
        }))
    password = forms.CharField(
        label = _('Password'),
        strip = False, 
        widget = forms.PasswordInput(attrs={
            'class':'form-control', 
            'placeholder':'Password'}))

class RegisterForm(forms.Form):
    email = forms.EmailField(
        label = _('Email'),
        widget = forms.EmailInput(attrs={
            'class':'form-control', 
            'placeholder':'Email Address'})
        )
    username = forms.CharField(
        label = _('Username'),
        widget = forms.TextInput(attrs={
            'class':'form-control', 
            'placeholder':'Public Username'})
        )
    set_password = forms.CharField(
        label = _('Password'),
        widget = forms.PasswordInput(attrs={
            'class':'form-control', 
            'placeholder':'Password'})
        )
    confirm_password = forms.CharField(
        label = _('Confirm Password'),
        widget = forms.PasswordInput(attrs={
            'class':'form-control', 
            'placeholder':'Enter your password again'})
        )

class UploadForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('concept', 'creator', 'subject', 'title', 'topic', 'upload',)
        labels = {
            'concept':_('Concept'),
            'subject':_('Subject'),
            'title':_('Title'),
            'topic':_('Topic'),
            'upload':_('Your Video'),
        }
        widgets = {
            'concept':forms.Select(attrs={'class':'form-control'}),
            'creator':forms.HiddenInput(),
            'subject':forms.Select(attrs={'class':'form-control'}),
            'title':forms.TextInput(attrs={'class':'form-control',
                                           'placeholder':'Enter the title of your video'}),
            'topic':forms.Select(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['concept'].queryset = Concept.objects.none()
        self.fields['concept'].disabled = True
        self.fields['topic'].queryset = Topic.objects.none()
        self.fields['topic'].disabled = True

        if 'subject' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                self.fields['topic'].queryset = Topic.objects.filter(subject__id=subject_id).order_by('name')
                self.fields['topic'].disabled = False
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore and fallback to empty Topic queryset
        elif self.instance.pk:
            self.fields['topic'].queryset = self.instance.subject.topic_set.order_by('name')

        if 'topic' in self.data:
            try:
                topic_id = int(self.data.get('topic'))
                self.fields['concept'].queryset = Concept.objects.filter(topic__id=topic_id).order_by('name')
                self.fields['concept'].disabled = False
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore and fallback to empty Concept queryset
        elif self.instance.pk:
            self.fields['concept'].queryset = self.instance.topic.concept_set.order_by('name')

class UpdateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('creator', 'subject', 'title', 'topic')
        labels = {
            'concept':_('Concept'),
            'subject':_('Subject'),
            'title':_('Title'),
            'topic':_('Topic'),
        }
        widgets = {
            'concept':forms.Select(attrs={'class':'form-control'}),
            'subject':forms.Select(attrs={'class':'form-control'}),
            'title':forms.TextInput(attrs={'class':'form-control',
                                           'placeholder':'Enter the title of your video'}),
            'topic':forms.Select(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['concept'].queryset = Concept.objects.none()
        self.fields['concept'].disabled = True
        self.fields['topic'].queryset = Topic.objects.none()
        self.fields['topic'].disabled = True

        if 'subject' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                self.fields['topic'].queryset = Topic.objects.filter(subject__id=subject_id).order_by('name')
                self.fields['topic'].disabled = False
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore and fallback to empty Topic queryset
        elif self.instance.pk:
            self.fields['topic'].queryset = self.instance.subject.topic_set.order_by('name')

        if 'topic' in self.data:
            try:
                topic_id = int(self.data.get('topic'))
                self.fields['concept'].queryset = Concept.objects.filter(topic__id=topic_id).order_by('name')
                self.fields['concept'].disabled = False
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore and fallback to empty Concept queryset
        elif self.instance.pk:
            self.fields['concept'].queryset = self.instance.topic.concept_set.order_by('name')