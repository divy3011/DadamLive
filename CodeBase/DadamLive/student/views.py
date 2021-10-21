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
import pandas as pd
from staff.forms import FileForm
from .models import *
from faculty.models import *
import pytz
# import dlib
import cv2
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from copy import deepcopy
from sklearn.feature_extraction.text import TfidfVectorizer
utc=pytz.UTC
from django.contrib.staticfiles.storage import staticfiles_storage
import copy
import io
from django.core.files.base import ContentFile
import ntplib

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
        return [False, redirect('home')]
    try:
        info=UserInformation.objects.get(user=request.user)
        if info.userType.userTypeCode==settings.CODE_STUDENT:
            student=Student.objects.get(user=request.user)
            return [True, student]
            # if student.faceAdded:
            #     return [True, student]
            # else:
            #     return [False, render(request, "student/faceCollection.html",context={})]
        return [False, redirect('home')]
    except:
        return [False, redirect('home')]

def dashboardStudent(request):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
    enrolments=Enrolment.objects.filter(user=request.user)
    total_enrolments=enrolments.count()
    submissions=Submission.objects.filter(user=request.user)
    total_quizes_given=submissions.count()
    points=0
    no_face=0
    audio=0
    for each in submissions:
        points+=each.score
        att=IllegalAttempt.objects.get(submission=each)
        no_face+=att.noPersonDetected
        audio+=att.numberOfTimesAudioDetected
    
    advise="Going Good"

    if audio>10:
        advise="Reduce noise"
    
    if no_face>30:
        advise="Use Lit room"

    return render(request,"student/dashboard.html",context={"advise": advise, "points": points, "student": student, "total_enrolments": total_enrolments, "total_quizes_given": total_quizes_given, "submissions": submissions})

def my_courses(request):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
    usertype=UserType.objects.get(userTypeCode=settings.CODE_STUDENT)
    enrolments=Enrolment.objects.filter(user=request.user, userType=usertype)
    return render(request,"student/my_courses.html",context={"student": student, "enrolments": enrolments})
    
