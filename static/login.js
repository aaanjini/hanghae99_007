function to_main() {
    window.location.href = "/"
}

function sign_in() {
    let username = $("#id").val();
    let password = $("#pw").val();

    if (username == "") {
        $(".id_box").addClass("error");
        $("#id").focus();
        return;
    } else {
        $(".id_box").removeClass("error");
    }

    if (password == "") {
        $(".pw_box").addClass("error");
        $("#pw").focus();
        return;
    } else {
        $(".pw_box").removeClass("error");
    }
    $.ajax({
        type: "POST",
        url: "/sign_in",
        data: {
            username_give: username,
            password_give: password
        },
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token'], {path: '/'});
                window.location.replace("/")
            } else {
                alert(response['msg'])
            }
        }
    });
}