from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardTA,name="dashboardTA"),
    path('view/course/<str:course_id>',views.view_course_ta,name="view_course_ta"),
    path('course/announce/text/<str:course_id>',views.ta_announcement,name="ta_announcement"),
    
]