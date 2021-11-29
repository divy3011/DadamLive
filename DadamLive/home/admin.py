from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserType)
admin.site.register(UserInformation)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Staff)
admin.site.register(TeachingAssistant)
admin.site.register(Query)
admin.site.register(ForgotPassword)