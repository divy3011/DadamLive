from django.http.response import HttpResponse
from django.shortcuts import render
import cv2
import os
from django.contrib.staticfiles.storage import staticfiles_storage
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import dlib
from copy import deepcopy
from django.http.response import JsonResponse
import face_recognition
import pickle
from sklearn.preprocessing import LabelEncoder
from face_recognition.face_recognition_cli import image_files_in_folder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from .models import *
# Create your views here.
def face(request):
    return render(request, "recognition/index.html",context={})
s = 0
def train():
    training_dir='static/recognition/training_dataset'
    count=0
    for person_name in os.listdir(training_dir):
        curr_directory=os.path.join(training_dir,person_name)
        if not os.path.isdir(curr_directory):
            continue
        for imagefile in image_files_in_folder(curr_directory):
            count+=1
    X=[]
    y=[]
    i=0
    for person_name in os.listdir(training_dir):
        print(str(person_name))
        curr_directory=os.path.join(training_dir,person_name)
        if not os.path.isdir(curr_directory):
            continue
        for imagefile in image_files_in_folder(curr_directory):
            print(str(imagefile))
            image=cv2.imread(imagefile)
            try:
                X.append((face_recognition.face_encodings(image)[0]).tolist())
                y.append(person_name)
                i+=1
            except:
                print("removed")
                # os.remove(imagefile)
    targets=np.array(y)
    encoder = LabelEncoder()
    encoder.fit(y)
    y=encoder.transform(y)
    X1=np.array(X)
    print("shape: "+ str(X1.shape))
    np.save('static/recognition/classes.npy', encoder.classes_)
    svc = SVC(kernel='linear',probability=True)
    svc.fit(X1,y)
    svc_save_path="static/recognition/svc.sav"
    with open(svc_save_path, 'wb') as f:
        pickle.dump(svc,f)
    

def image_detector(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "login karo chup chap ja ke pehle, aaye bade sahib jaade"}, status=400)
    face_collection=0
    try:
        face_collection=FaceCollection.objects.get(user=request.user)
    except:
        face_collection=FaceCollection.objects.create(user=request.user)
    if(face_collection.count>100):
        # train()
        return JsonResponse({"message": "tumra face collect karliya, ab dubara muh mat dikhana"}, status=400)

    id=request.user.username
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
    faces = face_detector.detectMultiScale(img_raw, 1.3, 5)
    print(faces)
    for face in faces:
        print(face_collection.count)
        face_collection.count=face_collection.count+1
        face_collection.save()
        face_x, face_y, face_w, face_h = face
        imagei = image[int(face_y):int(face_y+face_h), int(face_x):int(face_x+face_w)]
        img_gray = cv2.cvtColor(imagei, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(directory+'/'+str(face_collection.count)+'.jpg'	, img_gray)
    
    return JsonResponse({"message": "collected 1 more face"}, status=200)

def check(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "login karo chup chap ja ke pehle, aaye bade sahib jaade"}, status=400)
    face_collection=0
    try:
        face_collection=FaceCollection.objects.get(user=request.user)
    except:
        face_collection=FaceCollection.objects.create(user=request.user)
    if(face_collection.count>100):
        # train()
        return JsonResponse({"message": "tumra face collect karliya, ab dubara muh mat dikhana"}, status=200)