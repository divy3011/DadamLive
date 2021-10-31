from django.http.response import JsonResponse
from django.core import serializers
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
from .models import *
from faculty.models import *
from threading import *
from home.models import *
from twilio.rest import Client
# Create your views here.

class Email_thread(Thread):
    def __init__(self,subject,message,email):
        self.email=email
        self.subject=subject
        self.message=message
        Thread.__init__(self)

    def run(self):
        SENDMAIL(self.subject,self.message,self.email)

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
        return [False, redirect('home')]
    try:
        info=UserInformation.objects.get(user=request.user)
        if info.userType.userTypeCode==settings.CODE_TA:
            ta=TeachingAssistant.objects.get(user=request.user)
            return [True, ta]
        return [False, redirect('home')]
    except:
        return [False, redirect('home')]

def dashboardTA(request):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolments=Enrolment.objects.filter(user=request.user)
    return render(request,"ta/dashboard.html",context={"enrolments": enrolments})

def view_course_ta(request, course_id):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolment=False
    course=False
    try:
        course=Course.objects.get(id=int(course_id))
        enrolment=Enrolment.objects.get(user=request.user, course=course)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)
    enrolments=Enrolment.objects.filter(course=course)
    announcements=Announcement.objects.filter(course=course).order_by('-id')
    quizes=Quiz.objects.filter(course=course).order_by('-id')
    TA_permissions=TeachingAssistantPermission.objects.filter(enrolment__course=course)
    permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
    context={"course": course, "enrolments": enrolments, "announcements": announcements, "quizes": quizes,"TA_permissions": TA_permissions, "permissions": permissions}
    return render(request, 'ta/view_course.html', context=context)

def ta_announcement(request, course_id):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolment=False
    course=False
    try:
        course=Course.objects.get(id=int(course_id))
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canAnnounce):
            return JsonResponse({"message": "It seems you have not been given permission to announce in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)

    if request.method=="POST":
        message=request.POST.get("ann_message")
        Announcement.objects.create(course=course, message=message, created_by=request.user)
        return redirect('view_course_ta', course_id)
    else:
        return JsonResponse({"error": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)

def ta_announce_quiz(request, course_id):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolment=False
    course=False
    try:
        course=Course.objects.get(id=int(course_id))
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canManageQuiz):
            return JsonResponse({"message": "It seems you have not been given permission to create a new quiz in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)
    
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
        if end_date<start_date:
            return JsonResponse({"error": "Start time must be less than end time"}, status=400)
        if start_date<datetime.datetime.now():
            return JsonResponse({"error": "Quiz can only be started in future"}, status=400)
        Quiz.objects.create(course=course, quiz_name=quiz_name, start_date=start_date, end_date=end_date, hidden=hide)
        return redirect('view_course_ta', course_id)
    else:
        return JsonResponse({"error": "Course was not found on this server"}, status=400)

def get_permission_data(request):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    if request.method!="POST":
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    enrolment=False
    course=False
    try:
        course=Course.objects.get(id=int(request.POST.get('course_id')))
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canManageTAPermissions):
            return JsonResponse({"message": "It seems you have not been given permission to manage TA permissions in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)
    
    try:
        taap=TeachingAssistantPermission.objects.get(id=int(request.POST.get('ta_permission_id')))
        if taap.enrolment.course!=course:
            return JsonResponse({"message": "The TA was never enroled in the course"}, status=400)
        return JsonResponse({"data": serializers.serialize('json', [taap])}, status=200)
    except:
        return JsonResponse({"message": "TA Permissions were not found on this server"}, status=400)

def update_ta_permissions(request):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    if request.method!="POST":
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    enrolment=False
    course=False
    try:
        course=Course.objects.get(id=int(request.POST.get('course_id_ta')))
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canManageTAPermissions):
            return JsonResponse({"message": "It seems you have not been given permission to manage TA permissions in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)
    try:
        taap=TeachingAssistantPermission.objects.get(id=int(request.POST.get('permission_id')))
        if taap.enrolment.course!=course:
            return JsonResponse({"message": "The TA was never enroled in the course"}, status=400)
        if taap.enrolment.user==request.user:
            return JsonResponse({"message": "For security reasons, you cannot update your own permissions, rather you can only view your permissions."}, status=400)
        taap.isMainTA=str_to_bool_converter(request.POST.get("select_head_ta"))
        taap.canManageTAPermissions=str_to_bool_converter(request.POST.get("canManageTAPermissions"))
        taap.canCheckAnswerSheets=str_to_bool_converter(request.POST.get("canCheckAnswerSheets"))
        taap.canAnnounce=str_to_bool_converter(request.POST.get("canAnnounce"))
        taap.canManageQuiz=str_to_bool_converter(request.POST.get("canManageQuiz"))
        taap.save()
        return JsonResponse({"message": "TA Permissions were saved successfully."}, status=200)
    except:
        return JsonResponse({"message": "TA Permissions were not found on this server"}, status=400)

def str_to_bool_converter(input):
    if int(input)==1:
        return True
    return False