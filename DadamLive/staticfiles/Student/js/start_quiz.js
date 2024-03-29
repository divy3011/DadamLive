window.onload = function() {
    getQuestions();
    setWindowsTimeOut();
    sendIP();
    AudioVideoDetection();
};

function getQuestions(){
    alert("We are loading questions. Please note that you do not switch any tab or close the full screen mode. After some illegal attempts you will be logged out automatically. In this version of application, do not refresh the page until there is some error, answers will not be synced until you press the submit button. If you hear your own audio then mute out the sound section for this tab.")
    quiz_id=document.getElementById("quiz_id").innerHTML;
    var serializedData = 'quiz_id='+ quiz_id
    $.ajax({
        type: 'GET',
        url: "get/questions/"+String(quiz_id),
        data: serializedData,
        success: function (response) {
            // console.log(response);
            mcq=JSON.parse(response["mcq"]);
            written=JSON.parse(response["written"]);
            quiz=JSON.parse(response["quiz"]);

            //Setting the timer
            setTimer(quiz);

            partOfSubmission=JSON.parse(response["partOfSubmission"]);
            for(i=0;i<Object.keys(written).length;i++){
                answer="";
                for(j=0;j<Object.keys(partOfSubmission).length;j++){
                    if(partOfSubmission[j].fields.question_id==written[i].pk && partOfSubmission[j].fields.question_type==2){
                        answer=partOfSubmission[j].fields.answer;
                        break;
                    }
                }
                question='<div style="margin-bottom: 40px"><div>Question. '+written[i].fields.question+' ('+written[i].fields.maximum_marks+')</div>'
                text_box='<div><textarea id="Written'+written[i].pk+'">'+answer+'</textarea></div></div>'
                $("#questions").append(question+text_box)
                syncWrittenQuestion("Written"+written[i].pk)
            }
            for(i=0;i<Object.keys(mcq).length;i++){
                options=mcq[i].fields.options.split(",")
                question='<div style="margin-bottom: 40px"><div>Question. '+mcq[i].fields.question+' ('+mcq[i].fields.maximum_marks+')</div>'
                manager="";
                prev_answers=false;
                for(j=0;j<Object.keys(partOfSubmission).length;j++){
                    if(partOfSubmission[j].fields.question_id==mcq[i].pk && partOfSubmission[j].fields.question_type==1){
                        prev_answers=partOfSubmission[j].fields.answer.split(",")
                        break;
                    }
                }
                for(j=0;j<options.length;j++){
                    flag=0;
                    if(prev_answers!=false){
                        for(k=0;k<prev_answers.length;k++){
                            if((1+String(prev_answers[k]))==(1+String(j))){
                                flag=1;
                                manager+='<div><input type="checkbox" id="MCQ'+mcq[i].pk+"Option"+j+'" checked>'+options[j]+'</div>';
                                break;
                            }
                        }
                    }
                    if(flag==0) 
                        manager+='<div><input type="checkbox" id="MCQ'+mcq[i].pk+"Option"+j+'">'+options[j]+'</div>'
                }
                all_options='<div id="MCQ'+mcq[i].pk+'">'+manager+'</div></div>'
                $("#questions").append(question+all_options)
                syncMCQQuestion("MCQ"+mcq[i].pk, options.length)
            }
            // addQuesionsToHtml();
        },
        error: function (response) {
            alert(response["responseJSON"]["message"])
            location.reload();
        }
    });
}

function syncMCQQuestion(question_id, max_options){
    document.getElementById(question_id).addEventListener("click", function(event) {
        quiz_id=document.getElementById("quiz_id").innerHTML;
        answer="";
        for(i=0;i<max_options;i++){
            option_id="#"+question_id+"Option"+i
            if ($(option_id).is(':checked')) {
                answer+=i+",";
            }
        }
        if(answer[answer.length - 1]==",")
            answer=answer.substr(0, answer.length - 1)
        serializedData={"quiz_id": quiz_id, "question_id": question_id, "answer": answer}
        while(internetConnected()==false){}
        $.ajax({
            type: 'GET',
            url: "save/question/1",
            data: serializedData,
            success: function (response) {
                
            },
            error: function (response) {
                alert(response["responseJSON"]["message"])
            }
        });
    });
}

function syncWrittenQuestion(question_id){
    document.getElementById(question_id).addEventListener("keydown", function(event) {
        quiz_id=document.getElementById("quiz_id").innerHTML;
        serializedData={"quiz_id": quiz_id, "question_id": question_id, "answer": document.getElementById(question_id).value}
        while(internetConnected()==false){}
        $.ajax({
            type: 'GET',
            url: "save/question/2",
            data: serializedData,
            success: function (response) {
                
            },
            error: function (response) {
                alert(response["responseJSON"]["message"])
            }
        });
    });
}

