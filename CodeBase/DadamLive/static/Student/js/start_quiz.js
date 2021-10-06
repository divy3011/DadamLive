window.onload = function() {
    getQuestions();
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
            console.log(response)
            addQuesionsToHtml();
            setTimer();
        },
        error: function (response) {
            alert(response["responseJSON"]["error"])
            location.reload();
        }
    });
}

