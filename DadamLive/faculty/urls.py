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
    path('course/manage/quiz/previous/status/<str:quiz_id>',views.change_prev_status,name="change_prev_status"),
    path('course/manage/quiz/analysis/',views.quiz_analysis,name="quiz_analysis"),
    path('generate/score/<str:quiz_id>',views.generate_score,name="generate_score"),
    path('detect/web/sources/<str:quiz_id>',views.detect_web_sources,name="detect_web_sources"),
    path('view/submission/<str:submission_id>',views.view_submission,name="view_submission"),
    path('view/submission/upload/marks/',views.upload_marks,name="upload_marks"),
    path('view/submission/final/',views.marks_given_for_all_q,name="marks_given_for_all_q"),
    path('match/student/answers/<str:quiz_id>',views.match_student_answers,name="match_student_answers"),
    path('view/submission/get/submission/',views.get_submission,name="get_submission"),
    path('course/upload/image/',views.upload_course_image,name="upload_course_image"),
    path('quiz/image/captured/<str:submission_id>',views.images_for_illegal_att,name="images_for_illegal_att"),
    path('course/view/get/permission/data/',views.get_permission_data,name="get_permission_data"),
    path('course/view/update/permissions/',views.update_ta_permissions,name="update_ta_permissions"),
    path('get/report/<str:course_id>',views.get_report,name="get_report"),
    path('profile/',views.view_profile_fa,name="view_profile_fa"),
    path('change_password/',views.change_password_fa,name="change_password_fa"),
    

]
