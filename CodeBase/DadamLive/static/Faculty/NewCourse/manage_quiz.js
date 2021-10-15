$(document).ready(function(){
    $('#myTable').dataTable();
    $('#myTable1').dataTable();
});


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
            // console.log(response)
            submissions=JSON.parse(response["submissions"]);
            illegal_attempts=JSON.parse(response["illegal_attempts"]);
            users=JSON.parse(response["users"]);
            n=Object.keys(submissions).length;
            for(i=0;i<n;i++){
                user=false;
                for(j=0;j<Object.keys(users).length;j++){
                    if(users[j].pk==submissions[i].fields.user){
                        user=users[j];
                        break;
                    }
                }
                attempt=false;
                for(j=0;j<Object.keys(illegal_attempts).length;j++){
                    if(illegal_attempts[j].fields.submission==submissions[i].pk){
                        attempt=illegal_attempts[j];
                        break;
                    }
                }
                ip="Yes"
                if(attempt.fields.usingSomeoneElseIP){
                    ip="No"
                }
                var t=$('#myTable').DataTable();
                t.row.add( [
                    user.fields.first_name,
                    user.fields.email,
                    attempt.fields.browserSwitched,
                    ip,
                    attempt.fields.numberOfTimesMultiplePersonsDetected,
                    attempt.fields.noPersonDetected,
                    attempt.fields.numberOfTimesAudioDetected,
                    submissions[i].fields.averagePlagiarism+"%",
                    attempt.fields.noOfTimesMobileDetected
                ] ).draw( false );
            }
        },
        error: function (response) {
            document.getElementById("analysis_message").innerHTML=response["message"];
        }
    });
}