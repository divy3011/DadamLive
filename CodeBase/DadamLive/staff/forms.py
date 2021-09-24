from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import FilePurposes

class FileForm(ModelForm):
    class Meta:
        model = FilePurposes
        fields = [
            "file",
        ]