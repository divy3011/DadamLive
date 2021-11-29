$("#form").submit(function (e) {
    e.preventDefault();
    if(validate()==false) {
        return false;
    }
    document.getElementById("login_button").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#form").trigger('reset');
            alert("A verification link has been sent to your email. Kindly, Check your inbox and click on the link to proceed.")
            location.reload();
        },
        error: function (response) {
            alert(response["responseJSON"]["error"])
            document.getElementById("login_button").disabled = false;
        }
    })
})

function validate(){
    if(document.getElementById("useremail").value==""){
        alert("Roll Number or Email must not be empty")
        return false;
    }
}