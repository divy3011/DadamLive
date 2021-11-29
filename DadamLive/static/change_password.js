$("#form").submit(function (e) {
    e.preventDefault();
    if(validate()==false) {
        return false;
    }
    document.getElementById("button_form").disabled = true;
    var serializedData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: "",
        data: serializedData,
        success: function (response) {
            $("#form").trigger('reset');
            alert("Your password has been changed successfully. Now you will be redirected to login page, there login again with new password to view dashboard.")
            location.reload();
        },
        error: function (response) {
            alert(response["responseJSON"]["error"])
            document.getElementById("button_form").disabled = false;
        }
    })
})

function validate() {
    password1 = document.getElementById('password1').value
    password2 = document.getElementById('password2').value
    if(password1=="" || password2==""){
        document.getElementById("myerror").innerHTML="Password must not be empty."
        fader('#myerror')
        return false;
    }
    if (password1 != password2) {
        document.getElementById("myerror").innerHTML = "Both the passwords are diferent";
        fader('#myerror')
        return false;
    } else {
        var val = passwordchecker(password1)
        if (!val) {
            document.getElementById("myerror").innerHTML = "Password must have atleast 8 characters with digits, letters and special characters";
            fader('#myerror')
            return false
        }
        return true
    }
}

function passwordchecker(str) {
    if ((str.match(/[a-z]/g) || str.match(/[A-Z]/g)) && str.match(
            /[0-9]/g) && str.match(
            /[^a-zA-Z\d]/g) && str.length >= 8)
        return true;
    return false;
}

function fader(ID){
    $(ID).fadeIn()
    $(ID).delay(4000).fadeOut(4000)
}
