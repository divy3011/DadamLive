from django.http.response import JsonResponse
from django.core import serializers
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from .models import *
from faculty.models import *
from threading import *
from home.models import *
import pandas as pd
from staff.forms import FileForm
from faculty.views import quizOngoing
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

def ta_manage_quiz(request, quiz_id):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolment=False
    course=False
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        course=quiz.course
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canManageQuiz) and (not permissions.canCheckAnswerSheets):
            return JsonResponse({"message": "It seems you have not been given permission to manage Quiz in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)
    
    manager=False
    if permissions.isMainTA or permissions.canManageQuiz:
        manager=True
    
    if request.method=="POST":
        if manager==False:
            return JsonResponse({"message": "Permission Denied"}, status=400)
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
                    return render(request,"ta/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": "Not an excel or csv file", "submissions": submissions, "permissions": permissions})
                return manage_quiz_helper(request, data, quiz, permissions)
        return redirect('ta_manage_quiz',quiz_id)
    else:
        mcq=MCQ.objects.filter(quiz=quiz)
        written=WrittenQuestion.objects.filter(quiz=quiz)
        submissions=0
        if quiz.quizHeld:
            submissions=Submission.objects.filter(quiz=quiz)
        return render(request,"ta/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "submissions": submissions, "permissions": permissions})

def manage_quiz_helper(request, data, quiz, permissions):
    mcq=MCQ.objects.filter(quiz=quiz)
    written=WrittenQuestion.objects.filter(quiz=quiz)
    if 'Question Type' not in data.columns and 'Question' not in data.columns and 'Maximum Marks' not in data.columns:
        return render(request,"ta/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": "Either of Question Type, Question or Maximum Marks Column was not found in the file.", "permissions": permissions})

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
        return render(request,"ta/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": "All questions have been added successfully.", "permissions": permissions})    
    elif len(field_with_unknown_values)==0:  
        error="Rows with duplicate data are : "+str(field_with_duplicate_data)+" . You can cross-verify, questions have been added from rest of the rows."
    elif len(field_with_duplicate_data)==0:  
        error="Rows with empty or not found values are : "+str(field_with_unknown_values)+" . You can cross-verify, questions have been added from rest of the rows."
    else:
        error1="Rows with duplicate data are : "+str(field_with_duplicate_data)+" ."
        error2="Rows with empty or not found values are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, questions have been added from rest of the rows."
        error=error1+"\n"+error2
    return render(request,"ta/manage_quiz.html",context={"quiz": quiz, "mcq": mcq, "written": written, "message": error, "permissions": permissions})

def ta_change_quiz_status(request,quiz_id):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolment=False
    course=False
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        course=quiz.course
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canManageQuiz):
            return JsonResponse({"message": "It seems you have not been given permission to hide Quiz in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)

    if quiz.hidden:
        quiz.hidden=False
    else:
        if quizOngoing(quiz)==False:
            return JsonResponse({"message": "This option is not available during quiz"}, status=400)
        quiz.hidden=True
    quiz.save()
    return redirect('ta_manage_quiz',quiz_id)

def ta_change_prev_status(request,quiz_id):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolment=False
    course=False
    quiz=""
    try:
        quiz=Quiz.objects.get(id=int(quiz_id))
        course=quiz.course
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canManageQuiz):
            return JsonResponse({"message": "It seems you have not been given permission to hide Quiz in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)

    if quizOngoing(quiz)==False:
        return JsonResponse({"message": "This option is not available during quiz"}, status=400)
    if quiz.disable_previous:
        quiz.disable_previous=False
    else:
        quiz.disable_previous=True
    quiz.save()
    return redirect('ta_manage_quiz',quiz_id)

def ta_quiz_analysis(request):
    ta=basicChecking(request)
    if ta[0]==False:
        return ta[1]
    enrolment=False
    course=False
    quiz=""
    if request.method!="POST":
        return JsonResponse({"message": "Unable to process this request."}, status=400)
    try:
        quiz=Quiz.objects.get(id=int(request.POST.get("quiz_id")))
        course=quiz.course
        enrolment=Enrolment.objects.get(user=request.user, course=course)
        permissions=TeachingAssistantPermission.objects.get(enrolment=enrolment)
        if (not permissions.isMainTA) and (not permissions.canManageQuiz):
            return JsonResponse({"message": "It seems you have not been given permission to hide Quiz in the class.."}, status=400)
    except:
        return JsonResponse({"message": "Course was not found on this server or you aren't assigned as TA by the faculty."}, status=400)
    
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

def view_profile_ta(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "Please login before viewing profile."}, status=400)
    ta=TeachingAssistant.objects.get(user=request.user)
    if request.method=="POST":
        user=User.objects.get(id=request.user.id)
        user.first_name=request.POST.get("first_name")
        user.last_name=request.POST.get("last_name")
        user.save()
        contact_number=request.POST.get("contact_number")

        return redirect('view_profile_ta')
    return render(request,"ta/view_profile.html",context={"ta": ta})