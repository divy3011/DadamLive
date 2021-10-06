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
from faculty.models import Enrolment
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
from faculty.models import *
import pytz

utc=pytz.UTC

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
        return False
    try:
        info=UserInformation.objects.get(user=request.user)
        if info.userType.userTypeCode==settings.CODE_STUDENT:
            student=Student.objects.get(user=request.user)
            return student
        return False
    except:
        return False

def dashboardStudent(request):
    student=basicChecking(request)
    if student==False:
        return redirect('home')
    return render(request,"student/dashboard.html",context={"student": student})

def my_courses(request):
    student=basicChecking(request)
    if student==False:
        return redirect('home')
    usertype=UserType.objects.get(userTypeCode=settings.CODE_STUDENT)
    enrolments=Enrolment.objects.filter(user=request.user, userType=usertype)
    return render(request,"student/my_courses.html",context={"student": student, "enrolments": enrolments})
    
def view_course_student(request, course_id):
    student=basicChecking(request)
    if student==False:
        return redirect('home')
    course=""
    try:
        course=Course.objects.get(id=int(course_id))
        Enrolment.objects.get(course=course, user=request.user)
    except:
        return JsonResponse({"message": "Course was not found on this server or you have not been invited by the instructor."}, status=400)
    announcements=Announcement.objects.filter(course=course)
    quizes=Quiz.objects.filter(course=course, hidden=False)
    return render(request,"student/view_course_student.html",context={"student": student, "course": course, "announcements": announcements, "quizes": quizes})

def quiz_identification(quiz):
    if quiz.hidden:
        return JsonResponse({"message": "Quiz has been moved to hidden section and is no longer available to you."}, status=400)

    if quiz.end_date.date()<datetime.datetime.now().date():
        return JsonResponse({"message": "Quiz is no longer avaiable."}, status=400)
    
    if quiz.start_date.date()>datetime.datetime.now().date():
        return JsonResponse({"message": "Quiz has not been started yet."}, status=400)

    if quiz.start_date.date()==datetime.datetime.now().date() and datetime.datetime.now().time()<quiz.start_date.time():
        return JsonResponse({"message": "Quiz has not been started yet."}, status=400)

    if quiz.end_date.date()==datetime.datetime.now().date() and datetime.datetime.now().time()>quiz.end_date.time():
        return JsonResponse({"message": "Quiz is no longer available."}, status=400)

    return True

def start_quiz(request, quiz_id):
    student=basicChecking(request)
    if student==False:
        return redirect('home')
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        Enrolment.objects.get(course=quiz.course, user=request.user)
    except:
        return JsonResponse({"message": "Quiz was not found on this server or you have not been invited by the instructor."}, status=400)
    
    identity=quiz_identification(quiz)
    if identity!=True:
        return identity

    submission=False
    try:
        submission=Submission.objects.get(quiz=quiz, user=request.user)
        if submission.sumitted:
            return JsonResponse({"message": "You already have submitted the quiz 1 time."}, status=400)
    except:
        pass

    if request.method=="POST":
        pass
    else:
        return render(request,"student/start_quiz.html",context={"quiz": quiz})

def get_questions(request, quiz_id):
    student=basicChecking(request)
    if student==False:
        return redirect('home')
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        Enrolment.objects.get(course=quiz.course, user=request.user)
    except:
        return JsonResponse({"message": "Quiz was not found on this server or you have not been invited by the instructor."}, status=400)
    
    identity=quiz_identification(quiz)
    if identity!=True:
        return identity

    submission=False
    try:
        submission=Submission.objects.get(quiz=quiz, user=request.user)
        if submission.sumitted:
            return JsonResponse({"message": "You already have submitted the quiz 1 time."}, status=400)
    except:
        pass

    if request.method=="POST":
        pass
    else:
        mcq=MCQ.objects.filter(quiz=quiz)
        written=WrittenQuestion.objects.filter(quiz=quiz)
        return JsonResponse({"quiz": serializers.serialize('json', [quiz]), "mcq": serializers.serialize('json', mcq), "written": serializers.serialize('json', written)}, status=200)

def save_question(request, q_type):
    student=basicChecking(request)
    if student==False:
        return redirect('home')
    quiz=""
    quiz_id=int(request.GET["quiz_id"])
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        Enrolment.objects.get(course=quiz.course, user=request.user)
    except:
        return JsonResponse({"message": "Quiz was not found on this server or you have not been invited by the instructor."}, status=400)
    
    identity=quiz_identification(quiz)
    if identity!=True:
        return identity

    submission=False
    try:
        submission=Submission.objects.get(quiz=quiz, user=request.user)
        if submission.sumitted:
            return JsonResponse({"message": "You already have submitted the quiz 1 time."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)

    if int(q_type)==1:
        pass
    elif int(q_type)==2:
        part=""
        answer=request.GET["answer"]
        question_id=request.GET["question_id"]
        # PartOfSubmission.objects.get(submission=submission, question_type=int(q_type), question_id=int(question_id))
        try:
            part=PartOfSubmission.objects.get(submission=submission, question_type=int(q_type), question_id=int(question_id[7:]))
        except:
            part=PartOfSubmission.objects.create(submission=submission, question_type=int(q_type), question_id=int(question_id[7:]))
        part.answer=answer
        part.save()
    else:
        return JsonResponse({"message": "Not a valid question."}, status=400)
    return JsonResponse({"success": "State Saved"}, status=200)

