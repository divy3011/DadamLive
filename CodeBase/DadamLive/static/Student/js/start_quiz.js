window.onload = function() {
    getQuestions();
    // setFullScreen();
    // setTimer();
};

function getQuestions(){
    alert("We are loading questions. Please note that you do not switch any tab or close the full screen mode. After some illegal attempts you will be logged out automatically. In this version of application, do not refresh the page until there is some error, answers will not be synced until you press the submit button.")
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