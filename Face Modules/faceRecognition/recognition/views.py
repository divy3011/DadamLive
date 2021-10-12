from django.http.response import HttpResponse
from django.shortcuts import render
import cv2
import os
from django.contrib.staticfiles.storage import staticfiles_storage
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from copy import deepcopy
from django.http.response import JsonResponse
# Create your views here.
def face(request):
    return render(request, "recognition/index.html",context={})
count = 0
def image_detector(request):
    id = 'divy'
    global count
    if(os.path.exists('static/recognition/training_dataset/{}/'.format(id))==False):
        os.makedirs('static/recognition/training_dataset/{}/'.format(id))
    directory='static/recognition/training_dataset/{}/'.format(id)
    image=request.POST.get("image")
    image = base64.b64decode(image)
    image = Image.open(BytesIO(image))
    image  = np.array(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    file_path = staticfiles_storage.path('recognition/haarcascade_frontalface_default.xml')
    face_detector = cv2.CascadeClassifier(file_path)
    img_raw = deepcopy(image)
    print(face_detector)
    print(image)
    faces = face_detector.detectMultiScale(img_raw, 1.3, 5)
    print(faces)
    for face in faces:
        count+=1
        face_x, face_y, face_w, face_h = face
        imagei = image[int(face_y):int(face_y+face_h), int(face_x):int(face_x+face_w)]
        img_gray = cv2.cvtColor(imagei, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(directory+'/'+str(count)+'.jpg'	, img_gray)
    if(count>100):
        count=0
        return JsonResponse({"message": "collected 100 faces"}, status=200)
    else:
        return JsonResponse({"message": "collected 1 more face"}, status=200)