function getTAData(ta_permission_id, course_id){
    serializedData={"ta_permission_id": ta_permission_id, "course_id": course_id}
    $.ajax({
        type: 'POST',
        url: "get/permission/data/",
        data: serializedData,
        success: function (response) {
            data=JSON.parse(response["data"])[0];
            document.getElementById('ta_details').innerHTML="Teaching Assistant ID #"+data.pk;
            document.getElementById('permission_id').value=ta_permission_id;
            document.getElementById('course_id_ta').value=course_id;
            add_main_ta_select(data);
            can_manage_ta_change_permissions(data);
            canCheckAnswerSheets(data);
            canAnnounce(data);
            canManageQuiz(data);
        },
        error: function (response) {
            alert("Unable to get the TA data. You can't further change the TA permissions.")
        }
    });
}

function add_main_ta_select(data){
    var select_head_ta_yes=document.createElement('option');
    select_head_ta_yes.value=1;
    select_head_ta_yes.innerHTML="Yes";

    var select_head_ta_no=document.createElement('option');
    select_head_ta_no.value=0;
    select_head_ta_no.innerHTML="No";
    $("#select_head_ta").empty();
    if(data.fields.isMainTA){
        document.getElementById('select_head_ta').appendChild(select_head_ta_yes);
        document.getElementById('select_head_ta').appendChild(select_head_ta_no);
    }
    else{
        document.getElementById('select_head_ta').appendChild(select_head_ta_no);
        document.getElementById('select_head_ta').appendChild(select_head_ta_yes);
    }
}

function can_manage_ta_change_permissions(data){
    var canManageTAPermissions_yes=document.createElement('option');
    canManageTAPermissions_yes.value=1;
    canManageTAPermissions_yes.innerHTML="Yes";

    var canManageTAPermissions_no=document.createElement('option');
    canManageTAPermissions_no.value=0;
    canManageTAPermissions_no.innerHTML="No";
    $("#canManageTAPermissions").empty();
    if(data.fields.canManageTAPermissions){
        document.getElementById('canManageTAPermissions').appendChild(canManageTAPermissions_yes);
        document.getElementById('canManageTAPermissions').appendChild(canManageTAPermissions_no);
    }
    else{
        document.getElementById('canManageTAPermissions').appendChild(canManageTAPermissions_no);
        document.getElementById('canManageTAPermissions').appendChild(canManageTAPermissions_yes);
    }
}

function canCheckAnswerSheets(data){
    var canCheckAnswerSheets_yes=document.createElement('option');
    canCheckAnswerSheets_yes.value=1;
    canCheckAnswerSheets_yes.innerHTML="Yes";

    var canCheckAnswerSheets_no=document.createElement('option');
    canCheckAnswerSheets_no.value=0;
    canCheckAnswerSheets_no.innerHTML="No";
    $("#canCheckAnswerSheets").empty();
    if(data.fields.canCheckAnswerSheets){
        document.getElementById('canCheckAnswerSheets').appendChild(canCheckAnswerSheets_yes);
        document.getElementById('canCheckAnswerSheets').appendChild(canCheckAnswerSheets_no);
    }
    else{
        document.getElementById('canCheckAnswerSheets').appendChild(canCheckAnswerSheets_no);
        document.getElementById('canCheckAnswerSheets').appendChild(canCheckAnswerSheets_yes);
    }
}

function canAnnounce(data){
    var canAnnounce_yes=document.createElement('option');
    canAnnounce_yes.value=1;
    canAnnounce_yes.innerHTML="Yes";

    var canAnnounce_no=document.createElement('option');
    canAnnounce_no.value=0;
    canAnnounce_no.innerHTML="No";
    $("#canAnnounce").empty();
    if(data.fields.canAnnounce){
        document.getElementById('canAnnounce').appendChild(canAnnounce_yes);
        document.getElementById('canAnnounce').appendChild(canAnnounce_no);
    }
    else{
        document.getElementById('canAnnounce').appendChild(canAnnounce_no);
        document.getElementById('canAnnounce').appendChild(canAnnounce_yes);
    }
}

function canManageQuiz(data){
    var canManageQuiz_yes=document.createElement('option');
    canManageQuiz_yes.value=1;
    canManageQuiz_yes.innerHTML="Yes";

    var canManageQuiz_no=document.createElement('option');
    canManageQuiz_no.value=0;
    canManageQuiz_no.innerHTML="No";
    $("#canManageQuiz").empty();
    if(data.fields.canManageQuiz){
        document.getElementById('canManageQuiz').appendChild(canManageQuiz_yes);
        document.getElementById('canManageQuiz').appendChild(canManageQuiz_no);
    }
    else{
        document.getElementById('canManageQuiz').appendChild(canManageQuiz_no);
        document.getElementById('canManageQuiz').appendChild(canManageQuiz_yes);
    }
}

$("#ta_form").submit(function (e) {
    e.preventDefault();
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "update/permissions/",
        data: serializedData,
        success: function (response) {
            alert("Permissions updated successfully.")
        },
        error: function (response) {
            alert("Unable to update permission for the TA. Please refresh the page and try again.")
        }
    })
})