from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class LoadedFile(models.Model):
    path = models.FileField(upload_to='files')
    date_creation = models.DateTimeField(auto_now_add=True)

    @property
    def name(self):
        return '{}'.format(self.path.name)
    
    @property
    def new_name(self):
        return '{}'.format(self.path.name[6:-4])



class JPKFile(models.Model):
    """Tags structure - file"""
    name = models.CharField(max_length=125, verbose_name='nazwa pliku')
    raw_ns = models.CharField(max_length=125, verbose_name='namespace')

    def __str__(self):
        return self.name

    @property
    def ns(self):
        return '{{{}}}'.format(self.raw_ns)

class JPKTable(models.Model):
    """Tags structure - table"""
    name = models.CharField(max_length=64, verbose_name='tabela')
    file = models.ForeignKey(JPKFile, on_delete=models.CASCADE, verbose_name='plik', related_name='tables')

    def __str__(self):
        return '{}: {}'.format(self.file, self.name)


TYPES = (
    ("str", "znakowy"),
    ("date", "data"),
    ("value", "kwotowy"),
    ("num", "liczbowy"),
)

class JPKTag(models.Model):
    """Tags structure - tag"""
    name = models.CharField(max_length=64, verbose_name='tag')
    type = models.CharField(choices=TYPES, default="str", max_length=16, verbose_name='typ')
    table = models.ForeignKey(JPKTable, on_delete=models.CASCADE, verbose_name='tabela', related_name='tags')