function internetConnected(){
    return true;
}

numberOfTimesWindowsTimedOut=0;

function setWindowsTimeOut(){
    var x=setTimeout(function() {
        window.blur();
        $(window).blur(function() {
            if(numberOfTimesWindowsTimedOut<3){
                numberOfTimesWindowsTimedOut++;
                alert('It was noticed that you changed the tab, changed web address or opened any another application. Ignore doing that otherwise you will be logged out immediately out of the test.');
            }
            logIllegalActivity(1)
        });
        clearInterval(x)
    }, 5000);
}

function logIllegalActivity(typeAct){
    quiz_id=document.getElementById("quiz_id").innerHTML;
    var serializedData = 'type='+ typeAct
    $.ajax({
        type: 'GET',
        url: "mark/activity/"+String(quiz_id),
        data: serializedData,
        success: function (response) {},
        error: function (response) {}
    });
}

function setTimer(quiz){
    last_date=quiz[0].fields.end_date
    date=last_date.substr(0,10)
    time=last_date.substr(11,8)
    date=date.split("-")
    time=getMonth(date[1])+" "+date[2]+", "+date[0] + " "+time
    var countDownDate = new Date(time).getTime();
    var x = setInterval(function() {
        var now = new Date().getTime();
        var distance = countDownDate - now;
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
        document.getElementById("myTimer").innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
        if (distance < 0) {
            clearInterval(x);
            document.getElementById("myTimer").innerHTML = "Test Ended";
            alert("Saving the submission. Do not close this page.")
            sendEndSignal();
        }
    }, 1000);
}

function getMonth(id){
    id=parseInt(id)
    if(id==1){
        return "Jan"
    }
    if(id==2){
        return "Feb"
    }
    if(id==3){
        return "Mar"
    }
    if(id==4){
        return "Apr"
    }
    if(id==5){
        return "May"
    }
    if(id==6){
        return "Jun"
    }
    if(id==7){
        return "Jul"
    }
    if(id==8){
        return "Aug"
    }
    if(id==9){
        return "Sep"
    }
    if(id==10){
        return "Oct"
    }
    if(id==11){
        return "Nov"
    }
    if(id==12){
        return "Dec"
    }
    return "Unavailable"
}

function sendIP(){
    $.getJSON('https://api.db-ip.com/v2/free/self', function(data) {
        // location_details=JSON.stringify(data, null, 2);
        ip=data["ipAddress"]
        var serializedData = 'ipAddress='+ ip;
        quiz_id=document.getElementById("quiz_id").innerHTML;
        $.ajax({
            type: 'GET',
            url: "mark/ip/address/"+String(quiz_id),
            data: serializedData,
            success: function (response) {},
            error: function (response) {}
        });
    });
}

async function AudioVideoDetection(){
    count=0;
    try{
        let video = document.querySelector("#video");
        let canvas = document.querySelector("#canvas");

        let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        audioDetection(stream);
        video.srcObject = stream;
    }
    catch{
        if(count<3){
            count++;
            alert("No camera was found. You can give the test but this malpractie will be saved.")
        }
        return ;
    }

    let delayTime=10000
    
    setInterval(function(){
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        let image_data_url = canvas.toDataURL().replace(/^data:image\/png;base64,/, "");

        quiz_id=document.getElementById("quiz_id").innerHTML;
        serializedData={"quiz_id": quiz_id, "image": image_data_url, "csrfmiddlewaretoken": sha256("ABIPHRVBBBEBIBUBFUBEUweirypg@)8374")}
        while(internetConnected()==false){}
        $.ajax({
            type: 'POST',
            url: "image/detector/"+String(quiz_id),
            data: serializedData,
            success: function (response) {
                
            },
            error: function (response) {
                alert(response["responseJSON"]["message"])
            }
        });
    },delayTime);
}

function audioDetection(stream){

    // These levels must be in increasing order.
    level1=100;
    level2=150;
    level3=200;
    
    // When audioCounter reaches maxCounter an illegal attempt will be saved
    maxCounter=150;

    audioCounter=0;
    try{
        audioContext = new AudioContext();
        analyser = audioContext.createAnalyser();
        microphone = audioContext.createMediaStreamSource(stream);
        javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);

        analyser.smoothingTimeConstant = 0.8;
        analyser.fftSize = 1024;

        microphone.connect(analyser);
        analyser.connect(javascriptNode);
        javascriptNode.connect(audioContext.destination);
        javascriptNode.onaudioprocess = function() {
            var array = new Uint8Array(analyser.frequencyBinCount);
            analyser.getByteFrequencyData(array);
            var values = 0;

            var length = array.length;
            for (var i = 0; i < length; i++) {
                values += (array[i]);
            }

            var average = values / length;

            soundIntensity=Math.round(average);
            if(soundIntensity>level3){
                audioCounter+=3;
            }
            else if(soundIntensity>level2){
                audioCounter+=2;
            }
            else if(soundIntensity>level1){
                audioCounter+=1;
            }
            if(audioCounter>=maxCounter){
                audioCounter=0;
                logIllegalActivity(5);
            }
        }
    }
    catch{
        alert("No microphone was found. You can give the test but this malpractie will be saved.")
    }
}

