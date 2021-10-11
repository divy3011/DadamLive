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
        return False
    try:
        info=UserInformation.objects.get(user=request.user)
        if info.userType.userTypeCode==settings.CODE_FACULTY:
            faculty=Faculty.objects.get(user=request.user)
            return faculty
        return False
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

def manage_quiz(request,quiz_id):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        course=quiz.course
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    
    if request.method=="POST":
        question_type=request.POST.get("question_type")
        if int(question_type)==1:
            question_written=request.POST.get("question_written")
            max_marks_written=float(request.POST.get("max_marks_written"))
            scheme=int(request.POST.get("marking_scheme"))
            mcq=MCQ.objects.create(quiz=quiz, question=question_written, maximum_marks=max_marks_written, markingScheme=scheme)
            index=0
            for i in range(1,7):
                select=request.POST.get("sel"+str(i))
                if int(select)!=1:
                    option=request.POST.get("opt"+str(i))
                    mcq.options.append(option)
                    if int(select)==2:
                        mcq.correct_answers.append(index)
                    index=index+1
            mcq.save()

        elif int(question_type)==2:
            question_written=request.POST.get("question_written")
            max_marks_written=float(request.POST.get("max_marks_written"))
            WrittenQuestion.objects.create(quiz=quiz, question=question_written, maximum_marks=max_marks_written)
        elif int(question_type)==3:
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
                    mcq=MCQ.objects.filter(quiz=quiz)
                    written=WrittenQuestion.objects.filter(quiz=quiz)
                    submissions=False
                    if quiz.quizHeld:
                        submissions=Submission.objects.filter(quiz=quiz)
                    return render(request,"faculty/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": "Not an excel or csv file", "submissions": submissions})
                return manage_quiz_helper(request, data, quiz)
        return redirect('manage_quiz',quiz_id)
    else:
        mcq=MCQ.objects.filter(quiz=quiz)
        written=WrittenQuestion.objects.filter(quiz=quiz)
        submissions=False
        if quiz.quizHeld:
            submissions=Submission.objects.filter(quiz=quiz)
        return render(request,"faculty/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "submissions": submissions})

def manage_quiz_helper(request, data, quiz):
    mcq=MCQ.objects.filter(quiz=quiz)
    written=WrittenQuestion.objects.filter(quiz=quiz)
    if 'Question Type' not in data.columns and 'Question' not in data.columns and 'Maximum Marks' not in data.columns:
        return render(request,"faculty/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": "Either of Question Type, Question or Maximum Marks Column was not found in the file."})

    field_with_unknown_values=[]
    field_with_duplicate_data=[]
    for i in range(len(data["Question"])):
        typeOfQ=data["Question Type"][i]
        question_written=data["Question"][i]
        max_marks_written=data["Maximum Marks"][i]
        if typeOfQ=="Subjective":
            try:
                WrittenQuestion.objects.get(quiz=quiz, question=question_written, maximum_marks=max_marks_written)
                field_with_duplicate_data.append(i+1)
            except:
                WrittenQuestion.objects.create(quiz=quiz, question=question_written, maximum_marks=max_marks_written)
        elif typeOfQ=="Objective":
            try:
                MCQ.objects.get(quiz=quiz, question=question_written, maximum_marks=max_marks_written)
                field_with_duplicate_data.append(i+1)
            except:
                try:
                    scheme=data["Marking Scheme"][i]
                    mcq=MCQ.objects.create(quiz=quiz, question=question_written, maximum_marks=max_marks_written, markingScheme=scheme)
                    index=0
                    for j in range(1,7):
                        if "Option"+str(j) not in data.columns:
                            break
                        option=data["Option"+str(j)][i]
                        if str(option)!="nan":
                            mcq.options.append(option)
                    if "Correct Options" not in data.columns:
                        field_with_unknown_values.append(i+1)
                        mcq.delete()
                    correct_answers=str(data["Correct Options"][i]).split(",")
                    for correct_option in correct_answers:
                        mcq.correct_answers.append(int(correct_option)-1)
                    mcq.save()
                except:
                    field_with_unknown_values.append(i+1)
                    mcq.delete()
    mcq=MCQ.objects.filter(quiz=quiz)
    written=WrittenQuestion.objects.filter(quiz=quiz)
    if len(field_with_unknown_values)==0 and len(field_with_duplicate_data)==0:
        return render(request,"faculty/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": "All questions have been added successfully."})    
    elif len(field_with_unknown_values)==0:  
        error="Rows with duplicate data are : "+str(field_with_duplicate_data)+" . You can cross-verify, questions have been added from rest of the rows."
    elif len(field_with_duplicate_data)==0:  
        error="Rows with empty or not found values are : "+str(field_with_unknown_values)+" . You can cross-verify, questions have been added from rest of the rows."
    else:
        error1="Rows with duplicate data are : "+str(field_with_duplicate_data)+" ."
        error2="Rows with empty or not found values are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, questions have been added from rest of the rows."
        error=error1+"\n"+error2
    return render(request,"faculty/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": error})

