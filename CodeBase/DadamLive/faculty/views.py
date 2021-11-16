from django.http.response import JsonResponse
from django.core import serializers
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
import datetime
from home.models import *
from threading import *
import pandas as pd
from staff.forms import FileForm
from .models import *
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from .forms import *
from background_task import background
import xlsxwriter
from io import BytesIO

# Create your views here.
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
    
def basicCheckingWithTA(request):
    if request.user.is_authenticated==False:
        return False
    try:
        info=UserInformation.objects.get(user=request.user)
        if info.userType.userTypeCode==settings.CODE_TA:
            ta=TeachingAssistant.objects.get(user=request.user)
            return ta
        return False
    except:
        return False

def dashboardFaculty(request):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    courses=Course.objects.filter(instructor=request.user)
    if request.method=="POST":
        course=False
        new_name=request.POST.get("name")
        try:
            course=Course.objects.get(id=int(request.POST.get("course_id")))
            if course.instructor!=request.user:
                return JsonResponse({"message": "Course not found"}, status=400)
        except:
            return JsonResponse({"message": "Course not found"}, status=400)
        try:
            Course.objects.get(instructor=request.user, courseName=new_name)
            return JsonResponse({"error": "Course Name is already taken by you. Try another one!"}, status=400)
        except:
            pass
        course.courseName=new_name
        course.save()
        return redirect('dashboardFaculty')
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

def get_permission_data(request):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    if request.method!="POST":
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    course=""
    try:
        course=Course.objects.get(id=int(request.POST.get('course_id')))
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    try:
        taap=TeachingAssistantPermission.objects.get(id=int(request.POST.get('ta_permission_id')))
        if taap.enrolment.course!=course:
            return JsonResponse({"message": "The TA was never enroled in the course"}, status=400)
        return JsonResponse({"data": serializers.serialize('json', [taap])}, status=200)
    except:
        return JsonResponse({"message": "TA Permissions were not found on this server"}, status=400)

def update_ta_permissions(request):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    if request.method!="POST":
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    course=""
    try:
        course=Course.objects.get(id=int(request.POST.get('course_id_ta')))
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    try:
        taap=TeachingAssistantPermission.objects.get(id=int(request.POST.get('permission_id')))
        if taap.enrolment.course!=course:
            return JsonResponse({"message": "The TA was never enroled in the course"}, status=400)
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
        announcements=Announcement.objects.filter(course=course).order_by('-id')
        quizes=Quiz.objects.filter(course=course).order_by('-id')
        TA_permissions=TeachingAssistantPermission.objects.filter(enrolment__course=course)
        ta_contacts=[]
        for each in enrolments:
            if each.userType.userTypeCode==settings.CODE_TA:
                ta_contacts.append(TeachingAssistant.objects.get(user=each.user))
        context={"course": course, "enrolments": enrolments, "announcements": announcements, "quizes": quizes,"TA_permissions": TA_permissions, "ta_contacts": ta_contacts}
        return render(request,"faculty/view_course.html",context=context)

# Not advised to uncomment the return render because user have to g back in order to avail other features.
def add_student_ta(request,course_id):
    faculty=basicChecking(request)
    course=False
    if faculty==False:
        try:
            ta=TeachingAssistant.objects.get(user=request.user)
            enrolment=False
            try:
                course=Course.objects.get(id=int(course_id))
                enrolment=Enrolment.objects.get(user=request.user, course=course)
                permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
                if (not permissions.isMainTA) and (not permissions.canAnnounce):
                    return JsonResponse({"message": "It seems you have not been given permission to add students and ta's in the class.."}, status=400)
            except:
                return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)
        except:
            return redirect('home')
    else:
        try:
            course=Course.objects.get(id=int(course_id))
            if course.instructor!=request.user:
                return JsonResponse({"message": "Course was not found on this server"}, status=400)
        except:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)

    if request.method!="POST":
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    user_re=int(request.POST.get("user"))
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
            return JsonResponse({"message": "Not an excel or csv file"})
            # if user_re==2:
            #     permissions=TeachingAssistantPermission.objects.get(enrolment=Enrolment.objects.get(user=request.user, course=course))
            #     return render(request,"ta/view_course.html",context={"course": course, "message": "Not an excel or csv file", "permissions": permissions})
            # return render(request,"faculty/view_course.html",context={"course": course, "message": "Not an excel or csv file"})
        return add_student_ta_helper(request, data, course, user_re)
    return JsonResponse({"message": "An Error Occured. Try Again!"}, status=400)
    # if user_re==2:
    #     permissions=TeachingAssistantPermission.objects.get(enrolment=Enrolment.objects.get(user=request.user, course=course))
    #     return render(request,"ta/view_course.html",context={"course": course, "message": "Error Occured.", "permissions": permissions})
    # return render(request,"faculty/view_course.html",context={"course": course, "message": "Error Occured."})

