from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Course)
admin.site.register(Enrolment)
admin.site.register(Quiz)
admin.site.register(MCQ)
admin.site.register(WrittenQuestion)
admin.site.register(Submission)