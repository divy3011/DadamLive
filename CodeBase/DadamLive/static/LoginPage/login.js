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
            alert("Login Successful. Redirecting to Dashboard...")
            location.reload();
        },
        error: function (response) {
            document.getElementById("password").value=""
            alert(response["responseJSON"]["error"])
            // console.log(response)
            // document.getElementById("error").innerHTML=response["responseJSON"]["error"];
            // $('#error').fadeIn();
            // $('#error').delay(2000).fadeOut(1500);
            document.getElementById("login_button").disabled = false;
        }
    })
})

function validate(){
    if(document.getElementById("useremail").value==""){
        alert("Username or Email must not be empty")
        return false;
    }
    if(document.getElementById("password").value==""){
        alert("Password must not be empty")
        return false;
    }
}