def add_student_ta_helper(request, data, course, user_re):
    if 'Email' not in data.columns and 'Username' not in data.columns:
        return JsonResponse({"message": "Email column was not found in the file."})
        # if user_re==2:
        #     permissions=TeachingAssistantPermission.objects.get(enrolment=Enrolment.objects.get(user=request.user, course=course))
        #     return render(request,"ta/view_course.html",context={"course": course, "message": "Email column was not found in the file.", "permissions": permissions})
        # return render(request,"faculty/view_course.html",context={"course": course, "message": "Email column was not found in the file."})     
    emailGiven=True 
    if 'Email' not in data.columns:
        emailGiven=False
    if 'Role' not in data.columns:
        return JsonResponse({"message": "Account Type column was not found in the file."})
        # if user_re==2:
        #     permissions=TeachingAssistantPermission.objects.get(enrolment=Enrolment.objects.get(user=request.user, course=course))
        #     return render(request,"ta/view_course.html",context={"course": course, "message": "Email column was not found in the file.", "permissions": permissions})
        # return render(request,"faculty/view_course.html",context={"course": course, "message": "Account Type column was not found in the file."})      

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
            enrolment=Enrolment.objects.create(user=user, course=course, userType=userType)
            TeachingAssistantPermission.objects.create(enrolment=enrolment)
            subject="Enrolment Confirmation in DadamLive"
            message="You have been enroled as "+role+" in "+course.courseName+" in DadamLive. You can leave the course if you want but all the progress including tests will be lost if you do so."
            try:
                Email_thread(subject,message,email).start()
            except:
                print("Unable to send email")
        else:
            field_with_unknown_values.append(i+1)

    if len(field_with_unknown_values)==0 and len(field_with_duplicate_data)==0:
        return JsonResponse({"message": "All users have been added successfully."})
        # if user_re==2:
        #     permissions=TeachingAssistantPermission.objects.get(enrolment=Enrolment.objects.get(user=request.user, course=course))
        #     return render(request,"ta/view_course.html",context={"course": course, "message": "All users have been added successfully.", "permissions": permissions})
        # return render(request,"faculty/view_course.html",context={"course": course, "message": "All users have been added successfully."})    
    elif len(field_with_unknown_values)==0:  
        error="Rows with duplicate data are : "+str(field_with_duplicate_data)+" . You can cross-verify, users have been added from rest of the rows."
    elif len(field_with_duplicate_data)==0:  
        error="Rows with empty email and empty username or undefined role are : "+str(field_with_unknown_values)+" . You can cross-verify, users have been added from rest of the rows."
    else:
        error1="Rows with duplicate data are : "+str(field_with_duplicate_data)+" ."
        error2="Rows with empty email and empty username or undefined role are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, users have been added from rest of the rows."
        error=error1+"\n"+error2
    return JsonResponse({"message": error})
    # if user_re==2:
    #     permissions=TeachingAssistantPermission.objects.get(enrolment=Enrolment.objects.get(user=request.user, course=course))
    #     return render(request,"ta/view_course.html",context={"course": course, "message": error, "permissions": permissions})
    # return render(request,"faculty/view_course.html",context={"course": course, "message": error})

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
        Announcement.objects.create(course=course, message=message, created_by=request.user)
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
        if end_date<start_date:
            return JsonResponse({"error": "Start time must be less than end time"}, status=400)
        if start_date<datetime.datetime.now():
            return JsonResponse({"error": "Quiz can only be started in future"}, status=400)
        quiz=Quiz.objects.create(course=course, quiz_name=quiz_name, start_date=start_date, end_date=end_date, hidden=hide)
        TestEnder(quiz.id).start()
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
            quiz.maximum_marks+=max_marks_written
            quiz.save()

        elif int(question_type)==2:
            question_written=request.POST.get("question_written")
            max_marks_written=float(request.POST.get("max_marks_written"))
            WrittenQuestion.objects.create(quiz=quiz, question=question_written, maximum_marks=max_marks_written)
            quiz.maximum_marks+=max_marks_written
            quiz.save()

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
        submissions=0
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
                quiz.maximum_marks+=max_marks_written
                quiz.save()
        elif typeOfQ=="Objective":
            try:
                MCQ.objects.get(quiz=quiz, question=question_written, maximum_marks=max_marks_written)
                field_with_duplicate_data.append(i+1)
            except:
                try:
                    scheme=data["Marking Scheme"][i]
                    mcq=MCQ.objects.create(quiz=quiz, question=question_written, maximum_marks=max_marks_written, markingScheme=scheme)
                    quiz.maximum_marks+=max_marks_written
                    quiz.save()
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
                    correct_answers=[]
                    try:
                        correct_answers.append(float(data["Correct Options"][i]))
                    except:
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
            return JsonResponse({"message": "This option is not available during quiz"}, status=400)
        quiz.hidden=True
    quiz.save()
    return redirect('manage_quiz',quiz_id)