def change_quiz_status(request,quiz_id):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        course=quiz.course
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)

    if quiz.hidden:
        quiz.hidden=False
    else:
        if quizOngoing(quiz)==False:
            return JsonResponse({"message": "This option is available during quiz"}, status=400)
        quiz.hidden=True
    quiz.save()
    return redirect('manage_quiz',quiz_id)

def quizOngoing(quiz):
    if quiz.end_date.date()<datetime.datetime.now().date():
        return True
    
    if quiz.start_date.date()>datetime.datetime.now().date():
        return True

    if quiz.start_date.date()==datetime.datetime.now().date() and datetime.datetime.now().time()<quiz.start_date.time():
        return True

    if quiz.end_date.date()==datetime.datetime.now().date() and datetime.datetime.now().time()>quiz.end_date.time():
        return True
    
    return False

def quiz_analysis(request):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    if request.method!="POST":
        return JsonResponse({"message": "Unable to process this request."}, status=400)
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(request.POST.get("quiz_id")))
        course=quiz.course
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    
    if quiz.quizHeld==False:
        return JsonResponse({"message": "Analysis can not be done until quiz gets over."}, status=400)
    
    submissions=Submission.objects.filter(quiz=quiz)
    illegal_attempts=[]
    for each in submissions:
        try:
            attempt=IllegalAttempt.objects.get(submission=each)
            illegal_attempts.append(attempt)
        except:
            pass
    part_of_submissions=0
    attempt=0
    for each in submissions:
        try:
            part=PartOfSubmission.objects.filter(submission=each)
            if attempt==0:
                part_of_submissions=part
            else:
                part_of_submissions.append(part)
        except:
            pass
    submissions=serializers.serialize('json', submissions)
    illegal_attempts=serializers.serialize('json', illegal_attempts)
    part_of_submissions=serializers.serialize('json', part_of_submissions)
    users=serializers.serialize('json', User.objects.all())
    written=serializers.serialize('json', WrittenQuestion.objects.filter(quiz=quiz))
    return JsonResponse({"users": users, "written": written, "submissions": submissions, "illegal_attempts": illegal_attempts, "part_of_submissions": part_of_submissions}, status=200)

def generate_score(request, quiz_id):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        course=quiz.course
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    
    if quiz.quizHeld==False:
        return JsonResponse({"message": "Score can not be calculated until quiz gets over."}, status=400)

    submissions=Submission.objects.filter(quiz=quiz)
    mcq=MCQ.objects.filter(quiz=quiz)
    for s in submissions:
        s.score=0
        s.save()
        for m in mcq:
            try:
                p=PartOfSubmission.objects.get(submission=s, question_id=int(m.id))
                marked=str(p.answer).split(",")
                answer=m.correct_answers
                marks=calculate_marks(answer, marked, m)
                p.mark=marks
                p.save()
                s.score+=marks
                s.save()
            except:
                pass
    return redirect('manage_quiz', quiz_id)

def calculate_marks(answer, marked, mcq):
    print(answer, marked)
    if marked[0]=='':
        return 0.0
    answer.sort()
    marked.sort()
    if mcq.markingScheme==2:
        if len(answer)!=len(marked):
            return mcq.negativeMarks
        for i in range(answer):
            if int(answer[i])!=int(marked[i]):
                return mcq.negativeMarks
        return mcq.maximum_marks
    total_options_correct=0
    if mcq.markingScheme==1:
        for each in marked:
            if int(each) in answer:
                total_options_correct+=1
            else:
                total_options_correct-=1
    if total_options_correct>0:
        return (mcq.maximum_marks*total_options_correct)/len(answer)
    return 0