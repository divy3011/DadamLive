from django.urls import path
from . import views

urlpatterns = [
    path('face/',views.face,name="face"),
    path('face/image/detector/',views.image_detector,name="image_detector"),
    path('face/check/',views.check,name="check"),
    
]