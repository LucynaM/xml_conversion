from django import forms
from .models import LoadedFile, JPKFile, JPKTag, JPKTable


class LoadedFileForm(forms.ModelForm):
    class Meta:
        model = LoadedFile
        fields = ['path', ]


class JPKFileForm(forms.ModelForm):
    class Meta:
        model = JPKFile
        fields = '__all__'


class JPKTableForm(forms.ModelForm):
    class Meta:
        model = JPKTable
        fields = ['name', ]


class JPKTagForm(forms.ModelForm):
    class Meta:
        model = JPKTag
        fields = ['name', 'type',]
