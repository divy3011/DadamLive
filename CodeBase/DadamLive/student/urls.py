from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardStudent,name="dashboardStudent"),
    path('courses/',views.my_courses,name="my_courses"),
    path('courses/view/<str:course_id>',views.view_course_student,name="view_course_student"),
    path('quiz/start/<str:quiz_id>',views.start_quiz,name="start_quiz"),
    path('quiz/start/get/questions/<str:quiz_id>',views.get_questions,name="get_questions"),
    path('quiz/start/save/question/<str:q_type>',views.save_question,name="save_question"),
    path('quiz/start/mark/activity/<str:quiz_id>',views.mark_activity,name="mark_activity"),
    path('quiz/start/mark/ip/address/<str:quiz_id>',views.mark_ip,name="mark_ip"),
    path('quiz/start/image/detector/<str:quiz_id>',views.image_detector,name="image_detector"),
    path('quiz/start/end/test/<str:quiz_id>',views.end_test,name="end_test"),
    path('quiz/start/freeze/answer/',views.freeze_answer,name="freeze_answer"),
    path('quiz/start/tab/change/image/<str:quiz_id>',views.tab_change_image_save,name="tab_change_image_save"),
    path('profile/',views.view_profile_st,name="view_profile_st"),
    path('change_password/',views.change_password_st,name="change_password_st"),
    
    

]