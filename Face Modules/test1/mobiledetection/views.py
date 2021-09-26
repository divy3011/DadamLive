from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
def cell(request):
    return render(request, "mobiledetection/index.html",context={})