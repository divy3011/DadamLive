from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardStudent,name="dashboardStudent"),
    path('courses/',views.my_courses,name="my_courses"),
    path('courses/view/<str:course_id>',views.view_course_student,name="view_course_student"),
    path('quiz/start/<str:quiz_id>',views.start_quiz,name="start_quiz"),
    path('quiz/start/get/questions/<str:quiz_id>',views.get_questions,name="get_questions"),
    

]