def change_prev_status(request,quiz_id):
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

    if quizOngoing(quiz)==False:
        return JsonResponse({"message": "This option is not available during quiz"}, status=400)
    if quiz.disable_previous:
        quiz.disable_previous=False
    else:
        quiz.disable_previous=True
    quiz.save()
    return redirect('manage_quiz',quiz_id)

# False if quiz ongoing
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

# True if quiz ended
def quizEnded(quiz):
    if quiz.end_date.date()<datetime.datetime.now().date():
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
    if marked[0]=='':
        return 0.0
    answer.sort()
    marked.sort()
    if mcq.markingScheme==2:
        if len(answer)!=len(marked):
            return mcq.negativeMarks
        for i in range(len(answer)):
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

def detect_web_sources(request,quiz_id):
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
        return JsonResponse({"message": "Web Source can not be detected until quiz gets over."}, status=400)
    if quiz.webDetectionDone:
        return JsonResponse({"message": "Web Source Detection has been done already."}, status=400)

    submissions=Submission.objects.filter(quiz=quiz)
    written=WrittenQuestion.objects.filter(quiz=quiz)
    for s in submissions:
        averagePlagiarism=0
        n=0
        for w in written:
            try:
                p=PartOfSubmission.objects.get(submission=s, question_id=int(w.id))
                marked=p.answer

                # If length of answer is less than 20 then we are not checking for plag
                if len(marked)<20:
                    pass

                detect=sendPlagRequest(marked)
                p.plagPercent=float(detect[0])
                p.sources=str(detect[1])
                p.save()
                averagePlagiarism=averagePlagiarism*n
                averagePlagiarism+=float(detect[0])
                n+=1
                averagePlagiarism=averagePlagiarism/n
            except:
                pass
        s.averagePlagiarism=averagePlagiarism
        s.save()
    quiz.webDetectionDone=True
    quiz.save()
    return redirect('manage_quiz', quiz_id)

