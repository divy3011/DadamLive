window.onload = function() {
    start();
};
async function start(){
    let video = document.querySelector("#video");
    let canvas = document.querySelector("#canvas");
    let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    video.srcObject = stream;
}
$(document).ready(function(){
    $('.next').click(function(){
        $('.pagination').find('.pagenumber.active').next().attr("hidden", false);
        $('.pagination').find('.pagenumber.active').next().addClass('active');
        $('.pagination').find('.pagenumber.active').prev().attr("hidden", true);
        $('.pagination').find('.pagenumber.active').prev().removeClass('active');
    })
    $('.prev').click(function(){
        $('.pagination').find('.pagenumber.active').prev().attr("hidden", false);
        $('.pagination').find('.pagenumber.active').prev().addClass('active');
        $('.pagination').find('.pagenumber.active').next().attr("hidden", true);
        $('.pagination').find('.pagenumber.active').next().removeClass('active');
    })
})