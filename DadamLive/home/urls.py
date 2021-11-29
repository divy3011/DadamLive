from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('login/',views.login_request,name="login_request"),
    path('logout/',views.logout_request,name="logout_request"),
    path('redirect/dashboard/',views.login_redirecter,name="login_redirecter"),
    path('query/',views.save_query,name="save_query"),
    path('forgot_password/',views.forgot_password,name="forgot_password"),
    path('change_password/<str:unique_code>',views.change_password,name="change_password"),
    
]
