from django.db import models
from django.contrib.auth.models import User
import datetime
from home.models import UserType
from django_mysql.models import ListTextField
from pytz import timezone

# Create your models here.
class Course(models.Model):
    instructor=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image=models.ImageField(upload_to='post_images/', default="demo.jpg", null=True)
    courseName=models.CharField(null=True, max_length=200)
    created_on=models.DateTimeField(default=datetime.datetime.now(timezone('Asia/Kolkata')))

    def __str__(self):
        return self.courseName

class Enrolment(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    userType=models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    enrolled_on=models.DateTimeField(default=datetime.datetime.now(timezone('Asia/Kolkata')))

    def __str__(self):
        return self.course.courseName

class TeachingAssistantPermission(models.Model):
    enrolment=models.ForeignKey(Enrolment, on_delete=models.CASCADE, null=True, blank=True)

    isMainTA=models.BooleanField(default=False)
    # If this feature is on the TA is like faculty and can do all those things that a faculty can do.

    canManageTAPermissions=models.BooleanField(default=False)
    # Very sensittive feature - Must not be given to every TA

    canCheckAnswerSheets=models.BooleanField(default=True)
    # Must be given to maximum TA otherwise who will check the answer sheets

    canAnnounce=models.BooleanField(default=True)

    canManageQuiz=models.BooleanField(default=False)
    # Includes creating quiz creating questions, quiz hidder, disable previous and all the features.

    def __str__(self):
        return self.enrolment.course.courseName

class Quiz(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    quiz_name=models.CharField(null=True, max_length=500)
    start_date=models.DateTimeField(default=datetime.datetime.now(timezone('Asia/Kolkata')))
    end_date=models.DateTimeField(default=datetime.datetime.now(timezone('Asia/Kolkata')))
    created_on=models.DateTimeField(default=datetime.datetime.now(timezone('Asia/Kolkata')))
    quizHeld=models.BooleanField(default=False)
    hidden=models.BooleanField(default=True)
    mcqMarksGenerated=models.BooleanField(default=False)
    webDetectionDone=models.BooleanField(default=False)
    studentAnswersMatched=models.BooleanField(default=False)
    maximum_marks=models.FloatField(default=0)
    disable_previous=models.BooleanField(default=False)

    def __str__(self):
        return self.course.courseName

class MCQ(models.Model):
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    question=models.TextField(null=True)

    options=ListTextField(base_field=models.CharField(default="", max_length=100000), size=10)
    #Rearrange the array to make correct answer as first index

    correct_answers=ListTextField(base_field=models.IntegerField(default=0), size=10)
    note=models.TextField(null=True, max_length=500)
    maximum_marks=models.FloatField(null=True, blank=True, default=1)
    max_time_limit_allowed=models.IntegerField(default=600, null=True, blank=True)
    #In seconds for obvious. Default is 10 minutes

    markingScheme=models.IntegerField(default=1, null=True)
    # 1 - Partial with negative consideration
    # 2 - No partial

    negativeMarks=models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.quiz.course.courseName

class WrittenQuestion(models.Model):
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    question=models.TextField(null=True, max_length=500)
    note=models.TextField(null=True, max_length=500)
    maximum_marks=models.FloatField(null=True, blank=True, default=1)
    max_time_limit_allowed=models.IntegerField(default=600, null=True, blank=True)
    #In seconds for obvious. Default is 10 minutes

    def __str__(self):
        return self.quiz.course.courseName
    
class Submission(models.Model):
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    score=models.FloatField(default=0)
    submitted=models.BooleanField(default=False)

    ip_address=models.CharField(null=True, max_length=50)

    averagePlagiarism=models.FloatField(default=0)
    # Considering written questions only not the mcq ones

    # Duplicate entry, to be removed
    marks_assigned=models.BooleanField(default=False)

class IllegalAttempt(models.Model):
    submission=models.ForeignKey(Submission, on_delete=models.CASCADE, null=True, blank=True)

    browserSwitched=models.IntegerField(null=True, default=0)
    # Activity Number 1

    # These number are with respect to the time delay in which image is sent to the server
    # So, like if numberOfTimesMultiplePersonsDetected=2 and timeDelay=10sec then multiple persons 
    # were there for 20 seconds

    numberOfTimesMultiplePersonsDetected=models.IntegerField(null=True, default=0)
    #Activity Number 2

    noPersonDetected=models.IntegerField(null=True, default=0)
    #Activity Number 3

    usingSomeoneElseIP=models.BooleanField(default=False)
    #Activity Number 4

    numberOfTimesAudioDetected=models.IntegerField(null=True, default=0)
    #Activity Number 5

    noOfTimesMobileDetected=models.IntegerField(null=True, default=0)
    # Activity Number 6

    screenShared=models.BooleanField(default=True)
    # Activity Number 7

    screenSharingTurnedOff=models.IntegerField(null=True, default=0)
    # Activity Number 8
    
class ImagesForActivity(models.Model):
    submission=models.ForeignKey(Submission, on_delete=models.CASCADE, null=True, blank=True)

    image=models.ImageField(upload_to='images_for_activity/', null=True)

    typeAct=models.IntegerField(null=True, default=0)
    # Same number as followed in Illegal Attempts

    # 1 - Tab Changed
    # 2 - Multiple Faces
    # 6 - Mobile Detected

    timeStamp=models.DateTimeField(default=datetime.datetime.now(timezone('Asia/Kolkata')))


class PartOfSubmission(models.Model):
    submission=models.ForeignKey(Submission, on_delete=models.CASCADE, null=True, blank=True)
    question_id=models.IntegerField(null=True, default=0)
    answer=models.TextField(default="", null=True)
    mark=models.FloatField(default=0.0)

    question_type=models.IntegerField(null=True, default=2)
    #1 - MCQ
    #2 - Written Question

    plagPercent=models.FloatField(default=0)
    sources=models.CharField(null=True, blank=True, max_length=10000)
    sub_id=ListTextField(base_field=models.IntegerField(default=0), size=1000, null=True)
    percentage_match=ListTextField(base_field=models.IntegerField(default=0), size=1000, null=True)
    maxPlagFromOtherStud=models.FloatField(default=0)
    answer_locked=models.BooleanField(default=False)


class Announcement(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    created_by=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message=models.CharField(null=True, max_length=5000)
    created_on=models.DateTimeField(default=datetime.datetime.now(timezone('Asia/Kolkata')))

    def __str__(self):
        return self.course.courseName