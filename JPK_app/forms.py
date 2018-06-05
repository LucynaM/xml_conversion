from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import LoadedFile


class LoadedFileForm(forms.ModelForm):
    class Meta:
        model = LoadedFile
        fields = ['path', 'type']
        labels = {
            'path': 'path',
            'type': 'type'
        }


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def clean(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        if password1 != password2:
            raise ValidationError
        return self.cleaned_data

class LogInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())