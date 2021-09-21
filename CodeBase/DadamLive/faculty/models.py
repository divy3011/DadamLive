from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Course(models.Model):
    instructor=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    courseName=models.CharField(null=True, max_length=200)
    created_on=models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.courseName