window.onload = function() {
    start();
};
async function start(){
    let video = document.querySelector("#video");
    let canvas = document.querySelector("#canvas");
    let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    video.srcObject = stream;
}