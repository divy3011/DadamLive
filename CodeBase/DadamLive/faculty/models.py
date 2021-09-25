from django.db import models
from django.contrib.auth.models import User
import datetime
from home.models import UserType
from django_mysql.models import ListTextField

# Create your models here.
class Course(models.Model):
    instructor=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    courseName=models.CharField(null=True, max_length=200)
    created_on=models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.courseName

class Enrolment(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    userType=models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    enrolled_on=models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.course.courseName

class Quiz(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    quiz_name=models.CharField(null=True, max_length=500)
    start_date=models.DateTimeField(default=datetime.datetime.now())
    end_date=models.DateTimeField(default=datetime.datetime.now())
    created_on=models.DateTimeField(default=datetime.datetime.now())
    quizHeld=models.BooleanField(default=False)
    hidden=models.BooleanField(default=True)

    def __str__(self):
        return self.course.courseName

class MCQ(models.Model):
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    question=models.CharField(null=True, max_length=500)

    options=ListTextField(base_field=models.CharField(default="", max_length=1000), size=10)
    #Rearrange the array to make correct answer as first index

    correct_answers=ListTextField(base_field=models.IntegerField(default=0), size=10)
    note=models.CharField(null=True, max_length=500)
    maximum_marks=models.FloatField(null=True, blank=True, default=1)
    max_time_limit_allowed=models.IntegerField(default=600, null=True, blank=True)
    #In seconds for obvious. Default is 10 minutes

    def __str__(self):
        return self.quiz.course.courseName

class WrittenQuestion(models.Model):
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    question=models.CharField(null=True, max_length=500)
    note=models.CharField(null=True, max_length=500)
    maximum_marks=models.FloatField(null=True, blank=True, default=1)
    max_time_limit_allowed=models.IntegerField(default=600, null=True, blank=True)
    #In seconds for obvious. Default is 10 minutes

    def __str__(self):
        return self.quiz.course.courseName
    
class Submission(models.Model):
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    answers_marked=ListTextField(base_field=models.CharField(default="", max_length=10000), size=100)
    question_id=ListTextField(base_field=models.CharField(default="", max_length=100), size=100)

    question_type=ListTextField(base_field=models.CharField(default="", max_length=10), size=100)
    #1 - MCQ
    #2 - Written Question

    score=models.CharField(null=True, max_length=20)

    def __str__(self):
        return self.quiz.course.courseName

class Announcement(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    message=models.CharField(null=True, max_length=5000)
    created_on=models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.course.courseName