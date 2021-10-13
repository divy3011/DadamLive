from django.test import TestCase

# Create your tests here.


# def image_clipping(request):
#     if request.user.is_authenticated==False:
#         return JsonResponse({"message": "Please login to go for video clipping"}, status=400)
#     student=1
#     try:
#         info=UserInformation.objects.get(user=request.user)
#         if info.userType.userTypeCode==settings.CODE_STUDENT:
#             student=Student.objects.get(user=request.user)
#     except:
#         return JsonResponse({"message": "For video clipping you must login through a student account."}, status=400)

#     if(student.faceCount>=100):
#         # Run a background server to train the model.
#         if student.faceAdded==False:
#             Train(student.id).start()
#         student.faceAdded=True
#         student.save()
#         return JsonResponse({"message": "Your face clipping is done successfully."}, status=400)

#     username=request.user.username
#     if(os.path.exists('static/Student/js/recognition/training_dataset/{}/'.format(username))==False):
#         os.makedirs('static/Student/js/recognition/training_dataset/{}/'.format(username))
#     directory='static/Student/js/recognition/training_dataset/{}/'.format(username)
#     image=request.POST.get("image")
#     image = base64.b64decode(image)
#     image = Image.open(BytesIO(image))
#     image  = np.array(image)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     file_path = staticfiles_storage.path('Student/js/recognition/haarcascade_frontalface_default.xml')
#     face_detector = cv2.CascadeClassifier(file_path)
#     img_raw = deepcopy(image)
#     faces = face_detector.detectMultiScale(img_raw, 1.3, 5)
#     for face in faces:
#         student.faceCount=student.faceCount+1
#         student.save()
#         face_x, face_y, face_w, face_h = face
#         imagei = image[int(face_y):int(face_y+face_h), int(face_x):int(face_x+face_w)]
#         img_gray = cv2.cvtColor(imagei, cv2.COLOR_BGR2GRAY)
#         cv2.imwrite(directory+'/'+str(student.faceCount)+'.jpg'	, img_gray)
    
#     return JsonResponse({"message": "collected 1 more face"}, status=200)

# class Train(Thread):
#     def __init__(self, student_id):
#         self.student_id=student_id
#         Thread.__init__(self)

#     def run(self):
#         number=random.randint(1,10)
#         train_model(self.student_id, schedule=number + int(settings.TIME_TO_TRAIN_MODEL*60))

# @background(schedule=60)
# def train_model(student_id):
#     student=Student.objects.get(id=int(student_id))
#     if student.addedOnce:
#         return False
#     person_name=student.user.username
#     training_dir='static/Student/js/recognition/training_dataset'
#     X=[]
#     y=[]
#     for person_name in os.listdir(training_dir):
#         curr_directory=os.path.join(training_dir,person_name)
#         if not os.path.isdir(curr_directory):
#             continue
#         try:
#             user=User.objects.get(username=person_name)
#             student=Student.objects.get(user=user)
#             if student.addedOnce==False:
#                 student.addedOnce=True
#                 student.save()
#         except:
#             pass
#         for imagefile in image_files_in_folder(curr_directory):
#             image=cv2.imread(imagefile)
#             try:
#                 X.append((face_recognition.face_encodings(image)[0]).tolist())
#                 y.append(person_name)
#             except:
#                 pass
#                 # os.remove(imagefile)
#     encoder = LabelEncoder()
#     encoder.fit(y)
#     y=encoder.transform(y)
#     X1=np.array(X)
#     np.save('static/Student/js/recognition/classes.npy', encoder.classes_)
#     svc = SVC(kernel='linear',probability=True)
#     svc.fit(X1,y)
#     svc_save_path="static/Student/js/recognition/svc.sav"
#     with open(svc_save_path, 'wb') as f:
#         pickle.dump(svc,f)
#     return True