def view_course_student(request, course_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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

    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')
    Internet_date_and_time = datetime.datetime.fromtimestamp(response.tx_time)

    # print(Internet_date_and_time.time(), quiz.start_date.time())
    # print(Internet_date_and_time.date(), quiz.start_date.date())

    if quiz.end_date.date()<Internet_date_and_time.date():
        return JsonResponse({"message": "Quiz is no longer avaiable."}, status=400)
    
    if quiz.start_date.date()>Internet_date_and_time.date():
        return JsonResponse({"message": "Quiz has not been started yet."}, status=400)

    if quiz.start_date.date()==Internet_date_and_time.date() and Internet_date_and_time.time()<quiz.start_date.time():
        return JsonResponse({"message": "Quiz has not been started yet."}, status=400)
    
    if quiz.end_date.date()==Internet_date_and_time.date() and Internet_date_and_time.time()>quiz.end_date.time():
        return JsonResponse({"message": "Quiz is no longer available."}, status=400)

    return True

def start_quiz(request, quiz_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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
        if submission.submitted:
            return JsonResponse({"message": "You already have submitted the quiz 1 time."}, status=400)
    except:
        submission=Submission.objects.create(quiz=quiz, user=request.user)

    written=WrittenQuestion.objects.filter(quiz=quiz)
    mcq=MCQ.objects.filter(quiz=quiz)
    for each in written:
        try:
            PartOfSubmission.objects.get(submission=submission, question_type=2, question_id=each.id)
        except:
            PartOfSubmission.objects.create(submission=submission, question_type=2, question_id=each.id)
    
    for each in mcq:
        try:
            PartOfSubmission.objects.get(submission=submission, question_type=1, question_id=each.id)
        except:
            PartOfSubmission.objects.create(submission=submission, question_type=1, question_id=each.id)

    if request.method=="POST":
        pass
    else:
        return render(request,"student/start_quiz.html",context={"quiz": quiz})

def get_questions(request, quiz_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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
        if submission.submitted:
            return JsonResponse({"message": "You already have submitted the quiz 1 time."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)

    if request.method=="POST":
        pass
    else:
        mcq=MCQ.objects.filter(quiz=quiz)
        written=WrittenQuestion.objects.filter(quiz=quiz)
        partOfSubmission=PartOfSubmission.objects.filter(submission=submission)
        return JsonResponse({"quiz": serializers.serialize('json', [quiz]), "mcq": serializers.serialize('json', mcq), "written": serializers.serialize('json', written), "partOfSubmission": serializers.serialize('json', partOfSubmission)}, status=200)

def save_question(request, q_type):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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
        if submission.submitted:
            return JsonResponse({"message": "You already have submitted the quiz 1 time."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)
    
    if int(q_type)!=1 and int(q_type)!=2:
        return JsonResponse({"message": "Not a valid question."}, status=400)

    part=""
    answer=request.GET["answer"]
    question_id=request.GET["question_id"]
    if int(q_type)==2:
        question_id=int(question_id[7:])
    else:
        question_id=int(question_id[3:])
    try:
        part=PartOfSubmission.objects.get(submission=submission, question_type=int(q_type), question_id=question_id)
        if part.answer_locked:
            return JsonResponse({"message": "Answer was locked, now it can't be changed"}, status=400)
    except:
        part=PartOfSubmission.objects.create(submission=submission, question_type=int(q_type), question_id=question_id)
    part.answer=answer
    part.save()
    
    return JsonResponse({"success": "State Saved"}, status=200)

def freeze_answer(request):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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
        if submission.submitted:
            return JsonResponse({"message": "You already have submitted the quiz 1 time."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)
    
    part=False
    try:
        part=PartOfSubmission.objects.get(id=int(request.GET.get("part_id")))
    except:
        return JsonResponse({"message": "Part not found"}, status=400)
    if quiz.disable_previous:
        if part.answer_locked==False:    
            part.answer=request.GET.get("answer")
            part.answer_locked=True
            part.save()
    else:
        part.answer=request.GET.get("answer")
        part.save()

    return JsonResponse({"message": "Part locked"}, status=200)


def mark_activity(request, quiz_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
    quiz=""
    typeAct=int(request.GET["type"])
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
        if submission.submitted:
            return JsonResponse({"message": "Quiz submitted that means you can't cheat."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)
    
    activity=""
    try:
        activity=IllegalAttempt.objects.get(submission=submission)
    except:
        activity=IllegalAttempt.objects.create(submission=submission)
    
    if typeAct==1:
        activity.browserSwitched=activity.browserSwitched+1
    if typeAct==5:
        activity.numberOfTimesAudioDetected=activity.numberOfTimesAudioDetected+1
    if typeAct==7:
        activity.screenShared=True
    if typeAct==8:
        activity.screenSharingTurnedOff=activity.screenSharingTurnedOff+1
    activity.save()

    return JsonResponse({"message": "Activity Marked"}, status=200)

def mark_ip(request, quiz_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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
        if submission.submitted:
            return JsonResponse({"message": "Quiz submitted that means you can't cheat."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)
    ipAddress=request.GET.get("ipAddress")
    try:
        s=Submission.objects.filter(ip_address=ipAddress, quiz=quiz)

        if len(s)!=0:
            flag=1
            if len(s)==1:
                if s[0].user==request.user:
                    flag=0
            if flag==1:
                for each in s:
                    i=""
                    try:
                        i=IllegalAttempt.objects.get(submission=each)
                    except:
                        i=IllegalAttempt.objects.create(submission=each)
                    i.usingSomeoneElseIP=True
                    i.save()
                i=""
                try:
                    i=IllegalAttempt.objects.get(submission=submission)
                except:
                    i=IllegalAttempt.objects.create(submission=submission)
                i.usingSomeoneElseIP=True
                i.save()
    except:
        pass

    submission.ip_address=ipAddress
    submission.save()

    return JsonResponse({"message": "IP Saved"}, status=200)

def image_detector(request,quiz_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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
        if submission.submitted:
            return JsonResponse({"message": "Quiz submitted that means you can't cheat."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)
    image=request.POST.get("image")
    img=request.POST.get("image1")
    img1=copy.deepcopy(img)

    face_cascade = cv2.CascadeClassifier('static/Student/js/haarcascade_frontalface_default.xml')
    # print(face_cascade)
    # detector = dlib.get_frontal_face_detector()
    image = base64.b64decode(image)
    image = Image.open(BytesIO(image))
    image  = np.array(image)


    imageRGB=[]
    for i in range(len(image)):
        res=[]
        for j in range(len(image[0])):
            res1=[]
            for k in range(3):
                res1.append(image[i][j][k])
            res.append(res1)
        imageRGB.append(res)
        
    imageRGB=np.array(imageRGB, dtype=np.uint8)

    gray = cv2.cvtColor(imageRGB, cv2.COLOR_BGR2GRAY)
    # faces = detector(gray)
    faces=face_cascade.detectMultiScale(gray, 1.1, 4)
    # print(len(faces))
    # print(faces)
    activity=""
    try:
        activity=IllegalAttempt.objects.get(submission=submission)
    except:
        activity=IllegalAttempt.objects.create(submission=submission)

    if len(faces)>1:
        format, imgstr=img.split(';base64,') 
        ext=format.split('/')[-1] 
        img=ContentFile(base64.b64decode(imgstr), name='temp.' + ext) 
        ImagesForActivity.objects.create(submission=submission,image=img,typeAct=2)
        print("Multiple faces were detected")
        activity.numberOfTimesMultiplePersonsDetected=activity.numberOfTimesMultiplePersonsDetected+1
        activity.save()
    elif len(faces)==0:
        print("No person was detected.")
        activity.noPersonDetected=activity.noPersonDetected+1
        activity.save()
    try:
        mobileDetection(image, activity, img1, submission)
    except:
        pass
        # print("Error in mobile detection fnc")

    return JsonResponse({"message": "Image Detection Done"}, status=200)

def tab_change_image_save(request, quiz_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
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
        if submission.submitted:
            return JsonResponse({"message": "Quiz submitted that means you can't cheat."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)
    image=request.POST.get("image")
    format, imgstr=image.split(';base64,') 
    ext=format.split('/')[-1] 
    image=ContentFile(base64.b64decode(imgstr), name='temp.' + ext) 

    ImagesForActivity.objects.create(submission=submission,image=image,typeAct=1)

    return JsonResponse({"message": "Image Saved"}, status=200)

def mobileDetection(img, activity, image, submission):
    imageRGB=[]
    for i in range(len(img)):
        res=[]
        for j in range(len(img[0])):
            res1=[]
            for k in range(3):
                res1.append(img[i][j][k])
            res.append(res1)
        imageRGB.append(res)
        
    img=np.array(imageRGB, dtype=np.uint8)

    configPath = 'static/Student/js/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightsPath = 'static/Student/js/frozen_inference_graph.pb'

    net = cv2.dnn_DetectionModel(weightsPath,configPath)
    net.setInputSize(320,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    classIds, confs, bbox = net.detect(img, confThreshold=0.45)

    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            if classId==77:
                activity.noOfTimesMobileDetected+=1
                activity.save()
                format, imgstr=image.split(';base64,') 
                ext=format.split('/')[-1] 
                image=ContentFile(base64.b64decode(imgstr), name='temp.' + ext) 

                ImagesForActivity.objects.create(submission=submission,image=image,typeAct=6)
                print("Mobile Detected")
    

def end_test(request, quiz_id):
    student=basicChecking(request)
    if student[0]==False:
        return student[1]
    student=student[1]
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        Enrolment.objects.get(course=quiz.course, user=request.user)
    except:
        return JsonResponse({"message": "Quiz was not found on this server or you have not been invited by the instructor."}, status=400)

    submission=False
    try:
        submission=Submission.objects.get(quiz=quiz, user=request.user)
        if submission.submitted:
            return JsonResponse({"message": "Quiz submitted that means you can't cheat."}, status=400)
    except:
        if submission==False:
            submission=Submission.objects.create(quiz=quiz, user=request.user)
    
    if submission.submitted==False:
        submission.submitted=True
        submission.save()
        subject = 'Quiz Submission'
        message = f'Your submission was received for the quiz'+quiz.quiz_name
        Email_thread(subject,message,request.user.email).start()
        checkForQuizStatus(quiz)
        return JsonResponse({"message": "Submission Saved"}, status=200)

    return JsonResponse({"message": "Already Submitted"}, status=200)

def checkForQuizStatus(quiz):
    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')
    Internet_date_and_time = datetime.datetime.fromtimestamp(response.tx_time)
    if quiz.end_date.date()<Internet_date_and_time.date():
        if quiz.quizHeld==False:
            quiz.quizHeld=True
            quiz.save()

    if quiz.end_date.date()==Internet_date_and_time.date() and Internet_date_and_time.time()>quiz.end_date.time():
        if quiz.quizHeld==False:
            quiz.quizHeld=True
            quiz.save()