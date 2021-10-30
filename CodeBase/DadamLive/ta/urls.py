from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardTA,name="dashboardTA"),
    path('view/course/<str:course_id>',views.view_course_ta,name="view_course_ta"),
    
]