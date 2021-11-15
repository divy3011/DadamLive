from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
import math,random
from home.models import *
from threading import *
import pandas as pd
from .forms import FileForm
# Create your views here.

class Email_thread(Thread):
    def __init__(self,subject,message,email):
        self.email=email
        self.subject=subject
        self.message=message
        Thread.__init__(self)

    def run(self):
        SENDMAIL(self.subject,self.message,self.email)

# def SENDMAIL(subject, message, email):
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = [email, ]
#     checker = User.objects.get(email=email)
#     username = checker.username
#     html_content = render_to_string("home/email.html",{'message': message, 'user_name': username})
#     text_content = strip_tags(html_content)
#     email = EmailMultiAlternatives(subject,text_content,email_from,recipient_list)
#     email.attach_alternative(html_content,"text/html")
#     email.send()
#     # return render(request,'home/email.html',{'title':'send an email'})
#     # send_mail( subject, message, email_from, recipient_list )

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
        if info.userType.userTypeCode==settings.CODE_STAFF:
            staff=Staff.objects.get(user=request.user)
            return staff
    except:
        return False

def dashboardStaff(request):
    staff=basicChecking(request)
    if staff==False:
        return redirect('home')
    return render(request,"staff/dashboard.html",context={"staff": staff})

def add_users(request):
    staff=basicChecking(request)
    if staff==False:
        return redirect('home')
    if staff.canAddUsers==False:
        return redirect('dashboardStaff')
    if request.method=="POST":
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
                return render(request,"staff/add_users.html",context={"staff": staff, "message": "Not an excel or csv file"})      
            return add_users_helper(request, data, staff)
        return render(request,"staff/add_users.html",context={"staff": staff, "message": "Error Occured."})
    else:
        return render(request,"staff/add_users.html",context={"staff": staff})

def add_users_helper(request, data, staff):
    if 'Email' not in data.columns:
        return render(request,"staff/add_users.html",context={"staff": staff, "message": "Email column was not found in the file."})      
    if 'Username' not in data.columns:
        return render(request,"staff/add_users.html",context={"staff": staff, "message": "Username column was not found in the file."})      
    if 'Account Type' not in data.columns:
        return render(request,"staff/add_users.html",context={"staff": staff, "message": "Account Type column was not found in the file."})      

    total_accounts=len(data['Email'])
    field_with_unknown_values=[]
    field_with_duplicate_data=[]
    for i in range(total_accounts):
        email=data['Email'][i]
        username=data['Username'][i]
        account_type=data['Account Type'][i]

        if email!="" and username!="" and account_type!="":
            try:
                User.objects.get(username=username)
                field_with_duplicate_data.append(i+1)
                continue
            except:
                pass
            try:
                User.objects.get(email=email)
                field_with_duplicate_data.append(i+1)
                continue
            except:
                pass
            if account_type!='Student' and account_type!='Staff' and account_type!="Faculty" and account_type!="TA":
                field_with_unknown_values.append(i+1)
                continue
            password=generate_random_password(10)
            User.objects.create(username=username, email=email)
            user=User.objects.get(username=username, email=email)
            user.set_password(password)
            user.save()
            subject="Welcome to DadamLive!"
            message="Your email has been used to create "+str(account_type)+" account in DadamLive. Login Credentials are as follows : \nUsername : "+str(username)+"\nPassword : "+password+"\nPassword is auto generated so it is recommended to change ASAP."
            try:
                Email_thread(subject,message,email).start()
            except:
                print("Unable to send email")
            if account_type == "Student":
                userType=UserType.objects.get(userTypeCode=int(settings.CODE_STUDENT))
                userInformation=UserInformation.objects.create(user=user, userType=userType)
                Student.objects.create(user=user, userInformation=userInformation)
            if account_type == "Faculty":
                userType=UserType.objects.get(userTypeCode=int(settings.CODE_FACULTY))
                userInformation=UserInformation.objects.create(user=user, userType=userType)
                Faculty.objects.create(user=user, userInformation=userInformation)
            if account_type == "TA":
                userType=UserType.objects.get(userTypeCode=int(settings.CODE_TA))
                userInformation=UserInformation.objects.create(user=user, userType=userType)
                TeachingAssistant.objects.create(user=user, userInformation=userInformation)
            if account_type == "Staff":
                userType=UserType.objects.get(userTypeCode=int(settings.CODE_STAFF))
                userInformation=UserInformation.objects.create(user=user, userType=userType)
                Staff.objects.create(user=user, userInformation=userInformation)
        else:
            field_with_unknown_values.append(i+1)

    if len(field_with_unknown_values)==0 and len(field_with_duplicate_data)==0:
        return render(request,"staff/add_users.html",context={"staff": staff, "message": "All accounts have been created successfully."})    
    elif len(field_with_unknown_values)==0:  
        error="Rows with duplicate data are : "+str(field_with_duplicate_data)+" . You can cross-verify, accounts have been created from rest of the rows."
    elif len(field_with_duplicate_data)==0:  
        error="Rows with empty email or empty username or undefined account type are : "+str(field_with_unknown_values)+" . You can cross-verify, accounts have been created from rest of the rows."
    else:
        error1="Rows with duplicate data are : "+str(field_with_duplicate_data)+" ."
        error2="Rows with empty email or empty username or undefined account type are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, accounts have been created from rest of the rows."
        error=error1+"\n"+error2
    return render(request,"staff/add_users.html",context={"staff": staff, "message": error})      

def generate_random_password(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$!"
    password = ""
    for i in range(n) :
        password += digits[math.floor(random.random() * 62)]
    password+='@'
    return password