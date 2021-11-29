function setID(id){
    document.getElementById("title").innerHTML="Upload new Image for Course ID #"+id;
    document.getElementById("course_id").value=id;

}

function setIDName(id, cour_name){
    document.getElementById("title1").innerHTML="Change Course Name for Course ID #"+id;
    document.getElementById("course_id1").value=id;
    document.getElementById("cour_name").value=cour_name;
}