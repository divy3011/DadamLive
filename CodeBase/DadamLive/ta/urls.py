from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardTA,name="dashboardTA"),
    path('course/view/<str:course_id>',views.view_course_ta,name="view_course_ta"),
    path('course/announce/text/<str:course_id>',views.ta_announcement,name="ta_announcement"),
    path('course/announce/quiz/<str:course_id>',views.ta_announce_quiz,name="ta_announce_quiz"),
    path('course/view/get/permission/data/',views.get_permission_data,name="get_permission_data"),
    path('course/view/update/permissions/',views.update_ta_permissions,name="update_ta_permissions"),
]