function sendEndSignal(){
    quiz_id=document.getElementById("quiz_id").innerHTML;
    while(internetConnected()==false){}
    $.ajax({
        type: 'GET',
        url: "end/test/"+String(quiz_id),
        success: function (response) {
            alert("Your submission has been saved successfully.")
            location.reload();
        },
        error: function (response) {
            alert(response["responseJSON"]["message"])
        }
    });
}

function end_quiz(e){
    if(!confirm("Do you want to end the quiz? You will not able to start it again.")){
        e.preventDefault();
        return false;
    }
    sendEndSignal();
}

function sha256(ascii) {
	function rightRotate(value, amount) {
		return (value>>>amount) | (value<<(32 - amount));
	};
	
	var mathPow = Math.pow;
	var maxWord = mathPow(2, 32);
	var lengthProperty = 'length';
	var i, j; // Used as a counter across the whole file
	var result = '';

	var words = [];
	var asciiBitLength = ascii[lengthProperty]*8;
	
	//* caching results is optional - remove/add slash from front of this line to toggle
	// Initial hash value: first 32 bits of the fractional parts of the square roots of the first 8 primes
	// (we actually calculate the first 64, but extra values are just ignored)
	var hash = sha256.h = sha256.h || [];
	// Round constants: first 32 bits of the fractional parts of the cube roots of the first 64 primes
	var k = sha256.k = sha256.k || [];
	var primeCounter = k[lengthProperty];
	/*/
	var hash = [], k = [];
	var primeCounter = 0;
	//*/

	var isComposite = {};
	for (var candidate = 2; primeCounter < 64; candidate++) {
		if (!isComposite[candidate]) {
			for (i = 0; i < 313; i += candidate) {
				isComposite[i] = candidate;
			}
			hash[primeCounter] = (mathPow(candidate, .5)*maxWord)|0;
			k[primeCounter++] = (mathPow(candidate, 1/3)*maxWord)|0;
		}
	}
	
	ascii += '\x80'; // Append '1' bit (plus zero padding)
	while (ascii[lengthProperty]%64 - 56) ascii += '\x00'; // More zero padding
	for (i = 0; i < ascii[lengthProperty]; i++) {
		j = ascii.charCodeAt(i);
		if (j>>8) return; // ASCII check: only accept characters in range 0-255
		words[i>>2] |= j << ((3 - i)%4)*8;
	}
	words[words[lengthProperty]] = ((asciiBitLength/maxWord)|0);
	words[words[lengthProperty]] = (asciiBitLength)
	
	// process each chunk
	for (j = 0; j < words[lengthProperty];) {
		var w = words.slice(j, j += 16); // The message is expanded into 64 words as part of the iteration
		var oldHash = hash;
		// This is now the "working hash", often labelled as variables a...g
		// (we have to truncate as well, otherwise extra entries at the end accumulate
		hash = hash.slice(0, 8);
		
		for (i = 0; i < 64; i++) {
			var i2 = i + j;
			// Expand the message into 64 words
			// Used below if 
			var w15 = w[i - 15], w2 = w[i - 2];

			// Iterate
			var a = hash[0], e = hash[4];
			var temp1 = hash[7]
				+ (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) // S1
				+ ((e&hash[5])^((~e)&hash[6])) // ch
				+ k[i]
				// Expand the message schedule if needed
				+ (w[i] = (i < 16) ? w[i] : (
						w[i - 16]
						+ (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15>>>3)) // s0
						+ w[i - 7]
						+ (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2>>>10)) // s1
					)|0
				);
			// This is only used once, so *could* be moved below, but it only saves 4 bytes and makes things unreadble
			var temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) // S0
				+ ((a&hash[1])^(a&hash[2])^(hash[1]&hash[2])); // maj
			
			hash = [(temp1 + temp2)|0].concat(hash); // We don't bother trimming off the extra ones, they're harmless as long as we're truncating when we do the slice()
			hash[4] = (hash[4] + temp1)|0;
		}
		
		for (i = 0; i < 8; i++) {
			hash[i] = (hash[i] + oldHash[i])|0;
		}
	}
	
	for (i = 0; i < 8; i++) {
		for (j = 3; j + 1; j--) {
			var b = (hash[i]>>(j*8))&255;
			result += ((b < 16) ? 0 : '') + b.toString(16);
		}
	}
	return result;
};
