from django.http.response import JsonResponse
from django.core import serializers
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
import math,random,string,datetime
from twilio.rest import Client
from home.models import *
from .forms import *
from .models import *
from threading import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.contrib.staticfiles import finders
from functools import lru_cache
import pandas as pd

class Email_thread(Thread):
    def __init__(self,subject,message,email):
        self.email=email
        self.subject=subject
        self.message=message
        Thread.__init__(self)

    def run(self):
        SENDMAIL(self.subject,self.message,self.email)

# Create your views here.
def SEND_OTP_TO_PHONE(mobile_number, country_code, message):
    client = Client(settings.PHONE_ACCOUNT_SID_TWILIO, settings.PHONE_ACCOUNT_AUTH_TOKEN_TWILIO)
    message = client.messages.create(
                        body=str(message),
                        from_= settings.PHONE_NUMBER_TWILIO,
                        to=str(country_code)+str(mobile_number)
                    )

def SENDMAIL(subject, message, email):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    checker = User.objects.get(email=email)
    username = checker.username
    html_content = render_to_string("home/email.html",{'message': message, 'user_name': username})
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject,text_content,email_from,recipient_list)
    email.attach_alternative(html_content,"text/html")
    email.send()
    # return render(request,'home/email.html',{'title':'send an email'})
    # send_mail( subject, message, email_from, recipient_list )

def home(request):
    return HttpResponse("<h1>Welcome to DadamLive Home Page</h1>")