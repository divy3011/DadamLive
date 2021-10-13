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