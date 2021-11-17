from faculty.views import dashboardFaculty
from django.http.response import JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from home.models import *
from .forms import *
from .models import *
from threading import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import escape, strip_tags
from staff.views import dashboardStaff
from student.views import dashboardStudent
from ta.views import dashboardTA
import math, random
from django.core.mail import send_mail
from pytz import timezone

class Email_thread(Thread):
    def __init__(self,subject,message,email):
        self.email=email
        self.subject=subject
        self.message=message
        Thread.__init__(self)

    def run(self):
        SENDMAIL(self.subject,self.message,self.email)

def SENDMAIL(subject, message, email):
    try:
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail( subject, message, email_from, recipient_list )
    except:
        print("Unable to send the email")

def home(request):
    return render(request,"home/home.html",context={})

def login_request(request):
    if request.user.is_authenticated:
        return login_redirecter(request)
    if request.method=='POST':
        useremail=request.POST.get('useremail')
        password=request.POST.get('password')
        try:
            checker = User.objects.get(username=useremail)
            user = authenticate(request, username=useremail, password=password)
            if user is not None:
                pass
            else:
                return JsonResponse({"error": "Invalid Credentials"}, status=400)
        except:
            try:
                checker = User.objects.get(email=useremail)
                user = authenticate(request, username=checker.username, password=password)
                if user is not None:
                    pass
                else:
                    return JsonResponse({"error": "Invalid Credentials"}, status=400)
            except:
                return JsonResponse({"error": "Invalid Credentials"}, status=400)
        login(request,user)
        return JsonResponse({"success": "Login is Successful."}, status=200)  
    else:
        return render(request,'home/login.html',context={})

def login_redirecter(request):
    try:
        info=UserInformation.objects.get(user=request.user)
        if info.userType.userTypeCode==settings.CODE_STAFF:
            #Staff User
            return redirect(dashboardStaff)
        if info.userType.userTypeCode==settings.CODE_FACULTY:
            #Faculty User
            return redirect(dashboardFaculty)
        if info.userType.userTypeCode==settings.CODE_STUDENT:
            #Student User
            return redirect(dashboardStudent)
        if info.userType.userTypeCode==settings.CODE_TA:
            # Teaching Assistant User
            return redirect(dashboardTA)
    except:
        return HttpResponse("<h1>Unable to fetch account details</h1>")

def logout_request(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')

def save_query(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        message=request.POST.get("message")
        Query.objects.create(name=name, email=email, phone=phone, message=message)
        return JsonResponse({"message": "Success"}, status=200)
    return JsonResponse({"message": "POST request is only allowed."}, status=400)

def forgot_password(request):
    if request.method=="POST":
        useremail=request.POST.get("useremail")
        user=False
        try:
            user=User.objects.get(email=useremail)
        except:
            try:
                user=User.objects.get(username=useremail)
            except:
                # Confuse users
                return JsonResponse({"message": "Success"}, status=200)
        fp=False
        try:
            fp=ForgotPassword.objects.get(user=user)
        except:
            fp=ForgotPassword.objects.create(user=user)
        
        uni_code=generate_code(25)
        fp.unique_code=uni_code
        fp.uni_time=datetime.datetime.now()
        fp.save()
        try:
            subject="Forgot your password?"
            link=settings.WEB_URL+"change_password/"+uni_code
            message="Hi, "+user.username+"\nA request was received that you forgot your password. Was it really you? Click on the following confirmation link to update your password.\n\nConfirmation Link is "+link+"\n\nIgnore this email if you do not want to change your password.\nNote: The link will expire in 5 minutes.\n\nThanks,\nDadamlive"
            Email_thread(subject,message,user.email).start()
        except:
            print("Unable to send email")
        return JsonResponse({"message": "Success"}, status=200)
    return render(request, "home/forgot_password.html", context={})

def change_password(request, unique_code):
    try:
        fp=ForgotPassword.objects.filter(unique_code=unique_code)
        if len(fp)==0:
            return redirect('login_request')
        if len(fp)!=1:
            return JsonResponse({"error": "There was internal clash. Please try to update your contact after 10 minutes."}, status=400)
        fp=fp[0]
        uni_time=fp.uni_time
        fp.uni_time=datetime.datetime.now()
        fp.save()
        fp=ForgotPassword.objects.get(id=fp.id)
        new_time=fp.uni_time
        time_delta=(new_time-uni_time)
        minutes=(time_delta.total_seconds())/60
        if minutes>6:
            return JsonResponse({"error": "This link has been expired."}, status=400)
    except:
        return redirect('login_request')

    if request.method=="POST":
        password2=request.POST.get("password2")
        user=fp.user
        user.set_password(password2)
        user.save()
        fp.unique_code=str(user.id)
        fp.save()
        return JsonResponse({"message": "Success"}, status=200)
    return render(request, "home/change_password.html", context={"user": fp.user})

def generate_code(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$!"
    password = ""
    for i in range(n) :
        password += digits[math.floor(random.random() * 62)]
    return password