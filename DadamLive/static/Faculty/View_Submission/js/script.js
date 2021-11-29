function animateValue(id, start, end, duration,flag) {
    var obj = id;
    var range = end - start;
    var minTimer = 50;
    var stepTime = Math.abs(Math.floor(duration / range));
    stepTime = Math.max(stepTime, minTimer);
    var startTime = new Date().getTime();
    var endTime = startTime + duration;
    var timer;
    function run() {
        var now = new Date().getTime();
        var remaining = Math.max((endTime - now) / duration, 0);
        var value = Math.round(end - (remaining * range));
        temp=String(value);
        if(flag){
          temp+='%';
        }
        obj.innerHTML = temp;
        if (value == end) {
            clearInterval(timer);
        }
    }
    timer = setInterval(run, stepTime);
    run();
}
r=document.getElementsByTagName('p');
for(let i=0;i<r.length;i++){
    text=r[i].innerHTML;
    flag=false;
    if(text.includes("%")){
        flag=true;
    }
    text=text.match(/\d+/)[0];
    text=parseInt(text);
    animateValue(r[i], 0, text, 500,flag);
}