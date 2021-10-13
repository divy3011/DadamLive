function main() {
    const video = document.getElementById("video");
    const start = document.getElementById("start");
    const stop = document.getElementById("stop");
  
    var displayMediaOptions = {
      video: {
        cursor: "always",
      },
      audio: false,
      displaySurface: "window",
    };
  
    start.onclick = function (e) {
      check();
    };
    stop.onclick = function (e) {
      stopSharing();
    };
    var flag="false";
    async function check(){
        startSharing();
        {
            try{
                console.log(video.srcObject);
                if(video.srcObject.getVideoTracks()[0].getSettings().displaySurface!=="monitor"){
                    let tracks = video.srcObject.getTracks();
                    tracks.forEach((track) => track.stop());
                    video.srcObject = null;
                    startSharing();
                }
                else if(video.srcObject.getVideoTracks()[0].getSettings().displaySurface==="monitor"){
                    flag="true";
                }
            }catch(error){
                console.log(error);
            }
        }
    }
    async function startSharing() {
      try {
        video.srcObject = await navigator.mediaDevices.getDisplayMedia(
          displayMediaOptions
        );
        } catch (error) {
          console.log(error);
        }
        console.log(video.srcObject)
        // video.srcObject.getVideoTracks()[0].getSettings().displaySurface="monitor";
        // // console.log(video.srcObject);
        // // console.log(ConstrainDOMString)
        // console.log(video.srcObject.getVideoTracks()[0].getSettings().displaySurface)
      }
  
      function stopSharing() {
          flag="false";
        let tracks = video.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
        video.srcObject = null;
      }
  }
  
  main();
  