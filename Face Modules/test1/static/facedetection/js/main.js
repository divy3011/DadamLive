const video = document.getElementById("video");
const isScreenSmall = window.matchMedia("(max-width: 700px)");
let predictedAges = [];

/****Loading the model ****/
// Promise.all([
//   faceapi.nets.tinyFaceDetector.loadFromUri("https://testdivy.herokuapp.com/static/facedetection/models"),
//   faceapi.nets.faceRecognitionNet.loadFromUri("https://testdivy.herokuapp.com/static/facedetection/models")
// ]).then(startVideo);

Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri("http://127.0.0.1:8000/static/facedetection/models"),
  faceapi.nets.faceRecognitionNet.loadFromUri("http://127.0.0.1:8000/static/facedetection/models")
]).then(startVideo);

function startVideo() {
  navigator.getUserMedia(
    { video: {} },
    stream => (video.srcObject = stream),
    err => console.error(err)
  );
}

/****Fixing the video with based on size size  ****/
function screenResize(isScreenSmall) {
  if (isScreenSmall.matches) {
    video.style.width = "640px";
  } else {
    video.style.width = "640px";
  }
}

screenResize(isScreenSmall);
isScreenSmall.addListener(screenResize);

/****Event Listeiner for the video****/
video.addEventListener("playing", () => {
  const canvas = faceapi.createCanvasFromMedia(video);
  let container = document.querySelector(".container");
  container.append(canvas);

  const displaySize = { width: video.width, height: video.height };
  faceapi.matchDimensions(canvas, displaySize);

  setInterval(async () => {
    const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions());

    const resizedDetections = faceapi.resizeResults(detections, displaySize);
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);

    /****Drawing the detection box and landmarkes on canvas****/
    faceapi.draw.drawDetections(canvas, resizedDetections);
  }, 50);
});