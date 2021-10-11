from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardFaculty,name="dashboardFaculty"),
    path('course/new/',views.start_new_course,name="start_new_course"),
    path('course/view/<str:course_id>',views.view_course,name="view_course"),
    path('course/add/alumini/<str:course_id>',views.add_student_ta,name="add_student_ta"),
    path('course/announce/text/<str:course_id>',views.faculty_announcement,name="faculty_announcement"),
    path('course/announce/quiz/<str:course_id>',views.announce_quiz,name="announce_quiz"),
    path('course/manage/quiz/<str:quiz_id>',views.manage_quiz,name="manage_quiz"),
    path('course/manage/quiz/change/status/<str:quiz_id>',views.change_quiz_status,name="change_quiz_status"),
    path('course/manage/quiz/analysis/',views.quiz_analysis,name="quiz_analysis"),

]
