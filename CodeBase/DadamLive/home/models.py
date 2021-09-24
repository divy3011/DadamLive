from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class UserType(models.Model):
    userType=models.CharField(max_length=20, null=True)
    userTypeCode=models.IntegerField(null=True)
    #For Student -  (645)
    #For Faculty -  (823)
    #For Staff -    (-872)
    #For TA -       (679)

    def __str__(self):
        return self.userType

class UserInformation(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    userType=models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return str(self.user)+str(self.userType)


class Student(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    userInformation=models.ForeignKey(UserInformation, on_delete=models.CASCADE, null=True, blank=True)
    image=models.ImageField(upload_to='post_images/', default="us_ma.png")

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class Faculty(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    userInformation=models.ForeignKey(UserInformation, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class Staff(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    userInformation=models.ForeignKey(UserInformation, on_delete=models.CASCADE, null=True, blank=True)
    canAddUsers=models.BooleanField(default=True, null=True)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class TeachingAssistant(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    userInformation=models.ForeignKey(UserInformation, on_delete=models.CASCADE, null=True, blank=True)
    contact_number=models.CharField(null=True, max_length=20)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'