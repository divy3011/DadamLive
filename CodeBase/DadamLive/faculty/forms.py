from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Course

class CoursePhotoForm(ModelForm):
    class Meta:
        model = Course
        fields = [
            "image"
        ]