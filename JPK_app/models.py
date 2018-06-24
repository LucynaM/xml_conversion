from django.db import models
from django.contrib.auth.models import User


class LoadedFile(models.Model):
    path = models.FileField(upload_to='files')
    date_creation = models.DateTimeField(auto_now_add=True)

    @property
    def name(self):
        return '{}'.format(self.path.name)
    
