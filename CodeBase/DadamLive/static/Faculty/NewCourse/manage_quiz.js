analysisDone=false;
function get_analysis(){
    if(analysisDone){
        return ;
    }
    analysisDone=true;
    quiz_id=document.getElementById("quiz_id").innerHTML;
    serializedData={"quiz_id": quiz_id}
    $.ajax({
        type: 'POST',
        url: "analysis/",
        data: serializedData,
        success: function (response) {
            console.log(response)
        },
        error: function (response) {
            document.getElementById("analysis_message").innerHTML=response["message"];
        }
    });
}