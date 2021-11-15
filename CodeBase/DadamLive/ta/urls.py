from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardTA,name="dashboardTA"),
    path('course/view/<str:course_id>',views.view_course_ta,name="view_course_ta"),
    path('course/announce/text/<str:course_id>',views.ta_announcement,name="ta_announcement"),
    path('course/announce/quiz/<str:course_id>',views.ta_announce_quiz,name="ta_announce_quiz"),
    path('course/view/get/permission/data/',views.get_permission_data,name="get_permission_data"),
    path('course/view/update/permissions/',views.update_ta_permissions,name="update_ta_permissions"),
    path('course/manage/quiz/<str:quiz_id>',views.ta_manage_quiz,name="ta_manage_quiz"),
    path('course/manage/quiz/change/status/<str:quiz_id>',views.ta_change_quiz_status,name="ta_change_quiz_status"),
    path('course/manage/quiz/previous/status/<str:quiz_id>',views.ta_change_prev_status,name="ta_change_prev_status"),
    path('course/manage/quiz/analysis/',views.ta_quiz_analysis,name="ta_quiz_analysis"),
    path('profile/',views.view_profile_ta,name="view_profile_ta"),
    path('profile/contact_number/verify/<str:unique_code>',views.verify_number,name="verify_number"),
    
]