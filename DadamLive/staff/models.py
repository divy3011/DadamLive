from django.db import models

# Create your models here.
class FilePurposes(models.Model):
    file=models.FileField(upload_to='uploads/', null=True, blank=True)