def match_student_answers(request, quiz_id):
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
        return JsonResponse({"message": "Student Answers can not be matched until quiz gets over."}, status=400)
    if quiz.studentAnswersMatched:
        return JsonResponse({"message": "Web Source Detection has been done already."}, status=400)

    submissions=Submission.objects.filter(quiz=quiz)
    written=WrittenQuestion.objects.filter(quiz=quiz)
    try:
        for w in written:
            all_parts=[]
            all_answers=[]
            for s in submissions:
                try:
                    p=PartOfSubmission.objects.get(submission=s, question_id=int(w.id))
                    all_parts.append(p)
                    all_answers.append(p.answer)
                except:
                    pass
            vect=TfidfVectorizer(min_df=1, stop_words="english")                                                                                                                                                                                                   
            tfidf=vect.fit_transform(all_answers)                                                                                                                                                                                                                       
            similarityMatrix=(tfidf*tfidf.T).toarray()
            for i in range(len(similarityMatrix)):
                matrix1=[]
                matrix2=[]
                for j in range(len(similarityMatrix[0])):
                    if i==j:
                        continue
                    matrix1.append(all_parts[j].id)
                    matrix2.append(int(100*similarityMatrix[i][j]))
                p=PartOfSubmission.objects.get(id=all_parts[i].id)
                p.sub_id=matrix1
                p.percentage_match=matrix2
                if len(matrix2)>1:
                    p.maxPlagFromOtherStud=max(matrix2)
                elif len(matrix2)==1:
                    p.maxPlagFromOtherStud=matrix2[0]
                p.save()
    except:
        return JsonResponse({"message": "Unable to do that because there not enough submissions"}, status=400)

    quiz.studentAnswersMatched=True
    quiz.save()
    return redirect('manage_quiz', quiz_id)

def sendPlagRequest(data):
    data = {'key': settings.API_KEY_WEB_SOURCE, 'data': str(data)}
    r=requests.post(url = settings.WEB_SOURCE_API, data=data)
    r=r.json()
    sources=[]
    for each in r["sources"]:
        sources.append(each["link"])
    return [r["plagPercent"], str(sources)]

def view_submission(request, submission_id):
    faculty=basicChecking(request)
    ta=basicCheckingWithTA(request)
    if faculty==False and ta==False:
        return redirect('home')
    submission=""
    quiz=""
    permissions=""
    try:
        submission=Submission.objects.get(id=int(submission_id))
        quiz=submission.quiz
        if faculty!=False and submission.quiz.course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
        if ta!=False:
            enrolment=Enrolment.objects.get(user=ta.user, course=quiz.course)
            permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
            if (not permissions.isMainTA) and (not permissions.canManageQuiz) and (not permissions.canCheckAnswerSheets):
                return JsonResponse({"message": "It seems you have not been given permission to check answer sheets.."}, status=400)
    except:
        return JsonResponse({"message": "Submission was not found on this server"}, status=400)
    
    if quiz.quizHeld==False:
        return JsonResponse({"message": "Submission can not be viewed until quiz gets over."}, status=400)
    parts=PartOfSubmission.objects.filter(submission=submission)
    written=WrittenQuestion.objects.filter(quiz=quiz)
    mcq=MCQ.objects.filter(quiz=quiz)
    attempt=False
    try:
        attempt=IllegalAttempt.objects.get(submission=submission)
    except:
        attempt=IllegalAttempt.objects.create(submission=submission)
    return render(request, "faculty/view_submission.html", context={"parts": parts, "submission": submission, "quiz": quiz, "written": written, "mcq": mcq, "attempt": attempt})

def upload_marks(request):
    faculty=basicChecking(request)
    ta=basicCheckingWithTA(request)
    if faculty==False and ta==False:
        return redirect('home')
    submission=""
    part=""
    quiz=""
    permissions=""
    try:
        part=PartOfSubmission.objects.get(id=int(request.GET.get("part_id")))
        quiz=part.submission.quiz
        if faculty!=False and quiz.course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
        if ta!=False:
            enrolment=Enrolment.objects.get(user=ta.user, course=quiz.course)
            permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
            if (not permissions.isMainTA) and (not permissions.canManageQuiz) and (not permissions.canCheckAnswerSheets):
                return JsonResponse({"message": "It seems you have not been given permission to check answer sheets.."}, status=400)
    except:
        return JsonResponse({"message": "Submission was not found on this server"}, status=400)

    if quiz.quizHeld==False:
        return JsonResponse({"message": "Marks can not be assigned until quiz gets over."}, status=400)
    marks=float(request.GET.get("marks"))
    if marks>WrittenQuestion.objects.get(id=int(part.question_id)).maximum_marks:
        return JsonResponse({"message": "You can't assign more than maximum marks for the question"}, status=400)
    submission=part.submission
    submission.score=submission.score-part.mark+marks
    submission.save()
    part.mark=marks
    part.save()
    return JsonResponse({"message": "Marks assigned for the question"}, status=200)

