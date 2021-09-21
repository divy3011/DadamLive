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
from threading import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.contrib.staticfiles import finders
from functools import lru_cache
import pandas as pd
from staff.forms import FileForm
from .models import *

# Create your views here.
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
    try:
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail( subject, message, email_from, recipient_list )
    except:
        print("Unable to send the email")

def basicChecking(request):
    if request.user.is_authenticated==False:
        return redirect('home')
    try:
        info=UserInformation.objects.get(user=request.user)
        if info.userType.userTypeCode==settings.CODE_FACULTY:
            faculty=Faculty.objects.get(user=request.user)
            return faculty
    except:
        return False

def dashboardFaculty(request):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    courses=Course.objects.filter(instructor=request.user)
    return render(request,"faculty/dashboard.html",context={"faculty": faculty, "courses": courses})

def start_new_course(request):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    if request.method=="POST":
        courseName=request.POST.get("course")
        try:
            course=Course.objects.get(instructor=request.user, courseName=courseName)
            return JsonResponse({"error": "Course Name is already taken by you. Try another one!"}, status=400)
        except:
            pass
        course=Course.objects.create(instructor=request.user, courseName=courseName)
        return JsonResponse({"success": "Course Added into the list"}, status=200)
    else:
        return render(request,"faculty/start_new_course.html",context={})

def view_course(request,course_id):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    course=""
    try:
        course=Course.objects.get(id=int(course_id))
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    
    if request.user=="POST":
        pass
    else:
        return render(request,"faculty/view_course.html",context={})