function submitForm(part_id){
    marks=document.getElementById(part_id).value;
    serializedData={"part_id": part_id, "marks": marks}
    $.ajax({
        type: 'GET',
        url: "upload/marks/",
        data: serializedData,
        success: function (response) {
            document.getElementById("current"+part_id).innerHTML="Current Marks: "+marks
        },
        error: function (response) {
            alert(response["responseJSON"]["message"])
        }
    });
    return false;
}

function marks_given_for_all_q(submission_id){
    serializedData={"submission_id": submission_id}
    $.ajax({
        type: 'GET',
        url: "final/",
        data: serializedData,
        success: function (response) {
            alert("This student's marks are freezed at the moment.")
        },
        error: function (response) {
            alert(response["responseJSON"]["message"])
        }
    });
    return false;
}

function getSimilarity(part_id){
    serializedData={"part_id": part_id}
    $.ajax({
        type: 'GET',
        url: "get/submission/",
        data: serializedData,
        success: function (response) {
            console.log(response)
            my_sub=JSON.parse(response["my_sub"])[0];
            other_subs=JSON.parse(response["other_subs"]);
            document.getElementById("inside_modal").innerHTML=""
            document.getElementById("heading_for_similarity").innerHTML="Plagiarism Matches for Submission ID #"+my_sub.fields.submission
            all=my_sub.fields.sub_id.split(",")
            per_match=my_sub.fields.percentage_match.split(",")
            answer="<div><b><p>Submission ID #"+my_sub.fields.submission+"</p></b><p>Answer: "+my_sub.fields.answer+"</p></div>"
            liner="<p>--------------------------------------------------</p>"
            $("#inside_modal").append(answer+liner)
            for(i=0;i<Object.keys(other_subs).length;i++){
                sub_id=-1
                for(j=0;j<all.length;j++){
                    if(all[j]==other_subs[i].pk){
                        sub_id=j;
                        break;
                    }
                }
                if(sub_id!=-1){
                    answer="<div><b><p>Submission ID #"+other_subs[i].fields.submission+" - Content Match percentage is "+per_match[sub_id]+"%</p></b><p>Answer: "+other_subs[i].fields.answer+"</p></div>"
                    liner="<p>--------------------------------------------------</p>"
                    $("#inside_modal").append(answer+liner)
                }
            }            
        },
        error: function (response) {
            alert(response["responseJSON"]["message"])
        }
    });
    return false;
}