def get_submission(request):
    faculty=basicChecking(request)
    ta=basicCheckingWithTA(request)
    if faculty==False and ta==False:
        return redirect('home')
    submission=""
    part=""
    quiz=""
    permissions=""
    try:
        part=PartOfSubmission.objects.get(id=int(request.GET.get("part_id")))
        quiz=part.submission.quiz
        if faculty!=False and quiz.course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
        if ta!=False:
            enrolment=Enrolment.objects.get(user=ta.user, course=quiz.course)
            permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
            if (not permissions.isMainTA) and (not permissions.canManageQuiz) and (not permissions.canCheckAnswerSheets):
                return JsonResponse({"message": "It seems you have not been given permission to check answer sheets.."}, status=400)
    except:
        return JsonResponse({"message": "Submission was not found on this server"}, status=400)
    
    if quiz.quizHeld==False:
        return JsonResponse({"message": "Answer can not be viewed until quiz gets over."}, status=400)

    other_subs=[]
    for each in part.sub_id:
        try:
            p=PartOfSubmission.objects.get(id=int(each))
            other_subs.append(p)
        except:
            pass

    my_sub=serializers.serialize('json', [part])
    other_subs=serializers.serialize('json', other_subs)

    return JsonResponse({"message": "200", "my_sub": my_sub, "other_subs": other_subs})

def images_for_illegal_att(request, submission_id):
    faculty=basicChecking(request)
    ta=basicCheckingWithTA(request)
    if faculty==False and ta==False:
        return redirect('home')
    submission=""
    quiz=""
    permissions=""
    try:
        submission=Submission.objects.get(id=int(submission_id))
        quiz=submission.quiz
        if faculty!=False and submission.quiz.course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
        if ta!=False:
            enrolment=Enrolment.objects.get(user=ta.user, course=quiz.course)
            permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
            if (not permissions.isMainTA) and (not permissions.canManageQuiz) and (not permissions.canCheckAnswerSheets):
                return JsonResponse({"message": "It seems you have not been given permission to check answer sheets.."}, status=400)
    except:
        return JsonResponse({"message": "Submission was not found on this server"}, status=400)
    
    if quiz.quizHeld==False:
        return JsonResponse({"message": "Images can not be viewed until quiz gets over."}, status=400)

    images=ImagesForActivity.objects.filter(submission=submission)

    return render(request, "faculty/view_images.html", {"quiz": quiz, "submission": submission, "images": images})

def marks_given_for_all_q(request):
    faculty=basicChecking(request)
    ta=basicCheckingWithTA(request)
    if faculty==False and ta==False:
        return redirect('home')
    submission=""
    quiz=""
    permissions=""
    try:
        submission=Submission.objects.get(id=int(request.GET.get("submission_id")))
        quiz=submission.quiz
        if faculty!=False and submission.quiz.course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
        if ta!=False:
            enrolment=Enrolment.objects.get(user=ta.user, course=quiz.course)
            permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
            if (not permissions.isMainTA) and (not permissions.canManageQuiz) and (not permissions.canCheckAnswerSheets):
                return JsonResponse({"message": "It seems you have not been given permission to check answer sheets.."}, status=400)
    except:
        return JsonResponse({"message": "Submission was not found on this server"}, status=400)
    
    if quiz.quizHeld==False:
        return JsonResponse({"message": "Submission can not be viewed until quiz gets over."}, status=400)
    
    submission.marks_assigned=True
    submission.save()
    return redirect(view_submission, request.GET.get("submission_id"))

