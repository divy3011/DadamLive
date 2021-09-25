from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings
import requests

# Create your views here.
def home(request):
    if request.method=="POST":
        data=request.POST.get("data")
        key=settings.KEY
        url=settings.URL
        PARAMS = {'key':key, 'data':data}
        response = requests.post(url, PARAMS)
        ans=response.json()["sources"]
        print(response.json()["sources"])
        return HttpResponse("<h1>"+str(ans)+"</h1>")
    else:
        return render(request,"home/index.html",context={})