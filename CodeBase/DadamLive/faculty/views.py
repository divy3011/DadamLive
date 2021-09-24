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
    
    if request.method=="POST":
        pass
    else:
        enrolments=Enrolment.objects.filter(course=course)
        announcements=Announcement.objects.filter(course=course)
        quizes=Quiz.objects.filter(course=course)
        #Also to add thesr in post request later
        context={"course": course, "enrolments": enrolments, "announcements": announcements, "quizes": quizes}
        return render(request,"faculty/view_course.html",context=context)

def add_student_ta(request,course_id):
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

    if request.method!="POST":
        return JsonResponse({"message": "Course was not found on this server"}, status=400)

    form=FileForm(request.POST,request.FILES)
    if form.is_valid():
        file=form.cleaned_data['file']
        if str(file).endswith('.csv'):
            # csv file
            data=pd.read_csv(file)
        elif str(file).endswith('.xlsx'):
            # excel file
            data=pd.read_excel(file)
        else:
            return render(request,"faculty/view_course.html",context={"course": course, "message": "Not an excel or csv file"})
        return add_student_ta_helper(request, data, course)
    return render(request,"faculty/view_course.html",context={"course": course, "message": "Error Occured."})

def add_student_ta_helper(request, data, course):
    if 'Email' not in data.columns and 'Username' not in data.columns:
        return render(request,"faculty/view_course.html",context={"course": course, "message": "Email column was not found in the file."})     
    emailGiven=True 
    if 'Email' not in data.columns:
        emailGiven=False
    if 'Role' not in data.columns:
        return render(request,"faculty/view_course.html",context={"course": course, "message": "Account Type column was not found in the file."})      

    total_accounts=0
    try:
        total_accounts=len(data['Email'])
    except:
        total_accounts=len(data['Username'])
    field_with_unknown_values=[]
    field_with_duplicate_data=[]
    for i in range(total_accounts):
        user=""
        if emailGiven:
            email=data['Email'][i]
            try:
                user=User.objects.get(email=email)
            except:
                field_with_unknown_values.append(i+1)
                continue 
        else:
            try:
                user=User.objects.get(username=data['Username'][i])
            except:
                field_with_unknown_values.append(i+1)
                continue
        role=data['Role'][i]
        if role!='Student' and role!="TA":
            field_with_unknown_values.append(i+1)
            continue
        if user and role:
            try:
                Enrolment.objects.get(user=user,course=course)
                field_with_duplicate_data.append(i+1)
                continue
            except:
                pass
            userType=""
            if role=="Student":
                userType=UserType.objects.get(userTypeCode=int(settings.CODE_STUDENT))
                try:
                    Student.objects.get(user=user)
                except:
                    field_with_unknown_values.append(i+1)
                    continue 
            if role=="TA":
                userType=UserType.objects.get(userTypeCode=int(settings.CODE_TA))
                try:
                    TeachingAssistant.objects.get(user=user)
                except:
                    field_with_unknown_values.append(i+1)
                    continue 
            Enrolment.objects.create(user=user, course=course, userType=userType)
            subject="Enrolment Confirmation in DadamLive"
            message="You have been enroled as "+role+" in "+course.courseName+" in DadamLive. You can leave the course if you want but all the progress including tests will be lost if you do so."
            try:
                Email_thread(subject,message,email).start()
            except:
                print("Unable to send email")
        else:
            field_with_unknown_values.append(i+1)

    if len(field_with_unknown_values)==0 and len(field_with_duplicate_data)==0:
        return render(request,"faculty/view_course.html",context={"course": course, "message": "All users have been added successfully."})    
    elif len(field_with_unknown_values)==0:  
        error="Rows with duplicate data are : "+str(field_with_duplicate_data)+" . You can cross-verify, users have been added from rest of the rows."
    elif len(field_with_duplicate_data)==0:  
        error="Rows with empty email and empty username or undefined role are : "+str(field_with_unknown_values)+" . You can cross-verify, users have been added from rest of the rows."
    else:
        error1="Rows with duplicate data are : "+str(field_with_duplicate_data)+" ."
        error2="Rows with empty email and empty username or undefined role are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, users have been added from rest of the rows."
        error=error1+"\n"+error2
    return render(request,"faculty/view_course.html",context={"course": course, "message": error})

def faculty_announcement(request,course_id):
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
    
    if request.method=="POST":
        message=request.POST.get("ann_message")
        Announcement.objects.create(course=course, message=message)
        return redirect('view_course', course_id)
    else:
        return JsonResponse({"error": "Course was not found on this server"}, status=400)

def announce_quiz(request, course_id):
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
    
    if request.method=="POST":
        quiz_name=request.POST.get("quiz_name")
        start_date=request.POST.get("start_date")
        end_date=request.POST.get("end_date")
        hidden_quiz=request.POST.get("hidden_quiz")
        hide=True
        if int(hidden_quiz)==2:
            hide=False
        start_date=datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_date=datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        print(start_date)
        if end_date<start_date:
            return JsonResponse({"error": "Start time must be less than end time"}, status=400)
        if start_date<datetime.datetime.now():
            return JsonResponse({"error": "Quiz can only be started in future"}, status=400)
        Quiz.objects.create(course=course, quiz_name=quiz_name, start_date=start_date, end_date=end_date, hidden=hide)
        return redirect('view_course', course_id)
    else:
        return JsonResponse({"error": "Course was not found on this server"}, status=400)