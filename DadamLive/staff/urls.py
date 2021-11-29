from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboardStaff,name="dashboardStaff"),
    path('users/add/',views.add_users,name="add_users"),
    
]
