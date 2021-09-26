from django.urls import path
from . import views

urlpatterns = [
    path('',views.cell,name="cell"),
]