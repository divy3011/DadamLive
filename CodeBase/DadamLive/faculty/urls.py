from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardFaculty,name="dashboardFaculty"),
    path('course/new/',views.start_new_course,name="start_new_course"),
    path('course/view/<str:course_id>',views.view_course,name="view_course"),
]