def get_report(request, course_id):
    faculty=basicChecking(request)
    ta=basicCheckingWithTA(request)
    if faculty==False and ta==False:
        return redirect('home')
    course=""
    try:
        course=Course.objects.get(id=int(course_id))
        if faculty!=False and course.instructor!=request.user:
            return JsonResponse({"message": "Course was not found on this server"}, status=400)
        if ta!=False:
            Enrolment.objects.get(user=ta.user, course=course)
    except:
        return JsonResponse({"message": "Course was not found on this server"}, status=400)
    
    report_dataframe=generate_report(course)
    excelFilename=course.courseName+" Report "+str(datetime.datetime.now().date())+".xlsx"
    
    with BytesIO() as b:
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        report_dataframe.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        filename=excelFilename
        response=HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition']='attachment; filename=%s' % filename
        return response
    
def generate_report(course):
    df=pd.DataFrame()
    col_names=["Roll Number"]
    data=[]
    temp=[]
    users=[]
    userType=UserType.objects.get(userTypeCode=int(settings.CODE_STUDENT))
    enrolments=Enrolment.objects.filter(course=course, userType=userType)
    for en in enrolments:
        temp.append(en.user.username)
        users.append(en.user)
    data.append(temp)
    quiz=Quiz.objects.filter(course=course)
    total=[]
    for q in quiz:
        col_names.append(q.quiz_name)
        temp=[]
        for en in enrolments:
            try:
                submission=Submission.objects.get(quiz=q, user=en.user)
                temp.append(submission.score)
            except:
                temp.append(0)
        data.append(temp)
        if len(total)==0:
            total=temp
        else:
            total1=[]
            for i in range(len(total)):
                total1.append(total[i]+temp[i])
            total=total1
    
    col_names.append("Total Score")
    data.append(total)
    
    for i in range(len(col_names)):
        df[col_names[i]]=data[i]            
    return df 
    

def upload_course_image(request):
    faculty=basicChecking(request)
    if faculty==False:
        return redirect('home')
    if request.method!="POST":
        return JsonResponse({"message": "Not a post request"}, status=400)
    course=False
    try:
        course=Course.objects.get(id=int(request.POST.get("course_id")))
        if course.instructor!=request.user:
            return JsonResponse({"message": "Course not found"}, status=400)
    except:
        return JsonResponse({"message": "Course not found"}, status=400)
    form = CoursePhotoForm(request.POST,request.FILES)
    if form.is_valid():
        try:
            image=request.POST.get("image")
            if image!="":
                course.image=form.cleaned_data.get("image")
                course.save()
            return redirect('dashboardFaculty')
        except:
            return redirect('dashboardFaculty')
        
class TestEnder(Thread):
    def __init__(self, quiz_id):
        self.quiz_id=quiz_id
        Thread.__init__(self)

    def run(self):
        try:
            quiz=Quiz.objects.get(id=int(self.quiz_id))
        except:
            return False
        number=(quiz.end_date-datetime.datetime.now()).total_seconds() + 20
        save_test_state(quiz.id, schedule=int(number))

@background(schedule=60)
def save_test_state(quiz_id):
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
    except:
        return False
    if quizEnded(quiz):
        quiz.quizHeld=True
        quiz.save()
    else:
        TestEnder(quiz.id).start()

def view_profile_fa(request):
    if not request.user.is_authenticated:
        return redirect('login_request') 

    if request.method=="POST":
        user=User.objects.get(id=request.user.id)
        user.first_name=request.POST.get("first_name")
        user.last_name=request.POST.get("last_name")
        user.save()
        return redirect('view_profile_fa')
    return render(request,"faculty/view_profile.html",context={})

def change_password_fa(request):
    if not request.user.is_authenticated:
        return redirect('login_request') 

    if request.method=="POST":
        user=User.objects.get(id=request.user.id)
        password=request.POST.get("password2")
        user.set_password(password)
        user.save()
        return JsonResponse({"success": "Password changed"}, status=200)
    return render(request,"faculty/change_password.html",context={})