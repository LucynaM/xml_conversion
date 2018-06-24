from django import forms
from .models import LoadedFile


class LoadedFileForm(forms.ModelForm):
    class Meta:
        model = LoadedFile
        fields = ['path', ]
