$("#course_form").submit(function (e) {
    e.preventDefault();
    if(validate()==false) {
        return false;
    }
    document.getElementById("course_button").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#course_form").trigger('reset');
            alert("Course has been added successfully. Visit Dashboard to add students and TAs in it...")
            location.reload();
        },
        error: function (response) {
            alert(response["responseJSON"]["error"])
            document.getElementById("course_button").disabled = false;
        }
    })
})

function validate(){
    if(document.getElementById("course").value==""){
        alert("Course Name must not be empty")
        return false;
    }
}